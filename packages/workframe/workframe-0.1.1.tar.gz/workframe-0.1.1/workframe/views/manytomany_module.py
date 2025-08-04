"""ManyToManyModule class for managing many-to-many relationships."""

from typing import Optional, Dict, Any
from flask import Blueprint, request, redirect, url_for, render_template, jsonify, flash
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from ..models.table import Table
from ..models.field import Field
from .list import ListView
from .detail import DetailView
from .module import Module


class ManyToManyModule:
    """
    ManyToManyModule class for handling many-to-many relationships.
    
    Creates and manages a junction table between two entities (e.g., users and groups)
    with a complete assignment management interface.
    
    Provides a complete assignment CRUD interface with mobile-first design.
    """
    
    def __init__(self, left_module: Module, right_module: Module, 
                 junction_table_name: Optional[str] = None,
                 name: Optional[str] = None, admin_required: bool = False):
        """
        Initialize ManyToManyModule.
        
        Args:
            left_module: Module instance for the left table (e.g., users)
            right_module: Module instance for the right table (e.g., groups)
            junction_table_name: Optional custom junction table name
            name: Optional module name (defaults to junction table name)
            admin_required: If True, restrict all operations to admin users only
        """
        self.left_module = left_module
        self.right_module = right_module
        self.left_table = left_module.table
        self.right_table = right_module.table
        
        # Generate junction table name if not provided
        if junction_table_name is None:
            # Sort table names alphabetically for consistent naming
            table_names = sorted([self.left_table.name, self.right_table.name])
            junction_table_name = f"{table_names[0]}_{table_names[1]}"
        
        self.junction_table_name = junction_table_name
        self.name = name or junction_table_name
        self.admin_required = admin_required
        
        # Create junction table
        self.junction_table = self._create_junction_table()
        
        self.blueprint = self._create_blueprint()
    
    def _create_junction_table(self) -> Table:
        """
        Create the junction table for the many-to-many relationship.
        
        Returns:
            Table instance for the junction table
        """
        # Generate foreign key field names
        left_fk_name = f"{self.left_table.name}_id"
        right_fk_name = f"{self.right_table.name}_id"
        
        # Create field definitions for junction table
        junction_fields = [
            Field(left_fk_name, 
                  lookup=self.left_table.name, 
                  display='name' if hasattr(self.left_table, 'name') else 'id',
                  required=True),
            Field(right_fk_name, 
                  lookup=self.right_table.name, 
                  display='name' if hasattr(self.right_table, 'name') else 'id',
                  required=True)
        ]
        
        # Create junction table
        junction_table = Table(self.junction_table_name, junction_fields)
        
        return junction_table
    
    def _create_junction_model(self, db):
        """
        Create the SQLAlchemy model for the junction table with proper constraints.
        
        Args:
            db: SQLAlchemy database instance
        """
        if self.junction_table.model:
            return  # Already created
        
        # Set database and create base model
        self.junction_table.db = db
        self.junction_table._create_model()
        
        # Add unique constraint to prevent duplicate assignments
        left_fk_name = f"{self.left_table.name}_id"
        right_fk_name = f"{self.right_table.name}_id"
        
        # Add unique constraint to the table
        constraint_name = f"uq_{self.junction_table_name}_{left_fk_name}_{right_fk_name}"
        unique_constraint = UniqueConstraint(
            left_fk_name, right_fk_name, 
            name=constraint_name
        )
        
        # Add the constraint to the table
        if hasattr(self.junction_table.model.__table__, 'append_constraint'):
            self.junction_table.model.__table__.append_constraint(unique_constraint)
    
    def _create_blueprint(self) -> Blueprint:
        """Create Flask blueprint with many-to-many assignment routes."""
        bp = Blueprint(self.name, __name__)
        
        # Import login decorators
        from flask_login import login_required
        from ..views.auth import admin_required as admin_required_decorator
        
        # Choose appropriate decorator based on admin_required setting
        if self.admin_required:
            auth_decorator = admin_required_decorator
        else:
            auth_decorator = login_required
        
        # Main assignment management view
        @bp.route('/', methods=['GET'])
        @auth_decorator
        def assignment_view():
            """Display assignment management interface."""
            try:
                # Get all assignments (junction table records)
                assignments_listview = ListView(self.junction_table)
                assignments_data = assignments_listview.get_data()
                
                # Get available left entities (e.g., users)
                left_listview = ListView(self.left_table)
                left_data = left_listview.get_data()
                
                # Get available right entities (e.g., groups)
                right_listview = ListView(self.right_table)
                right_data = right_listview.get_data()
                
                return render_template('crud/manytomany.html',
                                     left_table=self.left_table,
                                     right_table=self.right_table,
                                     junction_table=self.junction_table,
                                     assignments_data=assignments_data,
                                     left_data=left_data,
                                     right_data=right_data,
                                     module_name=self.name,
                                     left_module_name=self.left_module.name,
                                     right_module_name=self.right_module.name)
                                     
            except Exception as e:
                return self._error_response(f"Error loading assignment view: {str(e)}", 500)
        
        # Create new assignment
        @bp.route('/assign', methods=['POST'])
        @auth_decorator
        def create_assignment():
            """Create new assignment between entities."""
            try:
                left_fk_name = f"{self.left_table.name}_id"
                right_fk_name = f"{self.right_table.name}_id"
                
                left_id = request.form.get(left_fk_name)
                right_id = request.form.get(right_fk_name)
                
                if not left_id or not right_id:
                    flash(f'Please select both {self.left_table.name.title()} and {self.right_table.name.title()}', 'error')
                    return redirect(url_for(f'{self.name}.assignment_view'))
                
                # Check if assignment already exists
                existing = self.junction_table.model.query.filter_by(
                    **{left_fk_name: int(left_id), right_fk_name: int(right_id)}
                ).first()
                
                if existing:
                    flash('Assignment already exists', 'warning')
                    return redirect(url_for(f'{self.name}.assignment_view'))
                
                # Create new assignment
                assignment_data = {
                    left_fk_name: int(left_id),
                    right_fk_name: int(right_id)
                }
                
                assignment = self.junction_table.create_record(assignment_data)
                
                flash(f'Assignment created successfully!', 'success')
                return redirect(url_for(f'{self.name}.assignment_view'))
                
            except Exception as e:
                flash(f'Error creating assignment: {str(e)}', 'error')
                return redirect(url_for(f'{self.name}.assignment_view'))
        
        # Delete assignment
        @bp.route('/assignment/<int:assignment_id>/delete', methods=['POST'])
        @auth_decorator
        def delete_assignment(assignment_id):
            """Delete assignment."""
            try:
                assignment = self.junction_table.model.query.get(assignment_id)
                if not assignment:
                    flash('Assignment not found', 'error')
                    return redirect(url_for(f'{self.name}.assignment_view'))
                
                self.junction_table.delete_record(assignment_id)
                flash('Assignment removed successfully!', 'success')
                
                return redirect(url_for(f'{self.name}.assignment_view'))
                
            except Exception as e:
                flash(f'Error removing assignment: {str(e)}', 'error')
                return redirect(url_for(f'{self.name}.assignment_view'))
        
        # Bulk delete assignments
        @bp.route('/bulk-delete', methods=['POST'])
        @auth_decorator
        def bulk_delete():
            """Delete multiple assignments."""
            try:
                ids = request.form.getlist('ids')
                if not ids:
                    flash("No assignments selected for deletion", 'error')
                    return redirect(url_for(f'{self.name}.assignment_view'))
                
                # Convert to integers and validate
                try:
                    assignment_ids = [int(id_str) for id_str in ids]
                except ValueError:
                    flash("Invalid assignment IDs", 'error')
                    return redirect(url_for(f'{self.name}.assignment_view'))
                
                if not self.junction_table.model:
                    flash("Junction table model not available", 'error')
                    return redirect(url_for(f'{self.name}.assignment_view'))
                
                # Get the database instance
                from flask import current_app
                db = current_app.extensions['sqlalchemy']
                
                # Delete assignments
                deleted_count = 0
                for assignment_id in assignment_ids:
                    assignment = self.junction_table.model.query.get(assignment_id)
                    if assignment:
                        db.session.delete(assignment)
                        deleted_count += 1
                
                db.session.commit()
                
                flash(f'Successfully removed {deleted_count} assignment(s)', 'success')
                return redirect(url_for(f'{self.name}.assignment_view'))
                
            except Exception as e:
                flash(f'Error removing assignments: {str(e)}', 'error')
                return redirect(url_for(f'{self.name}.assignment_view'))
        
        # CSV Export
        @bp.route('/export.csv')
        @auth_decorator
        def export_csv():
            """Export assignment data as CSV."""
            try:
                listview = ListView(self.junction_table)
                return listview.export_csv()
            except Exception as e:
                return self._error_response(f"Error exporting data: {str(e)}", 500)
        
        # Individual entity management routes (delegated to respective modules)
        
        # Left entity routes
        @bp.route(f'/{self.left_table.name}/new', methods=['GET', 'POST'])
        @auth_decorator
        def create_left():
            """Create new left entity."""
            try:
                detailview = DetailView(self.left_table)
                detailview.set_mode('create')
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        return redirect(url_for(f'{self.name}.assignment_view'))
                
                return detailview.render(back_url=url_for(f'{self.name}.assignment_view'))
                
            except Exception as e:
                return self._error_response(f"Error creating {self.left_table.name}: {str(e)}", 500)
        
        # Right entity routes
        @bp.route(f'/{self.right_table.name}/new', methods=['GET', 'POST'])
        @auth_decorator
        def create_right():
            """Create new right entity."""
            try:
                detailview = DetailView(self.right_table)
                detailview.set_mode('create')
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        return redirect(url_for(f'{self.name}.assignment_view'))
                
                return detailview.render(back_url=url_for(f'{self.name}.assignment_view'))
                
            except Exception as e:
                return self._error_response(f"Error creating {self.right_table.name}: {str(e)}", 500)
        
        return bp
    
    def _error_response(self, message: str, status_code: int = 500) -> str:
        """
        Generate mobile-friendly error response using proper Bootstrap template.
        
        Args:
            message: Error message to display
            status_code: HTTP status code
            
        Returns:
            HTML error page
        """
        from flask import render_template, url_for
        
        error_type = {
            400: 'Bad Request',
            404: 'Not Found', 
            500: 'Server Error'
        }.get(status_code, 'Error')
        
        icon = {
            400: 'bi-exclamation-triangle',
            404: 'bi-search',
            500: 'bi-exclamation-octagon'
        }.get(status_code, 'bi-exclamation-circle')
        
        error_color = 'warning' if status_code == 404 else 'danger'
        
        try:
            return render_template('errors/error.html',
                                 error_type=error_type,
                                 error_message=message,
                                 error_icon=icon,
                                 error_color=error_color,
                                 status_code=status_code,
                                 back_url=url_for(f'{self.name}.assignment_view')), status_code
        except:
            # Fallback error template
            from flask import render_template_string
            template = f'''
            {{% extends "base.html" %}}
            
            {{% block title %}}{error_type} - WorkFrame{{% endblock %}}
            
            {{% block content %}}
            <div class="container-fluid">
                <div class="row justify-content-center min-vh-50 align-items-center">
                    <div class="col-12 col-md-8 col-lg-6">
                        <div class="card border-0 bg-{error_color} bg-opacity-10">
                            <div class="card-body text-center py-5">
                                <i class="bi {icon} display-4 text-{error_color} mb-3"></i>
                                <h2 class="h4 mb-3">{error_type}</h2>
                                <p class="mb-4">{message}</p>
                                <div class="d-flex justify-content-center gap-2 flex-wrap">
                                    <button onclick="history.back()" class="btn btn-outline-secondary">
                                        <i class="bi bi-arrow-left me-1"></i>Go Back
                                    </button>
                                    <a href="{url_for(f'{self.name}.assignment_view')}" class="btn btn-primary">
                                        <i class="bi bi-list me-1"></i>View Assignments
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {{% endblock %}}
            '''
            
            return render_template_string(template), status_code
    
    def get_routes_info(self) -> dict:
        """
        Get information about the routes this module provides.
        
        Returns:
            Dictionary with route information
        """
        return {
            'assignment_view': f'/{self.name}/',
            'create_assignment': f'/{self.name}/assign',
            'delete_assignment': f'/{self.name}/assignment/<id>/delete',
            'bulk_delete': f'/{self.name}/bulk-delete',
            'export_csv': f'/{self.name}/export.csv',
            'create_left': f'/{self.name}/{self.left_table.name}/new',
            'create_right': f'/{self.name}/{self.right_table.name}/new'
        }
    
    def __repr__(self):
        return f"<ManyToManyModule {self.name} ({self.left_table.name} <-> {self.right_table.name})>"
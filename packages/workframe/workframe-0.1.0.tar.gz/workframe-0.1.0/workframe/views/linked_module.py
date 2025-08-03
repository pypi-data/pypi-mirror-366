"""LinkedTableModule class for many-to-one relationship views."""

from typing import Optional
from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from ..models.table import Table
from .list import ListView
from .detail import DetailView
from .module import Module


class LinkedTableModule:
    """
    LinkedTableModule class for handling many-to-one relationships.
    
    Shows two tables on one page: master table (e.g., companies) and 
    detail table (e.g., contacts) that filters based on master selection.
    
    Provides a complete linked CRUD interface with mobile-first design,
    including master-detail filtering and contextual operations.
    """
    
    def __init__(self, detail_table: Table, master_module: Module, 
                 name: Optional[str] = None, admin_required: bool = False):
        """
        Initialize LinkedTableModule.
        
        Args:
            detail_table: Table instance for the detail table (e.g., contacts)
            master_module: Module instance for the master table (e.g., companies)
            name: Optional module name (defaults to detail table name)
            admin_required: If True, restrict all operations to admin users only
        """
        self.detail_table = detail_table
        self.master_module = master_module
        self.master_table = master_module.table
        self.name = name or detail_table.name
        self.admin_required = admin_required
        
        # Detect the foreign key field
        self.foreign_key_field = self._detect_foreign_key()
        if not self.foreign_key_field:
            raise ValueError(f"No foreign key found from {detail_table.name} to {self.master_table.name}")
        
        self.blueprint = self._create_blueprint()
    
    def _detect_foreign_key(self) -> Optional[str]:
        """
        Detect the foreign key field that links detail table to master table.
        
        Returns:
            Field name that references the master table, or None if not found
        """
        # Look for field named {master_table}_id
        expected_fk_name = f"{self.master_table.name}_id"
        if self.detail_table.get_field(expected_fk_name):
            return expected_fk_name
        
        # Look for Field objects with lookup to master table
        for field in self.detail_table.fields:
            if hasattr(field, 'lookup') and field.lookup == self.master_table.name:
                return field.name
        
        return None
    
    def _create_blueprint(self) -> Blueprint:
        """Create Flask blueprint with linked table routes."""
        bp = Blueprint(self.name, __name__)
        
        # Import login decorators
        from flask_login import login_required
        from ..views.auth import admin_required as admin_required_decorator
        
        # Choose appropriate decorator based on admin_required setting
        if self.admin_required:
            auth_decorator = admin_required_decorator
        else:
            auth_decorator = login_required
        
        # Main linked view (master + detail tables)
        @bp.route('/', methods=['GET'])
        @auth_decorator
        def linked_view():
            """Display linked tables: master on top, detail on bottom."""
            try:
                # Get master table data
                master_listview = ListView(self.master_table)
                master_data = master_listview.get_data()
                
                # Get detail table data (unfiltered initially)
                detail_listview = ListView(self.detail_table)
                detail_data = detail_listview.get_data()
                
                return render_template('crud/linked.html',
                                     master_table=self.master_table,
                                     detail_table=self.detail_table,
                                     master_data=master_data,
                                     detail_data=detail_data,
                                     foreign_key_field=self.foreign_key_field,
                                     module_name=self.name,
                                     master_module_name=self.master_module.name)
                                     
            except Exception as e:
                return self._error_response(f"Error loading linked view: {str(e)}", 500)
        
        # AJAX endpoint for filtering detail table
        @bp.route('/filter_detail/<int:master_id>')
        @auth_decorator
        def filter_detail(master_id):
            """Filter detail table by master record ID."""
            try:
                # Create filtered query for detail table
                detail_listview = ListView(self.detail_table)
                
                # Add filter for the foreign key
                filters = {self.foreign_key_field: master_id}
                filtered_data = detail_listview.get_data(filters=filters)
                
                # Get master record name for display
                master_record = self.master_table.model.query.get(master_id)
                master_name = getattr(master_record, 'name', f'ID {master_id}') if master_record else f'ID {master_id}'
                
                return jsonify({
                    'success': True,
                    'data': filtered_data,
                    'master_name': master_name,
                    'master_id': master_id
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
        
        # Detail table CRUD routes (prefixed to avoid conflicts)
        
        # Detail list view (standalone)
        @bp.route('/list')
        @auth_decorator
        def detail_list():
            """Standalone list view for detail table."""
            try:
                listview = ListView(self.detail_table)
                return listview.render()
            except Exception as e:
                return self._error_response(f"Error loading detail list: {str(e)}", 500)
        
        # Detail CSV Export
        @bp.route('/export.csv')
        @auth_decorator
        def export_csv():
            """Export detail table data as CSV."""
            try:
                listview = ListView(self.detail_table)
                return listview.export_csv()
            except Exception as e:
                return self._error_response(f"Error exporting data: {str(e)}", 500)
        
        # Detail bulk delete
        @bp.route('/bulk-delete', methods=['POST'])
        @auth_decorator
        def bulk_delete():
            """Delete multiple detail records."""
            try:
                ids = request.form.getlist('ids')
                if not ids:
                    return self._error_response("No items selected for deletion", 400)
                
                # Convert to integers and validate
                try:
                    record_ids = [int(id_str) for id_str in ids]
                except ValueError:
                    return self._error_response("Invalid record IDs", 400)
                
                if not self.detail_table.model:
                    return self._error_response("Table model not available", 500)
                
                # Get the database instance
                from flask import current_app
                db = current_app.extensions['sqlalchemy']
                
                # Delete records
                deleted_count = 0
                for record_id in record_ids:
                    record = self.detail_table.model.query.get(record_id)
                    if record:
                        db.session.delete(record)
                        deleted_count += 1
                
                db.session.commit()
                
                # Flash success message
                from flask import flash
                flash(f'Successfully deleted {deleted_count} record(s)', 'success')
                
                return redirect(url_for(f'{self.name}.linked_view'))
                
            except Exception as e:
                return self._error_response(f"Error deleting records: {str(e)}", 500)
        
        # Detail create view
        @bp.route('/new', methods=['GET', 'POST'])
        @auth_decorator
        def create_detail():
            """Create new detail record."""
            try:
                detailview = DetailView(self.detail_table)
                detailview.set_mode('create')
                
                # Pre-fill foreign key if master_id provided
                master_id = request.args.get('master_id')
                if master_id and request.method == 'GET':
                    # Set default value for foreign key field
                    detailview.set_field_default(self.foreign_key_field, master_id)
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        # Redirect back to linked view
                        return redirect(url_for(f'{self.name}.linked_view'))
                    # If there are validation errors, render form again with errors
                
                # Render with custom back URL to linked view
                return detailview.render(back_url=url_for(f'{self.name}.linked_view'))
                
            except Exception as e:
                return self._error_response(f"Error creating record: {str(e)}", 500)
        
        # Detail view
        @bp.route('/<int:record_id>/')
        @auth_decorator
        def detail_view(record_id):
            """Display detail record."""
            try:
                detailview = DetailView(self.detail_table, record_id)
                detailview.set_mode('view')
                return detailview.render(back_url=url_for(f'{self.name}.linked_view'))
                
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error loading record: {str(e)}", 500)
        
        # Detail edit view
        @bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
        @auth_decorator
        def edit_detail(record_id):
            """Edit detail record."""
            try:
                detailview = DetailView(self.detail_table, record_id)
                detailview.set_mode('edit')
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        # Redirect back to linked view
                        return redirect(url_for(f'{self.name}.linked_view'))
                    # If there are validation errors, render form again with errors
                
                # Render with custom back URL to linked view
                return detailview.render(back_url=url_for(f'{self.name}.linked_view'))
                
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error editing record: {str(e)}", 500)
        
        # Detail delete action
        @bp.route('/<int:record_id>/delete', methods=['POST'])
        @auth_decorator
        def delete_detail(record_id):
            """Delete detail record."""
            try:
                detailview = DetailView(self.detail_table, record_id)
                success, error = detailview.handle_delete()
                
                if success:
                    # Redirect back to linked view
                    return redirect(url_for(f'{self.name}.linked_view'))
                else:
                    return self._error_response(error or "Failed to delete record", 400)
                    
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error deleting record: {str(e)}", 500)
        
        # Master table routes (delegated to master module)
        
        # Master create view
        @bp.route('/master/new', methods=['GET', 'POST'])
        @auth_decorator
        def create_master():
            """Create new master record."""
            try:
                detailview = DetailView(self.master_table)
                detailview.set_mode('create')
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        # Redirect back to linked view
                        return redirect(url_for(f'{self.name}.linked_view'))
                    # If there are validation errors, render form again with errors
                
                # Render with custom back URL to linked view
                return detailview.render(back_url=url_for(f'{self.name}.linked_view'))
                
            except Exception as e:
                return self._error_response(f"Error creating master record: {str(e)}", 500)
        
        # Master edit view
        @bp.route('/master/<int:record_id>/edit', methods=['GET', 'POST'])
        @auth_decorator
        def edit_master(record_id):
            """Edit master record."""
            try:
                detailview = DetailView(self.master_table, record_id)
                detailview.set_mode('edit')
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        # Redirect back to linked view
                        return redirect(url_for(f'{self.name}.linked_view'))
                    # If there are validation errors, render form again with errors
                
                # Render with custom back URL to linked view
                return detailview.render(back_url=url_for(f'{self.name}.linked_view'))
                
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error editing master record: {str(e)}", 500)
        
        # Master delete action
        @bp.route('/master/<int:record_id>/delete', methods=['POST'])
        @auth_decorator
        def delete_master(record_id):
            """Delete master record."""
            try:
                detailview = DetailView(self.master_table, record_id)
                success, error = detailview.handle_delete()
                
                if success:
                    # Redirect back to linked view
                    return redirect(url_for(f'{self.name}.linked_view'))
                else:
                    return self._error_response(error or "Failed to delete record", 400)
                    
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error deleting master record: {str(e)}", 500)
        
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
                                 back_url=url_for(f'{self.name}.linked_view')), status_code
        except:
            # Fallback if error template doesn't exist
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
                                    <a href="{url_for(f'{self.name}.linked_view')}" class="btn btn-primary">
                                        <i class="bi bi-list me-1"></i>View Linked Tables
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <style>
            .min-vh-50 {{
                min-height: 50vh;
            }}
            
            @media (max-width: 576px) {{
                .card-body {{
                    padding: 2rem 1.5rem !important;
                }}
                
                .d-flex.flex-wrap .btn {{
                    margin-bottom: 0.5rem;
                }}
            }}
            </style>
            {{% endblock %}}
            '''
            
            from flask import render_template_string
            return render_template_string(template), status_code
    
    def get_routes_info(self) -> dict:
        """
        Get information about the routes this module provides.
        
        Returns:
            Dictionary with route information
        """
        return {
            'linked_view': f'/{self.name}/',
            'filter_detail': f'/{self.name}/filter_detail/<master_id>',
            'detail_list': f'/{self.name}/list',
            'detail_create': f'/{self.name}/new',
            'detail_view': f'/{self.name}/<id>/',
            'detail_edit': f'/{self.name}/<id>/edit',
            'detail_delete': f'/{self.name}/<id>/delete',
            'master_create': f'/{self.name}/master/new',
            'master_edit': f'/{self.name}/master/<id>/edit',
            'master_delete': f'/{self.name}/master/<id>/delete',
            'export_csv': f'/{self.name}/export.csv'
        }
    
    def __repr__(self):
        return f"<LinkedTableModule {self.name} ({self.detail_table.name} -> {self.master_table.name})>"
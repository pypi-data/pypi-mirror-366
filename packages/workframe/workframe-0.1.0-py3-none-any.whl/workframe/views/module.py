"""Module class for bundling CRUD views together."""

from typing import Optional
from flask import Blueprint, request, redirect, url_for, render_template_string
from ..models.table import Table
from .list import ListView
from .detail import DetailView


class Module:
    """
    Module class that bundles CRUD views together into a Flask blueprint.
    
    Provides a complete CRUD interface for a table with mobile-first design,
    including list, detail, create, edit, and delete functionality.
    """
    
    def __init__(self, table: Table, name: Optional[str] = None, admin_required: bool = False):
        """
        Initialize Module.
        
        Args:
            table: Table instance to create CRUD interface for
            name: Optional module name (defaults to table name)
            admin_required: If True, restrict all operations to admin users only
        """
        self.table = table
        self.name = name or table.name
        self.admin_required = admin_required
        self.blueprint = self._create_blueprint()
    
    def _create_blueprint(self) -> Blueprint:
        """Create Flask blueprint with CRUD routes."""
        bp = Blueprint(self.name, __name__)
        
        # Import login decorators
        from flask_login import login_required
        from ..views.auth import admin_required as admin_required_decorator
        
        # Choose appropriate decorator based on admin_required setting
        if self.admin_required:
            auth_decorator = admin_required_decorator
        else:
            auth_decorator = login_required
        
        # List view
        @bp.route('/', methods=['GET', 'POST'])
        @auth_decorator
        def list_view():
            """Display paginated list of records."""
            try:
                # Handle manual migration request
                if request.method == 'POST' and request.args.get('auto_migrate'):
                    error_msg = request.form.get('error_msg', '')
                    if self._attempt_auto_migration(error_msg):
                        from flask import flash
                        flash('Database schema was automatically updated!', 'success')
                        return redirect(url_for(f'{self.name}.list_view'))
                    else:
                        from flask import flash
                        flash('Auto-migration failed. Please try manual migration.', 'error')
                
                listview = ListView(self.table)
                return listview.render()
            except Exception as e:
                error_msg = str(e)
                if "no such column" in error_msg.lower() or "OperationalError" in error_msg:
                    return self._schema_migration_error(error_msg)
                return self._error_response(f"Error loading list: {error_msg}", 500)
        
        # CSV Export
        @bp.route('/export.csv')
        @auth_decorator
        def export_csv():
            """Export list data as CSV."""
            try:
                listview = ListView(self.table)
                return listview.export_csv()
            except Exception as e:
                return self._error_response(f"Error exporting data: {str(e)}", 500)
        
        # Bulk Delete
        @bp.route('/bulk-delete', methods=['POST'])
        @auth_decorator
        def bulk_delete():
            """Delete multiple records."""
            try:
                ids = request.form.getlist('ids')
                if not ids:
                    return self._error_response("No items selected for deletion", 400)
                
                # Convert to integers and validate
                try:
                    record_ids = [int(id_str) for id_str in ids]
                except ValueError:
                    return self._error_response("Invalid record IDs", 400)
                
                if not self.table.model:
                    return self._error_response("Table model not available", 500)
                
                # Get the database instance
                from flask import current_app
                db = current_app.extensions['sqlalchemy']
                
                # Delete records
                deleted_count = 0
                for record_id in record_ids:
                    record = self.table.model.query.get(record_id)
                    if record:
                        db.session.delete(record)
                        deleted_count += 1
                
                db.session.commit()
                
                # Flash success message
                from flask import flash
                flash(f'Successfully deleted {deleted_count} record(s)', 'success')
                
                return redirect(url_for(f'{self.name}.list_view'))
                
            except Exception as e:
                return self._error_response(f"Error deleting records: {str(e)}", 500)
        
        # Create view
        @bp.route('/new', methods=['GET', 'POST'])
        @auth_decorator
        def create_view():
            """Create new record."""
            try:
                detailview = DetailView(self.table)
                detailview.set_mode('create')
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        # Redirect to the new record's detail view
                        return redirect(url_for(f'{self.name}.detail_view', 
                                              record_id=detailview.record_id))
                    # If there are validation errors, render form again with errors
                    # (the errors will be shown in the form template)
                
                return detailview.render()
                
            except Exception as e:
                return self._error_response(f"Error creating record: {str(e)}", 500)
        
        # Detail view
        @bp.route('/<int:record_id>/')
        @auth_decorator
        def detail_view(record_id):
            """Display record details."""
            try:
                detailview = DetailView(self.table, record_id)
                detailview.set_mode('view')
                return detailview.render()
                
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error loading record: {str(e)}", 500)
        
        # Edit view
        @bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
        @auth_decorator
        def edit_view(record_id):
            """Edit existing record."""
            try:
                detailview = DetailView(self.table, record_id)
                detailview.set_mode('edit')
                
                if request.method == 'POST':
                    success, error = detailview.handle_form_submission()
                    if success:
                        # Redirect to detail view
                        return redirect(url_for(f'{self.name}.detail_view', 
                                              record_id=record_id))
                    # If there are validation errors, render form again with errors
                    # (the errors will be shown in the form template)
                
                return detailview.render()
                
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error editing record: {str(e)}", 500)
        
        # Delete action
        @bp.route('/<int:record_id>/delete', methods=['POST'])
        @auth_decorator
        def delete_view(record_id):
            """Delete record."""
            try:
                detailview = DetailView(self.table, record_id)
                success, error = detailview.handle_delete()
                
                if success:
                    # Redirect to list view
                    return redirect(url_for(f'{self.name}.list_view'))
                else:
                    return self._error_response(error or "Failed to delete record", 400)
                    
            except ValueError as e:
                return self._error_response(str(e), 404)
            except Exception as e:
                return self._error_response(f"Error deleting record: {str(e)}", 500)
        
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
                                 back_url=url_for(f'{self.name}.list_view')), status_code
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
                                    <a href="{url_for(f'{self.name}.list_view')}" class="btn btn-primary">
                                        <i class="bi bi-list me-1"></i>View All {self.table.name.title()}
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
            
            return render_template_string(template), status_code
    
    def _schema_migration_error(self, error_msg: str) -> str:
        """
        Generate schema migration error response with helpful instructions.
        
        Args:
            error_msg: Original database error message
            
        Returns:
            HTML error page with migration instructions
        """
        # First, try to auto-migrate the schema
        if self._attempt_auto_migration(error_msg):
            from flask import flash
            flash('Database schema was automatically updated to match your field definitions.', 'success')
            return redirect(url_for(f'{self.name}.list_view'))
        
        # If auto-migration fails, show the error page
        template = '''
        {% extends "base.html" %}
        
        {% block title %}Database Schema Update Required - WorkFrame{% endblock %}
        
        {% block content %}
        <div class="container-fluid">
            <div class="row justify-content-center min-vh-50 align-items-center">
                <div class="col-12 col-md-10 col-lg-8">
                    <div class="card border-0 bg-warning bg-opacity-10">
                        <div class="card-body py-5">
                            <div class="text-center mb-4">
                                <i class="bi bi-database-exclamation display-4 text-warning mb-3"></i>
                                <h2 class="h4 mb-3">Database Schema Update Required</h2>
                                <p class="lead">The database schema needs to be updated to match your current field definitions.</p>
                            </div>
                            
                            <div class="alert alert-warning">
                                <h6><i class="bi bi-exclamation-triangle me-2"></i>What happened?</h6>
                                <p class="mb-0">You've added or modified fields in your WorkFrame application, but the database still has the old table structure.</p>
                            </div>
                            
                            <div class="alert alert-info">
                                <h6><i class="bi bi-robot me-2"></i>Automatic Update Available:</h6>
                                <p class="mb-2">WorkFrame can automatically update your database schema to match your code definitions.</p>
                                <form method="POST" action="?auto_migrate=1" class="d-inline">
                                    <input type="hidden" name="error_msg" value="''' + error_msg + '''">
                                    <button type="submit" class="btn btn-success me-2">
                                        <i class="bi bi-gear-fill me-1"></i>Auto-Update Schema
                                    </button>
                                </form>
                                <small class="text-muted">Your existing data will be preserved where possible.</small>
                            </div>
                            
                            <div class="alert alert-light">
                                <h6><i class="bi bi-tools me-2"></i>Manual Option (Development):</h6>
                                <ol class="mb-2">
                                    <li>Stop your WorkFrame application</li>
                                    <li>Delete the database file: <code>workframe.db</code></li>
                                    <li>Restart your application - it will recreate the database with the correct schema</li>
                                </ol>
                                <p class="mb-0"><strong>Note:</strong> This will delete all existing data in development.</p>
                            </div>
                            
                            <details class="mt-3">
                                <summary class="text-muted" style="cursor: pointer;">Technical Error Details</summary>
                                <pre class="mt-2 p-2 bg-light rounded"><code>''' + error_msg + '''</code></pre>
                            </details>
                            
                            <div class="text-center mt-4">
                                <a href="/" class="btn btn-outline-primary">
                                    <i class="bi bi-house me-1"></i>Return to Dashboard
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        .min-vh-50 {
            min-height: 50vh;
        }
        
        details summary {
            outline: none;
        }
        
        code {
            background: rgba(0,0,0,0.1);
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
        }
        
        @media (max-width: 576px) {
            .card-body {
                padding: 2rem 1.5rem !important;
            }
        }
        </style>
        {% endblock %}
        '''
        
        return render_template_string(template), 500
    
    def _attempt_auto_migration(self, error_msg: str) -> bool:
        """
        Attempt to automatically migrate the database schema.
        
        Args:
            error_msg: The original database error message
            
        Returns:
            bool: True if migration succeeded, False otherwise
        """
        try:
            # Check if it's a missing column error
            if "no such column" not in error_msg.lower():
                return False
            
            # Get database instance
            from flask import current_app
            db = current_app.extensions['sqlalchemy']
            
            # Parse the missing column name from error message
            import re
            match = re.search(r'no such column: (\w+)\.(\w+)', error_msg, re.IGNORECASE)
            if not match:
                return False
            
            table_name = match.group(1)
            column_name = match.group(2)
            
            # Check if this is our table
            if table_name != self.table.table_name:
                return False
            
            # Find the field definition for this column
            field = self.table.get_field(column_name)
            if not field:
                return False
            
            # Generate the ALTER TABLE statement
            column_type = self._get_sqlite_column_type(field)
            nullable = "NULL" if not field.required else "NOT NULL"
            
            # Build the ALTER TABLE command
            alter_sql = f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {nullable}'
            
            # Add default value if specified
            if field.default is not None and not callable(field.default):
                if isinstance(field.default, str):
                    alter_sql += f" DEFAULT '{field.default}'"
                else:
                    alter_sql += f" DEFAULT {field.default}"
            
            # Execute the migration
            with db.engine.connect() as connection:
                connection.execute(db.text(alter_sql))
                connection.commit()
            
            print(f"[SUCCESS] Auto-migrated: Added column '{column_name}' to table '{table_name}'")
            return True
            
        except Exception as e:
            print(f"[ERROR] Auto-migration failed: {e}")
            return False
    
    def _get_sqlite_column_type(self, field):
        """Get SQLite column type for a field."""
        type_mapping = {
            'text': 'TEXT',
            'email': 'TEXT',
            'phone': 'TEXT',
            'string': 'TEXT',
            'textarea': 'TEXT',
            'number': 'INTEGER',
            'float': 'REAL',
            'currency': 'REAL',
            'boolean': 'INTEGER',
            'date': 'DATE',
            'datetime': 'DATETIME',
        }
        
        # Handle enum fields as text
        if field.enum:
            return 'TEXT'
        
        # Handle lookup fields as foreign keys
        if field.lookup:
            return 'INTEGER'
        
        return type_mapping.get(field.type, 'TEXT')
    
    def get_routes_info(self) -> dict:
        """
        Get information about the routes this module provides.
        
        Returns:
            Dictionary with route information
        """
        return {
            'list': f'/{self.name}/',
            'create': f'/{self.name}/new',
            'detail': f'/{self.name}/<id>/',
            'edit': f'/{self.name}/<id>/edit',
            'delete': f'/{self.name}/<id>/delete'
        }
    
    def __repr__(self):
        return f"<Module {self.name} ({self.table.name} table)>"
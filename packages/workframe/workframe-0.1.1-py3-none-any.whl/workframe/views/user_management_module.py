"""Enhanced User Management Module with integrated group management."""

from typing import Optional
from flask import Blueprint, request, redirect, url_for, render_template, jsonify, flash
from .list import ListView
from .detail import DetailView


class UserManagementModule:
    """
    Enhanced User Management Module that provides user list and detailed
    group management capabilities in the user detail view.
    """
    
    def __init__(self, user_model, group_model, db, name: Optional[str] = None, admin_required: bool = False):
        """
        Initialize UserManagementModule.
        
        Args:
            user_model: User SQLAlchemy model
            group_model: Group SQLAlchemy model  
            db: Database instance
            name: Optional module name (defaults to 'users')
            admin_required: If True, restrict all operations to admin users only
        """
        self.user_model = user_model
        self.group_model = group_model
        self.db = db
        self.name = name or 'users'
        self.admin_required = admin_required
        
        # Create blueprint
        self.blueprint = self._create_blueprint()
    
    def _create_blueprint(self) -> Blueprint:
        """Create Flask blueprint with user list and group management."""
        bp = Blueprint(self.name, __name__)
        
        # Import login decorators
        from flask_login import login_required
        from ..views.auth import admin_required as admin_required_decorator
        
        # Choose appropriate decorator based on admin_required setting
        if self.admin_required:
            auth_decorator = admin_required_decorator
        else:
            auth_decorator = login_required
        
        # User list view
        @bp.route('/')
        @auth_decorator
        def list_view():
            """Display list of users."""
            try:
                # Create a simple listview-like object to work with existing template
                from collections import namedtuple
                from ..models.field import Field
                
                # Get pagination parameters
                page = request.args.get('page', 1, type=int)
                per_page = 20
                
                # Get search query
                search = request.args.get('search', '')
                
                # Build query
                query = self.user_model.query
                if search:
                    query = query.filter(
                        (self.user_model.username.contains(search)) |
                        (self.user_model.email.contains(search)) |
                        (self.user_model.first_name.contains(search)) |
                        (self.user_model.last_name.contains(search))
                    )
                
                # Paginate results
                pagination = query.paginate(
                    page=page, per_page=per_page, error_out=False
                )
                
                # Create a mock listview object for template compatibility
                MockTable = namedtuple('MockTable', ['name'])
                MockListView = namedtuple('MockListView', [
                    'table', 'display_fields', 'search_query', 'format_cell_value', 
                    'get_sort_url', 'get_sort_icon', 'get_page_url'
                ])
                
                mock_table = MockTable(name='users')
                
                display_fields = [
                    Field('username', type='text'),
                    Field('email', type='email'),
                    Field('full_name', type='text'),
                    Field('is_admin', type='boolean'),
                    Field('is_active', type='boolean')
                ]
                
                def format_cell_value(record, field):
                    """Format field values for display"""
                    value = getattr(record, field.name, '')
                    if field.type == 'boolean':
                        return '✓' if value else '✗'
                    return str(value) if value else ''
                
                def get_sort_url(field_name):
                    return f"?sort={field_name}"
                
                def get_sort_icon(field_name):
                    return "bi-arrow-up"
                
                def get_page_url(page_num):
                    args = request.args.to_dict()
                    args['page'] = page_num
                    return '?' + '&'.join(f"{k}={v}" for k, v in args.items())
                
                listview = MockListView(
                    table=mock_table,
                    display_fields=display_fields,
                    search_query=search,
                    format_cell_value=format_cell_value,
                    get_sort_url=get_sort_url,
                    get_sort_icon=get_sort_icon,
                    get_page_url=get_page_url
                )
                
                return render_template('crud/list.html',
                                     listview=listview,
                                     pagination=pagination)
                                     
            except Exception as e:
                return self._error_response(f"Error loading users: {str(e)}", 500)
        
        # Enhanced user detail view with groups
        @bp.route('/<int:record_id>/')
        @auth_decorator
        def user_detail_with_groups(record_id):
            """Display user details with group management."""
            try:
                # Get user record
                user_record = self.user_model.query.get(record_id)
                if not user_record:
                    flash(f'User not found', 'error')
                    return redirect(url_for(f'{self.name}.list_view'))
                
                # Get all available groups
                all_groups = self.group_model.query.filter_by(is_active=True).all()
                
                # Get user's current groups
                user_groups = user_record.groups if hasattr(user_record, 'groups') else []
                
                return render_template('admin/user_detail_with_groups.html',
                                     user=user_record,
                                     user_groups=user_groups,
                                     all_groups=all_groups,
                                     module_name=self.name)
                                     
            except Exception as e:
                return self._error_response(f"Error loading user details: {str(e)}", 500)
        
        # Add user to group
        @bp.route('/<int:user_id>/add-group', methods=['POST'])
        @auth_decorator
        def add_user_to_group(user_id):
            """Add user to a group."""
            try:
                group_id = request.form.get('group_id')
                if not group_id:
                    flash('Please select a group', 'error')
                    return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
                
                # Get user and group
                user = self.user_model.query.get(user_id)
                group = self.group_model.query.get(group_id)
                
                if not user or not group:
                    flash('User or group not found', 'error')
                    return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
                
                # Check if user is already in group
                if group in user.groups:
                    flash(f'User is already in group "{group.name}"', 'warning')
                    return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
                
                # Add user to group
                user.groups.append(group)
                self.db.session.commit()
                
                flash(f'Added user to group "{group.name}"', 'success')
                return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
                
            except Exception as e:
                self.db.session.rollback()
                flash(f'Error adding user to group: {str(e)}', 'error')
                return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
        
        # Remove user from group
        @bp.route('/<int:user_id>/remove-group/<int:group_id>', methods=['POST'])
        @auth_decorator
        def remove_user_from_group(user_id, group_id):
            """Remove user from a group."""
            try:
                # Get user and group
                user = self.user_model.query.get(user_id)
                group = self.group_model.query.get(group_id)
                
                if not user or not group:
                    flash('User or group not found', 'error')
                    return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
                
                # Remove user from group
                if group in user.groups:
                    user.groups.remove(group)
                    self.db.session.commit()
                    
                    flash(f'Removed user from group "{group.name}"', 'success')
                else:
                    flash(f'User is not in group "{group.name}"', 'warning')
                
                return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
                
            except Exception as e:
                self.db.session.rollback()
                flash(f'Error removing user from group: {str(e)}', 'error')
                return redirect(url_for(f'{self.name}.user_detail_with_groups', record_id=user_id))
        
        return bp
    
    def _error_response(self, error_message, status_code=500):
        """Return error response with proper template."""
        return render_template('errors/500.html', 
                             error_message=error_message), status_code
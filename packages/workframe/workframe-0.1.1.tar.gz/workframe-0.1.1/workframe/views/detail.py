"""DetailView class for viewing and editing individual records."""

from typing import Optional, Dict, Any
from flask import request, url_for, render_template_string, render_template, redirect, flash
from ..models.table import Table
from ..models.field import Field
from ..forms.generator import Form


class DetailView:
    """
    DetailView for viewing and editing individual records.
    
    Provides mobile-optimized detail views with edit capabilities
    designed for business applications.
    """
    
    def __init__(self, table: Table, record_id: Optional[int] = None):
        """
        Initialize DetailView.
        
        Args:
            table: Table instance
            record_id: ID of record to display/edit (None for new records)
        """
        self.table = table
        self.record_id = record_id
        self.record = None
        self.mode = 'view'  # 'view', 'edit', or 'create'
        
        # Load record if ID provided
        if self.record_id:
            self.record = self._load_record()
    
    def _load_record(self):
        """Load record from database."""
        if not self.table.model:
            raise ValueError("Table model not available")
        
        record = self.table.model.query.get(self.record_id)
        if not record:
            raise ValueError(f"Record {self.record_id} not found")
        
        return record
    
    def set_mode(self, mode: str):
        """
        Set view mode.
        
        Args:
            mode: 'view', 'edit', or 'create'
        """
        if mode not in ['view', 'edit', 'create']:
            raise ValueError(f"Invalid mode: {mode}")
        
        self.mode = mode
        
        # Initialize field defaults dictionary for create mode
        if mode == 'create' and not hasattr(self, 'field_defaults'):
            self.field_defaults = {}
    
    def set_field_default(self, field_name: str, value: Any):
        """
        Set a default value for a field in create mode.
        
        Args:
            field_name: Name of the field to set default for
            value: Default value to set
        """
        if not hasattr(self, 'field_defaults'):
            self.field_defaults = {}
        
        self.field_defaults[field_name] = value
    
    def get_display_fields(self):
        """Get fields to display in detail view."""
        if self.mode == 'view':
            # Show all non-hidden fields in view mode
            return [f for f in self.table.fields if not f.hidden]
        else:
            # Show form fields in edit/create mode
            return self.table.get_form_fields()
    
    def handle_form_submission(self) -> tuple[bool, Optional[str]]:
        """
        Handle form submission for create/edit.
        
        Returns:
            tuple: (success, error_message)
        """
        if request.method != 'POST':
            return False, None
        
        # Create form and populate from request
        form = Form(self.table, self.mode, self.record)
        
        if not form.populate_from_request():
            return False, "No form data received"
        
        # Validate form
        if not form.validate():
            return False, f"Validation errors: {form.errors}"
        
        try:
            # Get cleaned data
            data = form.get_data_for_save()
            
            if self.mode == 'create':
                # Create new record
                self.record = self.table.create_record(data)
                self.record_id = self.record.id
                flash(f'{self.table.name.title()} created successfully!', 'success')
            
            elif self.mode == 'edit':
                # Update existing record
                self.record = self.table.update_record(self.record_id, data)
                flash(f'{self.table.name.title()} updated successfully!', 'success')
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def handle_delete(self) -> tuple[bool, Optional[str]]:
        """
        Handle record deletion.
        
        Returns:
            tuple: (success, error_message)
        """
        if not self.record_id:
            return False, "No record to delete"
        
        try:
            self.table.delete_record(self.record_id)
            flash(f'{self.table.name.title()} deleted successfully!', 'success')
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_field_value(self, field: Field) -> Any:
        """Get the current value for a field."""
        if not self.record:
            return field.default if field.default else ''
        
        return getattr(self.record, field.name, '')
    
    def format_field_value(self, field: Field) -> str:
        """Format field value for display."""
        value = self.get_field_value(field)
        return field.format_value(value)
    
    def render(self, template_name: str = None, back_url: str = None) -> str:
        """
        Render the detail view.
        
        Args:
            template_name: Optional custom template name
            back_url: Optional custom back URL (overrides default)
            
        Returns:
            Rendered HTML
        """
        if self.mode == 'view':
            template = template_name or 'crud/detail.html'
            # Use custom back_url if provided, otherwise use default
            view_back_url = back_url if back_url else '../'
            return render_template(template, detailview=self, back_url=view_back_url)
        else:
            # Form mode (create/edit)
            template = template_name or 'crud/form.html'
            
            # Create form
            form = Form(self.table, self.mode, self.record)
            
            # Set field defaults for create mode
            if self.mode == 'create' and hasattr(self, 'field_defaults'):
                form.set_defaults(self.field_defaults)
            
            # Populate form data for edit mode
            if self.mode == 'edit' and self.record:
                form.populate_from_record()
            
            # Handle any validation errors from previous submission
            if request.method == 'POST':
                form.populate_from_request()
                form.validate()  # This will populate form.errors
            
            action_text = 'Create' if self.mode == 'create' else 'Update'
            # Use custom back_url if provided, otherwise use default
            if back_url is None:
                back_url = '../' if self.mode == 'create' else '../'
            
            return render_template(template, 
                                 detailview=self,
                                 form=form,
                                 action_text=action_text,
                                 back_url=back_url)
    
    def _render_view_mode(self) -> str:
        """Render record in view mode."""
        if not self.record:
            return '<div class="alert alert-danger">Record not found</div>'
        
        # Build field display
        fields_html = []
        display_fields = self.get_display_fields()
        
        for field in display_fields:
            value = self.format_field_value(field)
            
            if not value and field.type != 'boolean':
                value = '<span class="text-muted">Not set</span>'
            
            fields_html.append(f'''
            <div class="row mb-3">
                <div class="col-sm-4">
                    <strong>{field.name.replace('_', ' ').title()}</strong>
                </div>
                <div class="col-sm-8">
                    {value}
                </div>
            </div>
            ''')
        
        # System fields
        if hasattr(self.record, 'created_at') and self.record.created_at:
            fields_html.append(f'''
            <div class="row mb-3">
                <div class="col-sm-4">
                    <strong>Created</strong>
                </div>
                <div class="col-sm-8">
                    <small class="text-muted">
                        {self.record.created_at.strftime('%B %d, %Y at %I:%M %p')}
                    </small>
                </div>
            </div>
            ''')
        
        if hasattr(self.record, 'updated_at') and self.record.updated_at:
            fields_html.append(f'''
            <div class="row mb-3">
                <div class="col-sm-4">
                    <strong>Last Updated</strong>
                </div>
                <div class="col-sm-8">
                    <small class="text-muted">
                        {self.record.updated_at.strftime('%B %d, %Y at %I:%M %p')}
                    </small>
                </div>
            </div>
            ''')
        
        template = f'''
        <div class="container-fluid">
            <nav aria-label="breadcrumb" class="mb-3">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item">
                        <a href="../">
                            <i class="bi bi-arrow-left me-1"></i>{self.table.name.title()}
                        </a>
                    </li>
                    <li class="breadcrumb-item active">View</li>
                </ol>
            </nav>
            
            <div class="row justify-content-center">
                <div class="col-12 col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="card-title mb-0">
                                    <i class="bi bi-eye me-2"></i>
                                    {self.table.name.title()} Details
                                </h5>
                                <div class="btn-group btn-group-sm">
                                    <a href="edit" class="btn btn-outline-primary">
                                        <i class="bi bi-pencil"></i> Edit
                                    </a>
                                    <button type="button" 
                                            class="btn btn-outline-danger" 
                                            data-confirm="Are you sure you want to delete this {self.table.name}?"
                                            onclick="document.getElementById('deleteForm').submit();">
                                        <i class="bi bi-trash"></i> Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            {''.join(fields_html)}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Hidden delete form -->
            <form id="deleteForm" method="POST" action="delete" style="display: none;">
                <input type="hidden" name="_method" value="DELETE">
            </form>
        </div>
        
        <style>
        /* Mobile optimizations */
        @media (max-width: 576px) {{
            .row.mb-3 {{
                margin-bottom: 1rem !important;
            }}
            
            .col-sm-4 {{
                margin-bottom: 0.25rem;
            }}
            
            .btn-group-sm .btn {{
                padding: 0.375rem 0.75rem;
                font-size: 0.875rem;
            }}
        }}
        
        /* Card spacing */
        .card-body .row:last-child {{
            margin-bottom: 0;
        }}
        </style>
        '''
        
        return template
    
    def _render_form_mode(self) -> str:
        """Render record in form mode (create/edit)."""
        # Create form
        form = Form(self.table, self.mode, self.record)
        
        # Populate form data for edit mode
        if self.mode == 'edit' and self.record:
            form.populate_from_record()
        
        # Handle any validation errors from previous submission
        if request.method == 'POST':
            form.populate_from_request()
            form.validate()  # This will populate form.errors
        
        action_text = 'Create' if self.mode == 'create' else 'Update'
        back_url = '../' if self.mode == 'create' else '../'
        
        # Build breadcrumb
        breadcrumb_items = []
        breadcrumb_items.append(f'''
        <li class="breadcrumb-item">
            <a href="{back_url}">
                <i class="bi bi-arrow-left me-1"></i>{self.table.name.title()}
            </a>
        </li>
        ''')
        
        if self.mode == 'edit':
            breadcrumb_items.append(f'<li class="breadcrumb-item"><a href="../">View</a></li>')
        
        breadcrumb_items.append(f'<li class="breadcrumb-item active">{action_text}</li>')
        
        # Render form fields
        fields_html = []
        for field in form.fields:
            field_html = form.render_field(field)
            fields_html.append(field_html)
        
        template = f'''
        <div class="container-fluid">
            <nav aria-label="breadcrumb" class="mb-3">
                <ol class="breadcrumb">
                    {''.join(breadcrumb_items)}
                </ol>
            </nav>
            
            <div class="row justify-content-center">
                <div class="col-12 col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="bi bi-{'plus-circle' if self.mode == 'create' else 'pencil'} me-2"></i>
                                {action_text} {self.table.name.title()}
                            </h5>
                        </div>
                        <div class="card-body">
                            <form method="POST" data-loading>
                                {''.join(fields_html)}
                                
                                <div class="d-flex gap-2 flex-wrap mt-4">
                                    <button type="submit" class="btn btn-primary flex-fill">
                                        <i class="bi bi-check-lg me-1"></i>{action_text}
                                    </button>
                                    <a href="{back_url}" class="btn btn-outline-secondary flex-fill">
                                        <i class="bi bi-x-lg me-1"></i>Cancel
                                    </a>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        /* Mobile-first form optimizations */
        @media (max-width: 576px) {{
            .form-control, .form-select {{
                font-size: 1.1rem;
                padding: 0.75rem;
            }}
            
            .form-check-input {{
                width: 1.25rem;
                height: 1.25rem;
            }}
            
            .btn {{
                padding: 0.75rem 1.5rem;
                font-size: 1.1rem;
            }}
            
            .card-body {{
                padding: 1.5rem;
            }}
        }}
        
        /* Touch-friendly spacing */
        .mb-3 {{
            margin-bottom: 1.5rem !important;
        }}
        
        /* Focus styles for accessibility */
        .form-control:focus, .form-select:focus {{
            border-color: var(--bs-primary);
            box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
        }}
        </style>
        '''
        
        return template
    
    def get_navigation_links(self) -> Dict[str, str]:
        """Get navigation links for this record."""
        links = {}
        
        if self.mode == 'view':
            links['edit'] = 'edit'
            links['list'] = '../'
        elif self.mode == 'edit':
            links['view'] = '../'
            links['list'] = '../../'
        elif self.mode == 'create':
            links['list'] = '../'
        
        return links
"""Form generation for WorkFrame CRUD operations."""

from typing import Dict, List, Any, Optional
from flask import request, render_template_string
from ..models.field import Field
from ..models.table import Table


class Form:
    """
    Form generator for WorkFrame applications.
    
    Creates mobile-first, responsive forms from field definitions
    with automatic validation and error handling.
    """
    
    def __init__(self, table: Table, action: str = 'create', record=None):
        """
        Initialize form generator.
        
        Args:
            table: Table instance with field definitions
            action: Form action ('create' or 'edit')
            record: Existing record for edit forms
        """
        self.table = table
        self.action = action
        self.record = record
        self.errors = {}
        self.data = {}
        
        # Get form fields (excluding hidden and readonly for create)
        self.fields = self._get_form_fields()
    
    def _get_form_fields(self) -> List[Field]:
        """Get fields that should be included in the form."""
        fields = []
        for field in self.table.fields:
            # Skip hidden fields
            if field.hidden or field.hidden_in_form:
                continue
            
            # For create forms, skip readonly fields
            if self.action == 'create' and field.readonly:
                continue
            
            fields.append(field)
        
        return fields
    
    def populate_from_request(self) -> bool:
        """
        Populate form data from Flask request.
        
        Returns:
            bool: True if form was submitted, False otherwise
        """
        if request.method != 'POST':
            return False
        
        self.data = {}
        
        for field in self.fields:
            if field.type == 'boolean':
                # Checkboxes are only present in POST data if checked
                self.data[field.name] = field.name in request.form
            else:
                value = request.form.get(field.name, '').strip()
                self.data[field.name] = value if value else None
        
        return True
    
    def populate_from_record(self):
        """Populate form data from existing record."""
        if not self.record:
            return
        
        self.data = {}
        for field in self.fields:
            value = getattr(self.record, field.name, None)
            self.data[field.name] = value
    
    def set_defaults(self, defaults: Dict[str, Any]):
        """
        Set default values for form fields.
        
        Args:
            defaults: Dictionary of field_name -> default_value mappings
        """
        if not self.data:
            self.data = {}
        
        for field_name, default_value in defaults.items():
            if field_name not in self.data or not self.data.get(field_name):
                self.data[field_name] = default_value
    
    def validate(self) -> bool:
        """
        Validate form data.
        
        Returns:
            bool: True if valid, False if errors found
        """
        self.errors = {}
        
        for field in self.fields:
            value = self.data.get(field.name)
            is_valid, error_message = field.validate(value)
            
            if not is_valid:
                self.errors[field.name] = error_message
        
        return len(self.errors) == 0
    
    def get_field_value(self, field: Field) -> Any:
        """Get the current value for a field."""
        return self.data.get(field.name, '')
    
    def get_field_error(self, field: Field) -> Optional[str]:
        """Get error message for a field."""
        return self.errors.get(field.name)
    
    def has_errors(self) -> bool:
        """Check if form has any validation errors."""
        return len(self.errors) > 0
    
    def render_field(self, field: Field) -> str:
        """
        Render a single form field as HTML.
        
        Args:
            field: Field to render
            
        Returns:
            HTML string for the field
        """
        value = self.get_field_value(field)
        error = self.get_field_error(field)
        
        # Build field HTML based on type
        if field.type == 'textarea':
            return self._render_textarea(field, value, error)
        elif field.is_enum_field() or field.is_lookup_field():
            return self._render_select(field, value, error)
        elif field.type == 'boolean':
            return self._render_checkbox(field, value, error)
        else:
            return self._render_input(field, value, error)
    
    def _render_input(self, field: Field, value: Any, error: Optional[str]) -> str:
        """Render a standard input field."""
        attrs = field.get_input_attributes()
        
        # Add error class if needed
        if error:
            attrs['class'] += ' is-invalid'
        
        # Set current value
        if value is not None:
            attrs['value'] = str(value)
        
        # Build attributes string
        attr_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items() if v is not False])
        
        template = f'''
        <div class="mb-3">
            <label for="{field.name}" class="form-label">
                {field.name.replace('_', ' ').title()}
                {'<span class="text-danger">*</span>' if field.required else ''}
            </label>
            <input type="{field.get_input_type()}" {attr_str}>
            {f'<div class="invalid-feedback">{error}</div>' if error else ''}
            {f'<div class="form-text">{field.placeholder}</div>' if field.placeholder and not field.placeholder.startswith('Enter') else ''}
        </div>
        '''
        
        return template
    
    def _render_textarea(self, field: Field, value: Any, error: Optional[str]) -> str:
        """Render a textarea field."""
        attrs = field.get_input_attributes()
        
        # Add error class if needed
        if error:
            attrs['class'] += ' is-invalid'
        
        # Remove value from attrs for textarea
        attrs.pop('value', None)
        
        # Build attributes string
        attr_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items() if v is not False])
        
        template = f'''
        <div class="mb-3">
            <label for="{field.name}" class="form-label">
                {field.name.replace('_', ' ').title()}
                {'<span class="text-danger">*</span>' if field.required else ''}
            </label>
            <textarea {attr_str}>{value or ''}</textarea>
            {f'<div class="invalid-feedback">{error}</div>' if error else ''}
        </div>
        '''
        
        return template
    
    def _render_select(self, field: Field, value: Any, error: Optional[str]) -> str:
        """Render a select field for enums and lookup fields."""
        # Get choices - pass database instance for lookup fields
        db = getattr(self.table, 'db', None)
        choices = field.get_choices(db)
        
        options = ['<option value="">Choose...</option>']
        for choice_value, choice_label in choices:
            selected = 'selected' if str(value) == str(choice_value) else ''
            options.append(f'<option value="{choice_value}" {selected}>{choice_label}</option>')
        
        options_html = '\n'.join(options)
        error_class = ' is-invalid' if error else ''
        
        # Add special handling for lookup fields
        field_label = field.name.replace('_', ' ').title()
        if field.is_lookup_field():
            # Remove '_id' suffix from display if present
            if field.name.endswith('_id'):
                field_label = field.name[:-3].replace('_', ' ').title()
        
        template = f'''
        <div class="mb-3">
            <label for="{field.name}" class="form-label">
                {field_label}
                {'<span class="text-danger">*</span>' if field.required else ''}
            </label>
            <select name="{field.name}" id="{field.name}" class="form-select{error_class}" {'required' if field.required else ''}>
                {options_html}
            </select>
            {f'<div class="invalid-feedback">{error}</div>' if error else ''}
        </div>
        '''
        
        return template
    
    def _render_checkbox(self, field: Field, value: Any, error: Optional[str]) -> str:
        """Render a checkbox field."""
        checked = 'checked' if value else ''
        error_class = ' is-invalid' if error else ''
        
        template = f'''
        <div class="mb-3">
            <div class="form-check">
                <input type="checkbox" 
                       name="{field.name}" 
                       id="{field.name}" 
                       class="form-check-input{error_class}" 
                       value="1" 
                       {checked}>
                <label class="form-check-label" for="{field.name}">
                    {field.name.replace('_', ' ').title()}
                    {'<span class="text-danger">*</span>' if field.required else ''}
                </label>
                {f'<div class="invalid-feedback">{error}</div>' if error else ''}
            </div>
        </div>
        '''
        
        return template
    
    def render(self, template_name: str = None) -> str:
        """
        Render the complete form.
        
        Args:
            template_name: Optional custom template name
            
        Returns:
            Complete HTML form
        """
        if template_name:
            return render_template(template_name, form=self)
        
        # Use built-in mobile-first template
        return self._render_default_form()
    
    def _render_default_form(self) -> str:
        """Render the default mobile-first form template."""
        fields_html = []
        
        # Group fields into sections for mobile
        for i, field in enumerate(self.fields):
            field_html = self.render_field(field)
            fields_html.append(field_html)
        
        action_text = 'Create' if self.action == 'create' else 'Update'
        form_title = f"{action_text} {self.table.name.title()}"
        
        template = f'''
        <div class="container-fluid">
            <div class="row justify-content-center">
                <div class="col-12 col-lg-8 col-xl-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="bi bi-plus-circle me-2"></i>{form_title}
                            </h5>
                        </div>
                        <div class="card-body">
                            <form method="POST" data-loading>
                                {''.join(fields_html)}
                                
                                <div class="d-flex gap-2 flex-wrap mt-4">
                                    <button type="submit" class="btn btn-primary flex-fill">
                                        <i class="bi bi-check-lg me-1"></i>{action_text}
                                    </button>
                                    <a href="../" class="btn btn-outline-secondary flex-fill">
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
    
    def get_data_for_save(self) -> Dict[str, Any]:
        """
        Get cleaned data ready for saving to database.
        
        Returns:
            Dictionary of field values ready for model
        """
        save_data = {}
        
        for field in self.fields:
            value = self.data.get(field.name)
            
            # Skip None values for optional fields
            if value is None and not field.required:
                continue
            
            # Type conversion
            if field.type == 'number':
                try:
                    value = int(value) if value else None
                except (ValueError, TypeError):
                    value = None
            
            elif field.type in ['currency', 'float']:
                try:
                    value = float(value) if value else None
                except (ValueError, TypeError):
                    value = None
            
            elif field.type == 'boolean':
                value = bool(value)
            
            save_data[field.name] = value
        
        return save_data
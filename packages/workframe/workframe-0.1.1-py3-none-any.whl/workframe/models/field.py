"""Field definitions for WorkFrame models."""

import re
import logging
from typing import Any, Callable, List, Optional, Union

logger = logging.getLogger(__name__)


class Field:
    """
    Field definition for WorkFrame models with validation, types, and relationships.
    """
    
    def __init__(
        self,
        name: str,
        type: str = 'text',
        required: bool = True,
        readonly: bool = False,
        hidden: bool = False,
        hidden_in_form: bool = False,
        hidden_in_list: bool = False,
        optional: bool = False,
        placeholder: Optional[str] = None,
        default: Optional[Union[str, Callable]] = None,
        validation: Optional[Callable] = None,
        enum: Optional[List[str]] = None,
        lookup: Optional[str] = None,
        display: Optional[str] = None,
        value: Optional[str] = None,
        allow_new: bool = False,
        rows: Optional[int] = None,
        format: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a Field definition.
        
        Args:
            name: Field name
            type: Field type (text, email, phone, date, datetime, currency, textarea)
            required: Whether field is required
            readonly: Whether field is read-only
            hidden: Whether field is hidden everywhere
            hidden_in_form: Whether field is hidden in forms only
            hidden_in_list: Whether field is hidden in list views only
            optional: Whether field is optional (alias for required=False)
            placeholder: Placeholder text for input
            default: Default value (string or callable)
            validation: Custom validation function
            enum: List of enumeration options
            lookup: Table name for foreign key lookup
            display: Display field name for lookups
            value: Value field name for lookups
            allow_new: Allow creating new lookup records
            rows: Number of rows for textarea
            format: Format string for display
        """
        self.name = name
        self.type = type
        self.required = not optional if optional else required
        self.readonly = readonly
        self.hidden = hidden
        self.hidden_in_form = hidden_in_form
        self.hidden_in_list = hidden_in_list
        self.placeholder = placeholder
        self.default = default
        self.validation = validation
        self.enum = enum
        self.lookup = lookup
        self.display = display or 'name'  # Default display field
        self.value = value or 'id'  # Default value field
        self.allow_new = allow_new
        self.rows = rows
        self.format = format
        
        # Store any additional keyword arguments
        for key, val in kwargs.items():
            setattr(self, key, val)
        
        # Auto-detection based on field name
        self._auto_detect_type()
    
    def _auto_detect_type(self):
        """Auto-detect field type based on field name patterns."""
        name_lower = self.name.lower()
        
        # Email detection
        if 'email' in name_lower and self.type == 'text':
            self.type = 'email'
            if not self.validation:
                self.validation = self._email_validator
        
        # Phone detection - but no validation, just input type
        elif 'phone' in name_lower and self.type == 'text':
            self.type = 'phone'
            # No automatic validation - phone formats vary too much globally
        
        # Date detection
        elif name_lower.endswith('_date') and self.type == 'text':
            self.type = 'date'
        
        # Datetime detection
        elif name_lower.endswith('_at') and self.type == 'text':
            self.type = 'datetime'
        
        # Currency detection
        elif any(word in name_lower for word in ['price', 'cost', 'amount', 'salary']) and self.type == 'text':
            self.type = 'currency'
        
        # Boolean detection
        elif name_lower.startswith('is_') or name_lower.startswith('has_') and self.type == 'text':
            self.type = 'boolean'
    
    def _email_validator(self, value):
        """Built-in email validator."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, str(value)) is not None
    
    def _phone_validator(self, value):
        """
        Deprecated phone validator - too prescriptive for global use.
        Phone formats vary significantly worldwide. This is kept for
        backwards compatibility but no longer used by default.
        """
        import re
        # Very basic check - just ensure it's not empty and has some digits
        return bool(value and re.search(r'\d', str(value)))
    
    def validate(self, value):
        """
        Validate a value against this field's rules.
        
        Args:
            value: The value to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check required
        if self.required and (value is None or value == ''):
            return False, f"{self.name.title()} is required"
        
        # Skip validation for empty optional fields
        if not self.required and (value is None or value == ''):
            return True, None
        
        # Type-specific validation
        if self.type == 'email':
            if self.validation and not self.validation(value):
                return False, "Invalid email format"
        
        elif self.type == 'phone' and self.validation:
            # Only validate if explicitly set by developer
            if not self.validation(value):
                return False, "Invalid phone number format"
        
        elif self.enum and value not in self.enum:
            return False, f"Value must be one of: {', '.join(self.enum)}"
        
        elif self.type == 'number':
            try:
                int(value)
            except (ValueError, TypeError):
                return False, "Must be a valid number"
        
        elif self.type == 'currency' or self.type == 'float':
            try:
                float(value)
            except (ValueError, TypeError):
                return False, "Must be a valid number"
        
        # Custom validation
        if self.validation and callable(self.validation):
            try:
                if not self.validation(value):
                    return False, "Invalid value"
            except Exception as e:
                return False, f"Validation error: {str(e)}"
        
        return True, None
    
    def format_value(self, value):
        """
        Format a value for display based on field type.
        
        Args:
            value: The value to format
            
        Returns:
            Formatted string representation
        """
        if value is None:
            return ''
        
        if self.format:
            try:
                return self.format.format(value)
            except:
                return str(value)
        
        # Type-specific formatting
        if self.type == 'currency':
            try:
                return f"${float(value):,.2f}"
            except:
                return str(value)
        
        elif self.type == 'phone':
            # No automatic formatting - phone formats vary globally
            # Just return the value as entered by the user
            return str(value)
        
        elif self.type == 'date':
            if hasattr(value, 'strftime'):
                return value.strftime('%B %d, %Y')
            return str(value)
        
        elif self.type == 'datetime':
            if hasattr(value, 'strftime'):
                return value.strftime('%B %d, %Y at %I:%M %p')
            return str(value)
        
        elif self.type == 'boolean':
            return 'Yes' if value else 'No'
        
        return str(value)
    
    def get_input_type(self):
        """Get HTML input type for this field."""
        type_mapping = {
            'email': 'email',
            'phone': 'tel',
            'number': 'number',
            'currency': 'number',
            'float': 'number',
            'date': 'date',
            'datetime': 'datetime-local',
            'boolean': 'checkbox',
            'textarea': 'textarea',
        }
        return type_mapping.get(self.type, 'text')
    
    def get_input_attributes(self):
        """Get HTML input attributes for this field."""
        attrs = {
            'name': self.name,
            'id': self.name,
            'class': 'form-control',
            'required': self.required,
        }
        
        if self.placeholder:
            attrs['placeholder'] = self.placeholder
        
        if self.readonly:
            attrs['readonly'] = True
            attrs['class'] += ' form-control-plaintext'
        
        # Type-specific attributes
        if self.type == 'textarea':
            attrs['rows'] = self.rows or 3
            attrs['class'] = 'form-control'
        
        elif self.type == 'currency' or self.type == 'number':
            attrs['step'] = '0.01' if self.type == 'currency' else '1'
            attrs['min'] = '0'
        
        elif self.type == 'boolean':
            attrs['class'] = 'form-check-input'
        
        return attrs
    
    def is_lookup_field(self):
        """Check if this is a lookup/foreign key field."""
        return self.lookup is not None
    
    def is_enum_field(self):
        """Check if this is an enumeration field."""
        return self.enum is not None and len(self.enum) > 0
    
    def get_choices(self, db=None, workframe_app=None):
        """Get choices for select fields (enum or lookup)."""
        if self.enum:
            return [(value, value) for value in self.enum]
        
        if self.lookup:
            # Try to get choices from WorkFrame app registry first
            if workframe_app and hasattr(workframe_app, 'table_models'):
                return self._get_lookup_choices_from_registry(workframe_app)
            # Fallback to old method
            elif db:
                return self._get_lookup_choices(db)
        
        return []
    
    def _get_lookup_choices_from_registry(self, workframe_app):
        """Get choices for lookup fields using WorkFrame's model registry."""
        try:
            lookup_table_name = self.lookup.lower()
            
            if lookup_table_name not in workframe_app.table_models:
                logger.warning(f"Lookup table '{lookup_table_name}' not found in registry. Available tables: {list(workframe_app.table_models.keys())}")
                return []
            
            lookup_model = workframe_app.table_models[lookup_table_name]
            
            # Query all records from the lookup table
            records = workframe_app.db.session.query(lookup_model).all()
            
            # Build choices list using display and value fields
            choices = []
            for record in records:
                value = getattr(record, self.value, record.id)
                display = getattr(record, self.display, getattr(record, 'name', str(value)))
                choices.append((value, display))
            
            return choices
            
        except Exception as e:
            logger.exception(f"Lookup field '{self.name}' failed to load choices from registry: {e}")
            return []
    
    def _get_lookup_choices(self, db):
        """Get choices for lookup fields from database."""
        try:
            logger.debug(f"Getting lookup choices for field '{self.name}', lookup='{self.lookup}', display='{self.display}', value='{self.value}'")
            
            # Get the lookup table model
            lookup_model = self._get_lookup_model(db)
            logger.debug(f"Found lookup model: {lookup_model}")
            if not lookup_model:
                logger.warning(f"No lookup model found for table '{self.lookup}'")
                return []
            
            # Query all records from the lookup table
            records = db.session.query(lookup_model).all()
            logger.debug(f"Found {len(records)} records in lookup table")
            
            # Build choices list using display and value fields
            choices = []
            for record in records:
                value = getattr(record, self.value, record.id)
                display = getattr(record, self.display, getattr(record, 'name', str(value)))
                choices.append((value, display))
                logger.debug(f"Added choice: {value} -> {display}")
            
            logger.debug(f"Returning {len(choices)} choices: {choices}")
            return choices
            
        except Exception as e:
            logger.exception(f"Lookup field '{self.name}' failed to load choices: {e}")
            return []
    
    def _get_lookup_model(self, db):
        """Get the SQLAlchemy model for the lookup table."""
        # Try to find the model in the database registry
        lookup_table_name = self.lookup.lower()
        
        # Look through all models in the database
        for mapper in db.Model.registry._class_registry.values():
            if hasattr(mapper, 'mapped_class'):
                model_class = mapper.mapped_class
                if hasattr(model_class, '__tablename__') and model_class.__tablename__ == lookup_table_name:
                    return model_class
        
        return None
    
    def __repr__(self):
        return f"Field('{self.name}', type='{self.type}', required={self.required})"
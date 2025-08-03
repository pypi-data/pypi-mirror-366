"""Table class for database table definitions in WorkFrame."""

from typing import List, Dict, Any, Optional, Union
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, Date, ForeignKey
from sqlalchemy.orm import validates
from datetime import datetime
from .field import Field


class Table:
    """
    Table class for defining database tables and their structure.
    
    Handles the creation of SQLAlchemy models from field definitions,
    providing a high-level interface for business applications.
    """
    
    def __init__(self, name: str, fields: List[Union[str, Field]], db=None):
        """
        Initialize a Table with field definitions.
        
        Args:
            name: Table name (will be used as SQLAlchemy table name)
            fields: List of field definitions (strings or Field objects)
            db: SQLAlchemy database instance
        """
        self.name = name
        self.table_name = name.lower()
        self.db = db
        self.fields = []
        self.model = None
        
        # Process field definitions
        self._process_fields(fields)
        
        # Create SQLAlchemy model
        if db:
            self._create_model()
    
    def _process_fields(self, fields: List[Union[str, Field]]):
        """Process field definitions into Field objects."""
        for field_def in fields:
            if isinstance(field_def, str):
                # Simple string field definition
                field = Field(field_def)
            elif isinstance(field_def, Field):
                # Already a Field object
                field = field_def
            else:
                raise ValueError(f"Invalid field definition: {field_def}")
            
            self.fields.append(field)
    
    def _create_model(self):
        """Create SQLAlchemy model from field definitions."""
        if not self.db:
            raise ValueError("Database instance required to create model")
        
        # Create attributes dictionary for the model
        attrs = {
            '__tablename__': self.table_name,
            'id': Column(Integer, primary_key=True),
            'created_at': Column(DateTime, default=datetime.utcnow),
            'updated_at': Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        }
        
        # Add field columns
        for field in self.fields:
            column = self._field_to_column(field)
            if column is not None:
                attrs[field.name] = column
        
        # Add model methods
        attrs['__repr__'] = self._create_repr_method()
        attrs['to_dict'] = self._create_to_dict_method()
        attrs['from_dict'] = classmethod(self._create_from_dict_method())
        
        # Create the model class
        model_name = self._get_model_name()
        self.model = type(model_name, (self.db.Model,), attrs)
        
        return self.model
    
    def _field_to_column(self, field: Field) -> Optional[Column]:
        """Convert a Field to a SQLAlchemy Column."""
        # Skip system fields that are handled separately
        if field.name in ['id', 'created_at', 'updated_at']:
            return None
        
        # Determine SQLAlchemy column type
        column_type = self._get_column_type(field)
        
        # Build column arguments
        column_args = []
        column_kwargs = {
            'nullable': not field.required,
            'index': field.name in ['email', 'username'] or field.name.endswith('_id')
        }
        
        # Add unique constraint for email fields
        if field.name == 'email':
            column_kwargs['unique'] = True
        
        # Add default value
        if field.default is not None:
            if callable(field.default):
                column_kwargs['default'] = field.default
            else:
                column_kwargs['default'] = field.default
        
        return Column(column_type, *column_args, **column_kwargs)
    
    def _get_column_type(self, field: Field):
        """Get SQLAlchemy column type for a field."""
        type_mapping = {
            'text': String(255),
            'email': String(255),
            'phone': String(50),
            'string': String(255),
            'textarea': Text,
            'number': Integer,
            'float': Float,
            'currency': Float,
            'boolean': Boolean,
            'date': Date,
            'datetime': DateTime,
        }
        
        # Handle enum fields as strings
        if field.enum:
            return String(100)
        
        # Handle lookup fields as foreign keys
        if field.lookup:
            # Create foreign key reference to the lookup table
            fk_reference = f"{field.lookup.lower()}.id"
            return Integer  # For now, just use Integer - full ForeignKey relationships will be added in next iteration
        
        return type_mapping.get(field.type, String(255))
    
    def _get_model_name(self) -> str:
        """Generate model class name from table name."""
        # Convert snake_case to PascalCase
        words = self.name.replace('_', ' ').title().replace(' ', '')
        return words if words.endswith('s') else words
    
    def _create_repr_method(self):
        """Create __repr__ method for the model."""
        def __repr__(self):
            # Try to find a good display field
            display_value = getattr(self, 'name', None) or \
                           getattr(self, 'title', None) or \
                           getattr(self, 'username', None) or \
                           f"#{self.id}"
            return f"<{self.__class__.__name__} {display_value}>"
        return __repr__
    
    def _create_to_dict_method(self):
        """Create to_dict method for the model."""
        def to_dict(self):
            """Convert model instance to dictionary."""
            result = {}
            for field in self.fields:
                value = getattr(self, field.name, None)
                if value is not None:
                    # Handle datetime serialization
                    if isinstance(value, datetime):
                        result[field.name] = value.isoformat()
                    else:
                        result[field.name] = value
            
            # Add system fields
            result['id'] = self.id
            if hasattr(self, 'created_at') and self.created_at:
                result['created_at'] = self.created_at.isoformat()
            if hasattr(self, 'updated_at') and self.updated_at:
                result['updated_at'] = self.updated_at.isoformat()
            
            return result
        return to_dict
    
    def _create_from_dict_method(self):
        """Create from_dict class method for the model."""
        def from_dict(cls, data: Dict[str, Any]):
            """Create model instance from dictionary."""
            instance = cls()
            
            # Set field values
            for field in self.fields:
                if field.name in data:
                    setattr(instance, field.name, data[field.name])
            
            return instance
        return from_dict
    
    def get_field(self, name: str) -> Optional[Field]:
        """Get field definition by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def get_display_fields(self) -> List[Field]:
        """Get fields that should be displayed in list views."""
        return [f for f in self.fields if not f.hidden and not f.hidden_in_list]
    
    def get_form_fields(self) -> List[Field]:
        """Get fields that should be included in forms."""
        return [f for f in self.fields if not f.hidden and not f.hidden_in_form and not f.readonly]
    
    def get_required_fields(self) -> List[Field]:
        """Get fields that are required."""
        return [f for f in self.fields if f.required]
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate data against field definitions.
        
        Returns:
            Dictionary with field names as keys and lists of error messages as values
        """
        errors = {}
        
        for field in self.fields:
            field_errors = []
            value = data.get(field.name)
            
            # Skip readonly fields in validation
            if field.readonly:
                continue
            
            # Check required fields
            if field.required and (value is None or value == ''):
                field_errors.append(f"{field.name.title()} is required")
            
            # Field-specific validation
            if value is not None and value != '':
                # Email validation
                if field.type == 'email':
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, value):
                        field_errors.append("Invalid email format")
                
                # Enum validation
                if field.enum and value not in field.enum:
                    field_errors.append(f"Value must be one of: {', '.join(field.enum)}")
                
                # Custom validation
                if field.validation and callable(field.validation):
                    try:
                        if not field.validation(value):
                            field_errors.append("Invalid value")
                    except Exception as e:
                        field_errors.append(f"Validation error: {str(e)}")
            
            if field_errors:
                errors[field.name] = field_errors
        
        return errors
    
    def create_record(self, data: Dict[str, Any]):
        """Create a new record with validation."""
        if not self.model:
            raise ValueError("Model not created. Database instance required.")
        
        # Validate data
        errors = self.validate_data(data)
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        
        # Create and save record
        record = self.model.from_dict(data)
        self.db.session.add(record)
        self.db.session.commit()
        
        return record
    
    def update_record(self, record_id: int, data: Dict[str, Any]):
        """Update an existing record with validation."""
        if not self.model:
            raise ValueError("Model not created. Database instance required.")
        
        record = self.model.query.get_or_404(record_id)
        
        # Validate data
        errors = self.validate_data(data)
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        
        # Update record
        for field in self.fields:
            if field.name in data and not field.readonly:
                setattr(record, field.name, data[field.name])
        
        record.updated_at = datetime.utcnow()
        self.db.session.commit()
        
        return record
    
    def delete_record(self, record_id: int):
        """Delete a record."""
        if not self.model:
            raise ValueError("Model not created. Database instance required.")
        
        record = self.model.query.get_or_404(record_id)
        self.db.session.delete(record)
        self.db.session.commit()
        
        return True
    
    def query(self):
        """Get query object for this table's model."""
        if not self.model:
            raise ValueError("Model not created. Database instance required.")
        return self.model.query
    
    def __repr__(self):
        return f"<Table {self.name} ({len(self.fields)} fields)>"
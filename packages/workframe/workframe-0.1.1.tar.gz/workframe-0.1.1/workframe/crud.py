"""CRUD convenience function for WorkFrame."""

from .models.field import Field
from .models.table import Table
from .views.module import Module
from .views.linked_module import LinkedTableModule
from .views.manytomany_module import ManyToManyModule


def crud(table_name, fields, db=None, admin_required=False, many_to_one=None, many_to_many=None):
    """
    High-level convenience function to create a complete CRUD module.
    
    This is the main entry point for WorkFrame - it creates a complete
    CRUD interface from a simple field list.
    
    Args:
        table_name: Name of the database table
        fields: List of field definitions (strings or Field objects)
        db: SQLAlchemy database instance (will be set by WorkFrame)
        admin_required: If True, restrict all operations to admin users only
        many_to_one: Module instance for master table in many-to-one relationship
        many_to_many: Module instance for junction table management
    
    Returns:
        Module ready for registration with WorkFrame
    
    Example:
        # Simple CRUD
        contacts = crud('contacts', ['name', 'email', 'phone', 'company'])
        app.register_module('/contacts', contacts, menu_title='Contacts')
        
        # Many-to-one linked tables
        companies = crud('companies', ['name', 'industry'])
        contacts = crud('contacts', ['name', 'email', 'company_id'], many_to_one=companies)
        app.register_module('/contacts', contacts, menu_title='Contacts')
        
        # Admin-only module
        users = crud('users', ['username', 'email'], admin_required=True)
        app.register_module('/admin/users', users, menu_title='Users')
    """
    # Create Table with field definitions
    table = Table(table_name, fields, db=db)
    
    # Check for relationship parameters
    if many_to_one is not None:
        # Create LinkedTableModule for many-to-one relationship
        if not hasattr(many_to_one, 'table'):
            raise ValueError("many_to_one parameter must be a Module instance with a table attribute")
        
        module = LinkedTableModule(
            detail_table=table,
            master_module=many_to_one,
            name=table_name,
            admin_required=admin_required
        )
        
    elif many_to_many is not None:
        # Create ManyToManyModule for many-to-many relationship
        if not hasattr(many_to_many, 'table'):
            raise ValueError("many_to_many parameter must be a Module instance with a table attribute")
        
        # For many-to-many, we create a junction table between the current table and the target table
        # The 'table' parameter becomes the left side of the relationship
        left_module = Module(table, name=table_name, admin_required=admin_required)
        
        module = ManyToManyModule(
            left_module=left_module,
            right_module=many_to_many,
            name=f"{table_name}_{many_to_many.table.name}",
            admin_required=admin_required
        )
        
    else:
        # Create regular Module with all CRUD views
        module = Module(table, name=table_name, admin_required=admin_required)
    
    return module
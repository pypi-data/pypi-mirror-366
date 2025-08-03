# WorkFrame

Simple Flask-based framework for building business applications quickly.

## Overview

WorkFrame is a Python framework designed specifically for building business applications with minimal ceremony. It focuses on business logic while handling all the web application plumbing automatically.

### Core Philosophy
- **Business-first**: Target business applications, not generic web development
- **Zero ceremony**: Minimal boilerplate code required  
- **Convention over configuration**: Sensible defaults that work out of the box
- **Escape hatches**: Always provide ways to customize when needed
- **Developer experience**: Should feel like magic for common use cases
- **Production ready**: Suitable for real business applications from day one

## Quick Start

### Installation

```bash
pip install workframe
```

### Simple Example

Create a file called `app.py`:

```python
from workframe import WorkFrame, crud

# Create app with custom branding
app = WorkFrame(__name__, 
               app_name="My Business App", 
               app_description="Customer Management System")

# Create a simple contact management system
contacts = crud('contacts', ['name', 'email', 'phone', 'company'])
app.register_module('/contacts', contacts, menu_title='Contacts', icon='bi-person')

if __name__ == '__main__':
    app.run(debug=True)
```

Run the application:

```bash
python app.py
```

Visit `http://localhost:5000` and login with `admin/admin`.

That's it! You now have a fully functional business application with:
- User authentication and session management
- Complete CRUD operations for contacts
- Professional Bootstrap 5 dark theme UI
- Responsive design for mobile/tablet
- Admin interface for user management

### Advanced Example

```python
from workframe import WorkFrame, crud, Field

app = WorkFrame(__name__)

# Define companies first (lookup target)
companies = crud('companies', [
    'name',
    'website', 
    Field('industry', enum=['Technology', 'Healthcare', 'Finance', 'Other']),
    Field('employee_count', type='number'),
    Field('is_client', type='boolean', default=False),
])

# Define contacts with advanced field types
contacts = crud('contacts', [
    'name',                                                 # simple text field
    'email',                                                # auto-detected email field
    Field('company_id', lookup='companies', display='name'), # foreign key dropdown
    Field('status', enum=['Active', 'Inactive']),           # dropdown
    Field('created_date', readonly=True, hidden_in_form=True),
    Field('notes', type='textarea', optional=True),
])

# Register modules with icons (companies first since contacts references it)
app.register_module('/companies', companies, menu_title='Companies', icon='bi-building')
app.register_module('/contacts', contacts, menu_title='Contacts', icon='bi-person-lines-fill')

if __name__ == '__main__':
    app.run(debug=True)
```

## Features

### Automatic CRUD Generation
- **One-line CRUD**: `crud('table_name', ['field1', 'field2'])` creates complete CRUD
- **List views**: Paginated, searchable, sortable data tables
- **CSV Export**: Export data to CSV with one click (NEW)
- **Bulk Actions**: Select multiple records and delete in bulk (NEW)
- **Forms**: Auto-generated forms with validation
- **Detail views**: View and edit individual records

### Rich Field Types
- Text, email, phone, date, datetime, currency, textarea
- **Foreign key lookups with dropdowns** (NEW)
- Enumeration fields with select options
- Boolean fields with checkboxes
- Auto-detection based on field names
- Extensive customization options

### Built-in Authentication
- **Secure by default** - All CRUD operations require authentication
- **Smart navigation** - Menu items only appear when user is authenticated
- **Production-ready security** - No exposed credentials or security hints (NEW)
- User management with admin/regular user roles
- Session-based authentication
- Password hashing and security
- Admin interface for user management

### Professional UI
- Bootstrap 5 dark theme
- **Mobile-first responsive design**
- **Smart navigation** with conditional menu items and multi-level support (NEW)
- **Complete custom branding** - app name appears throughout entire application (NEW)
- **Clean, professional styling** - no framework branding or copyright clutter (NEW)
- **Bootstrap icons** for menu items with 1,800+ icons available (NEW)
- Auto-generated navigation
- Flash messaging system
- **Automatic schema migration** - your code is the source of truth (NEW)
- **Smart error handling** with helpful migration instructions (NEW)
- Professional data export functionality

### Business Application Ready
- Multi-module applications
- Admin vs user permission separation
- **Authentication required by default** - no unsecured endpoints
- **Automatic database schema updates** - no manual migrations needed
- Production-ready security defaults
- SQLite for development, configurable for production

## Customization Options

### Application Branding

```python
from workframe import WorkFrame

# Customize your application's branding
app = WorkFrame(__name__,
    app_name="My Business App",           # Custom app name in navbar and title
    app_description="Customer Management" # Custom footer description
)
```

### Admin-Only Modules

```python
# Create admin-restricted CRUD modules
admin_reports = crud('reports', [
    'title',
    'description', 
    Field('created_date', readonly=True)
], admin_required=True)  # Only admin users can access

app.register_module('/admin/reports', admin_reports, 
                   menu_title='Reports', 
                   admin_only=True)
```

### Navigation and Menus

```python
# Single-level menu with icon
app.register_module('/contacts', contacts, 
                   menu_title='Contacts', 
                   icon='bi-person-lines-fill')

# Multi-level menu (dropdown)
app.register_module('/contacts', contacts, 
                   menu_title='All Contacts', 
                   icon='bi-person-lines-fill', 
                   parent='Customer Management')

app.register_module('/companies', companies, 
                   menu_title='All Companies', 
                   icon='bi-building', 
                   parent='Customer Management')

# Admin-only modules
app.register_module('/reports', reports, 
                   menu_title='Reports', 
                   icon='bi-graph-up',
                   admin_only=True)
```

### Field Customization

```python
from workframe import Field

# Advanced field definition
Field('field_name',
    type='text|email|phone|date|datetime|currency|textarea',
    required=True|False,
    readonly=True|False, 
    hidden=True|False,
    placeholder='text',
    default='value'|callable,
    validation=callable,
    enum=['option1', 'option2'],          # dropdown options
    lookup='table_name',                   # foreign key
    display='field_name',                  # display field for lookups
    rows=5,                               # textarea rows
    format='${:,.2f}'                     # display formatting
)
```

## Generated Routes

Every module automatically gets:
- `/module` - List all records with bulk selection
- `/module/export.csv` - Export data to CSV (NEW)
- `/module/bulk-delete` - Delete multiple records (NEW)
- `/module/new` - Create new record
- `/module/<id>` - View record details  
- `/module/<id>/edit` - Edit record
- `/module/<id>/delete` - Delete record

Plus admin routes:
- `/admin/users` - User management
- `/admin/groups` - Group management

## Requirements

- Python 3.9+
- Flask 2.3+
- Modern web browser

## Development Status

WorkFrame is currently in beta. The core functionality is stable and suitable for development and testing. Production use is possible but please test thoroughly.

## Documentation

More detailed documentation and examples are coming soon.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.

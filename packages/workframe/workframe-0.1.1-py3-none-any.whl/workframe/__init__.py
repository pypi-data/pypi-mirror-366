"""
WorkFrame - Simple Flask-based framework for building business applications quickly.

A framework that focuses on business logic while handling all the web application plumbing.
Zero ceremony, convention over configuration, with escape hatches for customization.
"""

__version__ = "0.1.1"
__author__ = "WorkFrame Contributors"
__email__ = "workframe@example.com"

from .core import WorkFrame
from .crud import crud
from .models.field import Field
from .models.table import Table
from .forms.generator import Form
from .views.list import ListView
from .views.detail import DetailView
from .views.module import Module

# Import decorators for convenience
def login_required(f):
    """Decorator for views that require login. Import from flask_login for direct use."""
    from flask_login import login_required
    return login_required(f)

def admin_required(f):
    """Decorator for views that require admin privileges."""
    from .views.auth import admin_required
    return admin_required(f)

__all__ = [
    'WorkFrame', 'crud', 'Field', 'Table', 'Form', 
    'ListView', 'DetailView', 'Module',
    'login_required', 'admin_required'
]
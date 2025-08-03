"""Core WorkFrame class that wraps Flask with business application defaults."""

import os
import secrets
import logging
from flask import Flask, render_template, render_template_string, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.exceptions import NotFound, InternalServerError


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if colors are supported
        self.use_colors = self._supports_color()
    
    def _supports_color(self):
        """Check if the terminal supports colors."""
        import sys
        
        # Force enable colors for now - let user disable if needed
        try:
            # Initialize colorama for Windows compatibility
            import colorama
            colorama.init(autoreset=True)
            return True
        except ImportError:
            pass
        
        # Check environment variable to force enable/disable
        force_color = os.environ.get('FORCE_COLOR', '').lower()
        if force_color in ('1', 'true', 'yes'):
            return True
        if force_color in ('0', 'false', 'no'):
            return False
        
        # Default to True - let the terminal decide
        return True
    
    def format(self, record):
        if self.use_colors:
            # Add color to the log level
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class WorkFrame:
    """
    Main WorkFrame application class that wraps Flask with sensible defaults
    for business applications.
    """
    
    def __init__(self, import_name, app_name="WorkFrame", app_description="Business Application Framework", **kwargs):
        """
        Initialize WorkFrame application.
        
        Args:
            import_name: The name of the application package
            app_name: Custom application name (default: "WorkFrame")
            app_description: Custom application description for footer (default: "Business Application Framework")
            **kwargs: Additional Flask application arguments
        """
        # Store customizable application settings
        self.app_name = app_name
        self.app_description = app_description
        
        # Create Flask app with sensible defaults
        self.app = Flask(
            import_name,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            **kwargs
        )
        
        # Configure app with secure defaults
        self._configure_app()
        
        # Configure colored logging
        self._configure_logging()
        
        # Initialize extensions
        self.db = SQLAlchemy()
        self.login_manager = LoginManager()
        
        self._init_extensions()
        self._register_error_handlers()
        self._register_routes()
        self._register_auth_blueprint()
        self._register_template_globals()
        
        # Store registered modules for navigation
        self.modules = []
        self.admin_modules = []
        
        # Store table models for lookup resolution
        self.table_models = {}
        
        # Initialize models
        self._init_models()
        
        # Create admin modules (routes need to be registered before app starts)
        self._create_admin_modules()
    
    def _configure_app(self):
        """Configure Flask app with secure defaults for business applications."""
        # Generate secure secret key if not provided
        if not self.app.config.get('SECRET_KEY'):
            self.app.config['SECRET_KEY'] = secrets.token_hex(32)
        
        # Database configuration - SQLite for development
        if not self.app.config.get('SQLALCHEMY_DATABASE_URI'):
            db_path = os.path.join(os.getcwd(), 'workframe.db')
            self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        
        # Security settings
        self.app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        self.app.config.setdefault('WTF_CSRF_ENABLED', True)
        self.app.config.setdefault('SESSION_COOKIE_SECURE', False)  # Set to True in production
        self.app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
        self.app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    
    def _configure_logging(self):
        """Configure colored logging for console output."""
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create console handler with colored formatter
        console_handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Set logging level (can be configured via environment)
        log_level = os.environ.get('WORKFRAME_LOG_LEVEL', 'INFO').upper()
        root_logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Add handler to root logger
        root_logger.addHandler(console_handler)
        
        # Also configure Flask's logger
        self.app.logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    def _init_extensions(self):
        """Initialize Flask extensions."""
        self.db.init_app(self.app)
        
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'auth.login'
        self.login_manager.login_message = 'Please log in to access this page.'
        self.login_manager.login_message_category = 'info'
    
    def _init_models(self):
        """Initialize database models."""
        from .models.models import create_models
        self.User, self.Group = create_models(self.db)
        
        # User loader for Flask-Login
        @self.login_manager.user_loader
        def load_user(user_id):
            return self.User.query.get(int(user_id))
    
    def _register_error_handlers(self):
        """Register error handlers for common HTTP errors."""
        @self.app.errorhandler(404)
        def not_found_error(error):
            return render_template('errors/404.html'), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            self.db.session.rollback()
            return render_template('errors/500.html'), 500
    
    def _register_routes(self):
        """Register core application routes."""
        from flask_login import login_required
        
        @self.app.route('/')
        @login_required
        def dashboard():
            """Main dashboard showing available modules."""
            return render_template('dashboard.html')
    
    def _register_auth_blueprint(self):
        """Register authentication blueprint."""
        from .views.auth import create_auth_blueprint, login_required_decorator, admin_required
        auth_bp = create_auth_blueprint(self)
        self.app.register_blueprint(auth_bp)
        
        # Make decorators accessible on the WorkFrame instance
        self.login_required = login_required_decorator
        self.admin_required = admin_required
    
    def _register_template_globals(self):
        """Register template context processors for global variables."""
        @self.app.context_processor
        def inject_navigation():
            """Inject navigation modules and app settings into all templates."""
            return {
                'modules': self.modules,
                'admin_modules': self.admin_modules,
                'app_name': self.app_name,
                'app_description': self.app_description,
                'workframe_app': self
            }
    
    
    def register_module(self, url_prefix, module, menu_title=None, admin_only=False, icon=None, parent=None):
        """
        Register a module (blueprint) with the application.
        
        Args:
            url_prefix: URL prefix for the module routes
            module: The module/blueprint to register
            menu_title: Display name in navigation menu
            admin_only: Whether this module should only be visible to admins
            icon: Bootstrap icon class (e.g., 'bi-folder', 'bi-person')
            parent: Parent menu item for multi-level menus
        """
        # Set database instance on module's table(s) if they exist
        if hasattr(module, 'table') and module.table and not module.table.db:
            # Regular Module with single table
            module.table.db = self.db
            module.table._create_model()
            
            # Register the model for lookup resolution
            self.table_models[module.table.table_name] = module.table.model
            
        elif hasattr(module, 'detail_table') and hasattr(module, 'master_table'):
            # LinkedTableModule with detail and master tables
            if module.detail_table and not module.detail_table.db:
                module.detail_table.db = self.db
                module.detail_table._create_model()
                self.table_models[module.detail_table.table_name] = module.detail_table.model
            
            if module.master_table and not module.master_table.db:
                module.master_table.db = self.db
                module.master_table._create_model()
                self.table_models[module.master_table.table_name] = module.master_table.model
                
        elif hasattr(module, 'left_table') and hasattr(module, 'right_table'):
            # ManyToManyModule with left, right, and junction tables
            if module.left_table and not module.left_table.db:
                module.left_table.db = self.db
                module.left_table._create_model()
                self.table_models[module.left_table.table_name] = module.left_table.model
            
            if module.right_table and not module.right_table.db:
                module.right_table.db = self.db
                module.right_table._create_model()
                self.table_models[module.right_table.table_name] = module.right_table.model
            
            if module.junction_table and not module.junction_table.db:
                module._create_junction_model(self.db)
                self.table_models[module.junction_table.table_name] = module.junction_table.model
        
        # Register the blueprint with Flask
        self.app.register_blueprint(module.blueprint, url_prefix=url_prefix)
        
        # Create module info for navigation
        module_info = {
            'url_prefix': url_prefix,
            'title': menu_title or module.name,
            'blueprint': module.blueprint,
            'icon': icon or 'bi-folder'
        }
        
        # Handle multi-level menus
        if parent:
            # Find or create parent menu
            parent_found = False
            target_list = self.admin_modules if admin_only else self.modules
            
            for existing_module in target_list:
                if existing_module['title'] == parent:
                    if 'children' not in existing_module:
                        existing_module['children'] = []
                    existing_module['children'].append(module_info)
                    parent_found = True
                    break
            
            if not parent_found:
                # Create parent menu
                parent_info = {
                    'title': parent,
                    'icon': icon or 'bi-folder',
                    'children': [module_info]
                }
                target_list.append(parent_info)
        else:
            # Add as top-level menu item
            if admin_only:
                self.admin_modules.append(module_info)
            else:
                self.modules.append(module_info)
    
    def create_tables(self):
        """Create all database tables and initialize default data."""
        with self.app.app_context():
            try:
                # Create all tables
                self.db.create_all()
                
                # Create default groups first
                self._create_default_groups()
                
                # Create default admin user and assign to groups
                self._create_default_admin()
                
                # Try to create admin modules again now that database is ready
                self._create_admin_modules()
            except Exception as e:
                logging.error(f"Database creation/migration error: {e}")
                logging.info("If you're seeing schema errors, you may need to delete the database file and restart.")
                logging.info("For development: delete workframe.db and restart the application.")
                raise
    
    def _create_default_admin(self):
        """Create default admin user if no users exist."""
        # Check if any users exist
        if self.User.query.count() == 0:
            admin_user = self.User(
                username='admin',
                email='admin@workframe.local',
                password='admin',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_active=True
            )
            self.db.session.add(admin_user)
            self.db.session.commit()
            
            # Assign admin user to Administrators group
            admin_group = self.Group.query.filter_by(name='Administrators').first()
            if admin_group:
                admin_user.groups.append(admin_group)
                self.db.session.commit()
                logging.info("Created default admin user: admin/admin and assigned to Administrators group")
            else:
                logging.warning("Created default admin user: admin/admin (Administrators group not found)")
    
    def _create_default_groups(self):
        """Create default groups if no groups exist."""
        # Check if any groups exist
        if self.Group.query.count() == 0:
            # Create Administrators group
            admin_group = self.Group(
                name='Administrators',
                description='Full system administration privileges',
                is_active=True
            )
            self.db.session.add(admin_group)
            
            # Create Users group for regular users
            users_group = self.Group(
                name='Users', 
                description='Standard user privileges',
                is_active=True
            )
            self.db.session.add(users_group)
            
            self.db.session.commit()
            logging.info("Created default groups: Administrators and Users")
    
    def _create_admin_modules(self):
        """Create and register built-in admin modules using WorkFrame's CRUD system."""
        # Only create admin modules if models are available
        if not hasattr(self, 'User') or not hasattr(self, 'Group'):
            return
            
        from .crud import crud
        from .models.field import Field
        
        # Check if admin modules are already registered
        admin_paths = [module.get('url_prefix', '') for module in self.admin_modules]
        
        if '/admin/users' not in admin_paths:
            # Create enhanced user management with integrated group management
            from .views.user_management_module import UserManagementModule
            
            # Create enhanced user module with group management
            users_admin = UserManagementModule(
                user_model=self.User,
                group_model=self.Group,
                db=self.db,
                name='admin_users',
                admin_required=True
            )
            
            # Register the enhanced module
            self.app.register_blueprint(users_admin.blueprint, url_prefix='/admin/users')
            
            module_info = {
                'url_prefix': '/admin/users',
                'title': 'Users',
                'blueprint': users_admin.blueprint,
                'icon': 'bi-people'
            }
            self.admin_modules.append(module_info)
        
        if '/admin/groups' not in admin_paths:
            # Create group management CRUD
            group_fields = [
                Field('name', required=True),
                Field('description', type='textarea', optional=True),
                Field('is_active', type='boolean', default=True),
                Field('created_at', readonly=True, hidden_in_form=True, type='datetime')
            ]
            
            # Create admin groups module
            groups_admin = crud('admin_groups', group_fields, admin_required=True)
            groups_admin.table.model = self.Group
            groups_admin.table.table_name = 'groups'
            groups_admin.table.db = self.db
            
            self.app.register_blueprint(groups_admin.blueprint, url_prefix='/admin/groups')
            
            module_info = {
                'url_prefix': '/admin/groups',
                'title': 'Groups',
                'blueprint': groups_admin.blueprint,
                'icon': 'bi-collection'
            }
            self.admin_modules.append(module_info)
    
    
    def run(self, host=None, port=None, debug=None, **options):
        """
        Run the WorkFrame application.
        
        Args:
            host: Hostname to listen on
            port: Port to listen on  
            debug: Enable debug mode
            **options: Additional run options
        """
        # Create tables if they don't exist
        self.create_tables()
        
        # Run Flask app
        self.app.run(
            host=host or '127.0.0.1',
            port=port or 5000,
            debug=debug if debug is not None else True,
            **options
        )
    
    def __getattr__(self, name):
        """Delegate attribute access to underlying Flask app."""
        return getattr(self.app, name)
"""Authentication views for WorkFrame."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user


def create_auth_blueprint(app):
    """Create authentication blueprint with access to WorkFrame app instance."""
    
    auth = Blueprint('auth', __name__)
    
    @auth.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page and handler."""
        # Redirect if already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember'))
            
            if not username or not password:
                flash('Please enter both username and password.', 'danger')
                return render_template('auth/login.html')
            
            # Find user by username or email
            user = app.User.query.filter(
                (app.User.username == username) | (app.User.email == username)
            ).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    flash('Your account has been disabled. Please contact an administrator.', 'danger')
                    return render_template('auth/login.html')
                
                # Log the user in
                login_user(user, remember=remember)
                user.update_last_login()
                
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        
        return render_template('auth/login.html')
    
    @auth.route('/logout')
    @login_required
    def logout():
        """Logout handler."""
        user_name = current_user.full_name
        logout_user()
        flash(f'Goodbye, {user_name}!', 'info')
        return redirect(url_for('auth.login'))
    
    @auth.route('/profile')
    @login_required
    def profile():
        """User profile page."""
        return render_template('auth/profile.html', user=current_user)
    
    return auth


def login_required_decorator(f):
    """Decorator for views that require login."""
    return login_required(f)


def admin_required(f):
    """Decorator for views that require admin privileges."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function
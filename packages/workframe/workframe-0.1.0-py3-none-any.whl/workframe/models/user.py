"""User and Group models for WorkFrame authentication."""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for many-to-many relationship between users and groups
user_groups = db.Table('user_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship to groups
    groups = db.relationship('Group', secondary=user_groups, back_populates='users')
    
    def __init__(self, username, email, password=None, **kwargs):
        """Initialize user with password hashing."""
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        
        # Set other attributes
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @property
    def full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    @property
    def is_authenticated(self):
        """Required by Flask-Login."""
        return True
    
    @property
    def is_anonymous(self):
        """Required by Flask-Login."""
        return False
    
    def get_id(self):
        """Required by Flask-Login."""
        return str(self.id)
    
    def has_group(self, group_name):
        """Check if user belongs to a specific group."""
        return any(group.name == group_name for group in self.groups)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Group(db.Model):
    """Group model for role-based access control."""
    
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to users
    users = db.relationship('User', secondary=user_groups, back_populates='groups')
    
    def __init__(self, name, description=None, **kwargs):
        """Initialize group."""
        self.name = name
        self.description = description
        
        # Set other attributes
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_user(self, user):
        """Add user to this group."""
        if user not in self.users:
            self.users.append(user)
    
    def remove_user(self, user):
        """Remove user from this group."""
        if user in self.users:
            self.users.remove(user)
    
    @property
    def user_count(self):
        """Get number of users in this group."""
        return len(self.users)
    
    def __repr__(self):
        return f'<Group {self.name}>'
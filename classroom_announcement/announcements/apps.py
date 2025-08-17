"""
Django App Configuration for Classroom Announcement Application.

This module contains the app configuration for the announcements app,
which handles all classroom-related functionality including rooms,
memberships, announcements, and user interactions.
"""

from django.apps import AppConfig


class AnnouncementsConfig(AppConfig):
    """
    Configuration class for the announcements Django app.
    
    This app provides a comprehensive classroom announcement system with:
    - Multi-level user roles (Owner, Admin, Member)
    - Room creation and management
    - Announcement posting and reactions
    - User account management and statistics
    
    Features:
        - Secure room access with unique codes
        - Role-based permissions system
        - Real-time reaction system
        - User activity tracking
        - Responsive glassmorphism UI design
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'announcements'
    verbose_name = 'Classroom Announcements'

"""
Django Admin Configuration for Classroom Announcement Application.

This module configures the Django admin interface for managing
classroom announcement application models. It provides administrative
access to rooms, memberships, announcements, and reactions.

Registered Models:
    Room: Classroom rooms with management capabilities
    RoomMembership: User memberships and roles within rooms
    Announcement: Announcements posted in rooms
    AnnouncementReaction: User reactions to announcements

The admin interface allows superusers to:
- View and manage all rooms and their settings
- Monitor user memberships and role assignments
- Moderate announcements and content
- View reaction statistics and user interactions
"""

from django.contrib import admin
from .models import Room, RoomMembership, Announcement, AnnouncementReaction


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Admin interface for Room model.
    
    Provides comprehensive management of classroom rooms including
    viewing room details, managing memberships, and monitoring activity.
    """
    list_display = ['room_name', 'room_code', 'created_by', 'created_at', 'member_count']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['room_name', 'room_code', 'created_by__username']
    readonly_fields = ['room_code', 'created_at', 'updated_at']
    
    def member_count(self, obj):
        """Display the number of members in the room."""
        return obj.memberships.count()
    member_count.short_description = 'Members'


@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    """
    Admin interface for RoomMembership model.
    
    Manages user memberships and role assignments within rooms.
    """
    list_display = ['user', 'room', 'role', 'joined_at', 'promoted_by']
    list_filter = ['role', 'joined_at', 'promoted_at']
    search_fields = ['user__username', 'room__room_name']
    readonly_fields = ['joined_at', 'promoted_at']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    Admin interface for Announcement model.
    
    Provides moderation and management capabilities for announcements.
    """
    list_display = ['title', 'room', 'author', 'created_at', 'reaction_count']
    list_filter = ['created_at', 'room', 'author']
    search_fields = ['title', 'content', 'author__username', 'room__room_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def reaction_count(self, obj):
        """Display the number of reactions on the announcement."""
        return obj.reactions.count()
    reaction_count.short_description = 'Reactions'


@admin.register(AnnouncementReaction)
class AnnouncementReactionAdmin(admin.ModelAdmin):
    """
    Admin interface for AnnouncementReaction model.
    
    Monitors user reactions and engagement with announcements.
    """
    list_display = ['user', 'announcement', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'announcement__title']
    readonly_fields = ['created_at']
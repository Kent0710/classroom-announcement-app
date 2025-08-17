"""
Models for the Classroom Announcement Application.

This module contains all database models for managing classroom rooms,
user memberships, announcements, and reactions within the application.

Classes:
    Room: Represents a classroom room with unique code and ownership
    RoomMembership: Tracks user memberships and roles within rooms
    Announcement: Represents announcements posted in rooms
    AnnouncementReaction: Tracks user reactions to announcements
"""

from django.db import models
from django.contrib.auth.models import User
import string
import random


class Room(models.Model):
    """
    Model representing a classroom room.
    
    Each room has a unique name and 6-character code that users can use to join.
    Rooms have an owner (creator) and can have multiple members with different roles.
    
    Attributes:
        room_name (CharField): Unique name of the room (max 100 chars)
        room_code (CharField): Unique 6-character alphanumeric code for joining
        created_by (ForeignKey): User who created the room (owner)
        created_at (DateTimeField): Timestamp when room was created
        updated_at (DateTimeField): Timestamp when room was last updated
    
    Methods:
        is_owner(user): Check if user is the room owner
        is_admin(user): Check if user is admin or owner
        is_member(user): Check if user is a member
        can_access(user): Check if user can access the room
        get_user_role(user): Get user's role in the room
        get_admins(): Get all admin users
        get_members(): Get all regular member users
        generate_room_code(): Static method to generate unique room codes
    """
    room_name = models.CharField(max_length=100, verbose_name="Room Name", unique=True)
    room_code = models.CharField(max_length=6, unique=True, verbose_name="Room Code")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.room_name} ({self.room_code})"
    
    def is_owner(self, user):
        """
        Check if the given user is the owner (original creator) of the room.
        
        Args:
            user (User): The user to check ownership for
            
        Returns:
            bool: True if user is the room owner, False otherwise
        """
        return self.created_by == user
    
    def is_admin(self, user):
        """
        Check if the given user is an admin or owner of the room.
        
        Admin privileges include all owner privileges except deleting the room
        and promoting other users to admin level.
        
        Args:
            user (User): The user to check admin status for
            
        Returns:
            bool: True if user is admin or owner, False otherwise
        """
        if self.is_owner(user):
            return True
        membership = RoomMembership.objects.filter(room=self, user=user).first()
        return membership and membership.is_admin()
    
    def is_member(self, user):
        """
        Check if the given user is a member of the room.
        
        This includes owners, admins, and regular members.
        
        Args:
            user (User): The user to check membership for
            
        Returns:
            bool: True if user is a member of the room, False otherwise
        """
        return RoomMembership.objects.filter(room=self, user=user).exists()
    
    def can_access(self, user):
        """
        Check if the given user can access the room.
        
        Users can access a room if they are the owner or have a membership.
        
        Args:
            user (User): The user to check access for
            
        Returns:
            bool: True if user can access the room, False otherwise
        """
        return self.is_owner(user) or self.is_member(user)
    
    def get_user_role(self, user):
        """
        Get the role of a user in this room.
        
        Args:
            user (User): The user to get the role for
            
        Returns:
            str: The user's role ('owner', 'admin', 'member') or None if not a member
        """
        if self.is_owner(user):
            return 'owner'
        membership = RoomMembership.objects.filter(room=self, user=user).first()
        return membership.role if membership else None
    
    def get_admins(self):
        """
        Get all admin users for this room.
        
        This includes both the owner and users with admin role.
        
        Returns:
            list[User]: List of User objects with admin privileges
        """
        admin_memberships = self.memberships.filter(role__in=['admin', 'owner'])
        return [membership.user for membership in admin_memberships]
    
    def get_members(self):
        """
        Get all regular member users for this room.
        
        This excludes admins and owner, returning only users with 'member' role.
        
        Returns:
            list[User]: List of User objects with member role only
        """
        member_memberships = self.memberships.filter(role='member')
        return [membership.user for membership in member_memberships]
    
    @staticmethod
    def generate_room_code():
        """
        Generate a unique 6-character alphanumeric room code.
        
        The code consists of uppercase letters and digits. This method ensures
        uniqueness by checking existing room codes in the database.
        
        Returns:
            str: A unique 6-character room code
        """
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Room.objects.filter(room_code=code).exists():
                return code


class RoomMembership(models.Model):
    """
    Model to track user memberships and roles within rooms.
    
    This model manages the many-to-many relationship between users and rooms,
    with additional role information and promotion tracking.
    
    Role Hierarchy:
        - Owner: Original room creator, highest privileges
        - Admin: Promoted by owner, can manage members and announcements
        - Member: Regular user, can view and react to announcements
    
    Attributes:
        room (ForeignKey): The room this membership belongs to
        user (ForeignKey): The user who has this membership
        role (CharField): User's role in the room (member/admin/owner)
        joined_at (DateTimeField): When the user joined the room
        promoted_at (DateTimeField): When user was promoted to admin (nullable)
        promoted_by (ForeignKey): User who promoted this member (nullable)
    
    Methods:
        is_owner(): Check if this membership represents the room owner
        is_admin(): Check if this membership represents an admin
        can_promote_demote(target): Check if can promote/demote target membership
    """
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),  # Original creator - has highest privileges
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    promoted_at = models.DateTimeField(null=True, blank=True)  # When promoted to admin
    promoted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promoted_users")
    
    class Meta:
        unique_together = ('room', 'user')
        verbose_name = "Room Membership"
        verbose_name_plural = "Room Memberships"
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.room.room_name} ({self.get_role_display()})"
    
    def is_owner(self):
        """
        Check if this membership represents the room owner.
        
        Returns:
            bool: True if this user is the room owner, False otherwise
        """
        return self.role == 'owner'
    
    def is_admin(self):
        """
        Check if this membership represents an admin or owner.
        
        Admin privileges include managing members and announcements,
        but owner has additional privileges like room deletion.
        
        Returns:
            bool: True if user has admin privileges or is owner, False otherwise
        """
        return self.role in ['admin', 'owner']
    
    def can_promote_demote(self, target_membership):
        """
        Check if this user can promote or demote the target membership.
        
        Permission Rules:
        - Owner can promote/demote anyone except themselves
        - Admin can only promote/demote regular members
        - Members cannot promote/demote anyone
        
        Args:
            target_membership (RoomMembership): The membership to check against
            
        Returns:
            bool: True if this user can promote/demote the target, False otherwise
        """
        if self.role == 'owner':
            # Owner can promote/demote anyone except themselves
            return target_membership.user != self.user
        elif self.role == 'admin':
            # Admin can only promote/demote regular members
            return target_membership.role == 'member'
        return False


class Announcement(models.Model):
    """
    Model representing announcements posted in rooms.
    
    Announcements are the primary content that users interact with in rooms.
    They can be posted by any room member and can receive reactions from users.
    
    Attributes:
        room (ForeignKey): The room where this announcement was posted
        author (ForeignKey): The user who created this announcement
        title (CharField): Title of the announcement (max 200 chars)
        content (TextField): Main content/body of the announcement
        created_at (DateTimeField): When the announcement was created
        updated_at (DateTimeField): When the announcement was last modified
    """
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="announcements")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=200, verbose_name="Announcement Title")
    content = models.TextField(verbose_name="Announcement Content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.room.room_name}"


class AnnouncementReaction(models.Model):
    """
    Model representing user reactions to announcements.
    
    Users can react to announcements with various emoji types. Each user
    can only have one reaction per announcement (enforced by unique_together).
    
    Available Reactions:
        - like: 👍 (Thumbs up)
        - love: ❤️ (Heart)
        - laugh: 😂 (Laughing face)
        - wow: 😮 (Surprised face)
        - sad: 😢 (Sad face)
        - angry: 😠 (Angry face)
    
    Attributes:
        announcement (ForeignKey): The announcement being reacted to
        user (ForeignKey): The user who made the reaction
        reaction_type (CharField): Type of reaction from REACTION_CHOICES
        created_at (DateTimeField): When the reaction was created
    """
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
    ]
    
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="announcement_reactions")
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('announcement', 'user')
        verbose_name = "Announcement Reaction"
        verbose_name_plural = "Announcement Reactions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_reaction_type_display()} - {self.announcement.title}"

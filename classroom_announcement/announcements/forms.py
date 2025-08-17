"""
Forms for the Classroom Announcement Application.

This module contains all form classes used for user input validation
and data collection throughout the application.

Forms included:
    CustomSignUpForm: User registration with simplified fields
    CustomSignInForm: User authentication/login
    RoomCreationForm: Creating new classroom rooms
    JoinRoomForm: Joining existing rooms with room codes
    AnnouncementForm: Creating and editing announcements
    RoomEditForm: Editing room information

All forms include custom styling and validation appropriate for
the glassmorphism design theme of the application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Room, Announcement


class CustomSignUpForm(UserCreationForm):
    """
    Custom user registration form with simplified fields.
    
    This form removes the password confirmation field and email requirement
    to streamline the registration process. Only username and password
    are required for account creation.
    
    Fields:
        username: Unique username for the account
        password1: User's chosen password
        
    Styling:
        - Custom CSS classes for glassmorphism design
        - Placeholder text for better UX
        - Responsive form styling
    """
    
    class Meta:
        model = User
        fields = ('username', 'password1')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field attributes
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your username',
            'id': 'username'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'id': 'password'
        })
        
        # Remove password2 field
        if 'password2' in self.fields:
            del self.fields['password2']
    
    def save(self, commit=True):
        """
        Save the user with properly hashed password.
        
        Args:
            commit (bool): Whether to save to database immediately
            
        Returns:
            User: The created user instance
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomSignInForm(AuthenticationForm):
    """
    Custom user authentication form with styled fields.
    
    Extends Django's built-in AuthenticationForm with custom styling
    to match the application's glassmorphism design theme.
    
    Fields:
        username: User's username for authentication
        password: User's password for authentication
        
    Features:
        - Custom CSS classes for consistent styling
        - Placeholder text for better user experience
        - Responsive design elements
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field attributes
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your username',
            'id': 'username'
        })
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'id': 'password'
        })

class RoomCreationForm(forms.ModelForm):
    """
    Form for creating new classroom rooms.
    
    Allows users to create new rooms with custom names and automatically
    generated unique room codes for joining.
    
    Fields:
        room_name: Custom name for the room (e.g., "Math 101", "Physics Lab")
        room_code: Auto-generated unique 6-character code (read-only)
        
    Features:
        - Auto-generates unique room codes
        - Validates room name uniqueness
        - Custom styling for form elements
        - Helpful placeholder text
    """
    
    class Meta:
        model = Room
        fields = ['room_name', 'room_code']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field attributes
        self.fields['room_name'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter room name (e.g., Math 101, Physics Lab)',
            'id': 'room_name'
        })
        
        self.fields['room_code'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter 6-character room code (e.g., ABC123)',
            'id': 'room_code',
            'maxlength': '6',
            'minlength': '6'
        })
        
        # Add help text
        self.fields['room_name'].help_text = "Choose a descriptive name for your classroom"
        self.fields['room_code'].help_text = "6-character code that students will use to join"
    
    def clean_room_code(self):
        """
        Validate and normalize the room code.
        
        Returns:
            str: Uppercase, validated room code
            
        Raises:
            ValidationError: If code is invalid or already exists
        """
        room_code = self.cleaned_data.get('room_code')
        if room_code:
            room_code = room_code.upper()
            if len(room_code) != 6:
                raise forms.ValidationError("Room code must be exactly 6 characters long.")
            if not room_code.isalnum():
                raise forms.ValidationError("Room code can only contain letters and numbers.")
            if Room.objects.filter(room_code=room_code).exists():
                raise forms.ValidationError("This room code is already taken. Please choose another.")
        return room_code


class JoinRoomForm(forms.Form):
    """
    Form for joining an existing room using a room code.
    
    Simple form that accepts a 6-character room code and validates
    that the room exists and is accessible.
    
    Fields:
        room_code: 6-character alphanumeric code for the target room
        
    Validation:
        - Code must be exactly 6 characters
        - Code must contain only letters and numbers
        - Room with the code must exist
        - User must not already be a member
    """
    room_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 6-character room code',
            'id': 'room_code',
            'style': 'text-transform: uppercase;'
        }),
        help_text="Enter the room code provided by your teacher"
    )
    
    def clean_room_code(self):
        """
        Validate that the room code exists.
        
        Returns:
            str: Uppercase room code
            
        Raises:
            ValidationError: If room doesn't exist
        """
        room_code = self.cleaned_data.get('room_code')
        if room_code:
            room_code = room_code.upper()
            if not Room.objects.filter(room_code=room_code).exists():
                raise forms.ValidationError("Room with this code does not exist.")
        return room_code


class AnnouncementForm(forms.ModelForm):
    """
    Form for creating and editing announcements.
    
    Used by room members to post new announcements or edit existing ones.
    Supports rich text content and requires a descriptive title.
    
    Fields:
        title: Brief, descriptive title for the announcement
        content: Detailed announcement content/body
        
    Features:
        - Character limits for title and content
        - Helpful placeholder text
        - Textarea widget for content with proper sizing
        - Validation for meaningful content
    """
    
    class Meta:
        model = Announcement
        fields = ['title', 'content']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field attributes
        self.fields['title'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter announcement title',
            'id': 'announcement_title'
        })
        
        self.fields['content'].widget.attrs.update({
            'class': 'form-textarea',
            'placeholder': 'Write your announcement content here...',
            'id': 'announcement_content',
            'rows': '5'
        })
        
        # Add help text
        self.fields['title'].help_text = "Give your announcement a clear, descriptive title"
        self.fields['content'].help_text = "Provide detailed information about your announcement"


class RoomEditForm(forms.ModelForm):
    """
    Form for editing room details.
    
    Allows room owners and admins to modify room information.
    Currently supports editing the room name only.
    
    Fields:
        room_name: Updated name for the room
        
    Notes:
        - Room code cannot be changed to maintain joining links
        - Only accessible to room admins and owners
        - Validates room name uniqueness
    """
    
    class Meta:
        model = Room
        fields = ['room_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['room_name'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter room name',
            'id': 'room_name'
        })

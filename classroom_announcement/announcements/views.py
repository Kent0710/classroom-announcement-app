"""
Views for the Classroom Announcement Application.

This module contains all view functions for handling HTTP requests and responses
in the classroom announcement system. It includes authentication, room management,
announcements, and user interactions.

Views included:
    Authentication: landing_page, signUp, signIn, logout_view
    Room Management: home, create_room, join_room, room_detail, delete_room
    User Management: kick_member, promote_user, demote_user
    Announcements: toggle_reaction, delete_announcement
    User Profile: account

Dependencies:
    - Django authentication system
    - Custom forms for user input validation
    - Models for data persistence
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomSignUpForm, CustomSignInForm, RoomCreationForm, JoinRoomForm, AnnouncementForm, RoomEditForm
from .models import Room, RoomMembership, Announcement, AnnouncementReaction


def landing_page(request):
    """
    Display the landing page for anonymous users.
    
    This is the entry point for users who are not authenticated.
    Provides navigation to sign up or sign in.
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered landing page template
    """
    return render(request, 'announcements/landing-page.html')


def signUp(request):
    """
    Handle user registration.
    
    GET: Display the sign up form
    POST: Process form submission, create new user account, and log them in
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered signup form or redirect to home on success
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomSignUpForm()
    
    return render(request, 'announcements/signup.html', {'form': form})

def signIn(request):
    """
    Handle user authentication/login.
    
    GET: Display the sign in form
    POST: Process login credentials and authenticate user
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered signin form or redirect to home on success
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = CustomSignInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomSignInForm()
    
    return render(request, 'announcements/signIn.html', {'form': form})

@login_required
def home(request):
    """
    Display the user's dashboard/home page.
    
    Shows rooms owned by the user and rooms where they are members.
    Provides navigation to create new rooms or join existing ones.
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered home page with user's rooms
        
    Context:
        user: Current authenticated user
        user_rooms: Rooms created by the user
        member_rooms: Rooms where user is a member
        has_rooms: Boolean indicating if user has any room associations
    """
    # Get rooms where user is creator (owner)
    user_rooms = Room.objects.filter(created_by=request.user)
    # Get rooms where user is a member (including admin roles)
    member_rooms = Room.objects.filter(memberships__user=request.user)
    
    context = {
        'user': request.user,
        'user_rooms': user_rooms,
        'member_rooms': member_rooms,
        'has_rooms': user_rooms.exists() or member_rooms.exists(),
    }
    return render(request, 'announcements/home.html', context)


@login_required
def join_room(request):
    """
    Handle joining a room using a room code.
    
    GET: Display the join room form
    POST: Process room code and add user to the room as a member
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered join form or redirect to room on success
        
    Validation:
        - Room code must exist
        - User cannot join their own room
        - User cannot join a room they're already a member of
    """
    form = JoinRoomForm()
    
    if request.method == "POST":
        form = JoinRoomForm(request.POST)
        if form.is_valid():
            room_code = form.cleaned_data['room_code']
            room = Room.objects.get(room_code=room_code)
            
            # Check if user is the owner
            if room.is_owner(request.user):
                messages.info(request, "You are the owner of this room.")
                return redirect('room_detail', room_id=room.id)
            
            # Check if user is already a member
            existing_membership = RoomMembership.objects.filter(room=room, user=request.user).first()
            if existing_membership:
                messages.info(request, f"You are already a {existing_membership.get_role_display().lower()} of this room.")
                return redirect('room_detail', room_id=room.id)
            
            # Add user as member
            RoomMembership.objects.create(room=room, user=request.user, role='member')
            messages.success(request, f"Successfully joined {room.room_name}!")
            return redirect('room_detail', room_id=room.id)
    
    context = {
        'form': form,
    }
    return render(request, 'announcements/join_room.html', context)

@login_required
def room_detail(request, room_id):
    """
    Display detailed view of a specific room.
    
    Shows room information, member list with roles, announcements, and provides
    management capabilities based on user's role in the room.
    
    Features:
    - View all announcements with reactions
    - Post new announcements (if member)
    - Manage members (if admin/owner)
    - Promote/demote users (if owner/admin with permissions)
    - Delete room (if owner)
    
    Args:
        request (HttpRequest): The HTTP request object
        room_id (int): ID of the room to display
        
    Returns:
        HttpResponse: Rendered room detail page or redirect if no access
        
    Context:
        room: Room object
        announcements_with_reactions: List of announcements with reaction data
        user_role: Current user's role in the room
        is_owner: Boolean if user is room owner
        is_admin: Boolean if user is admin or owner
        owner_membership: RoomMembership object for room owner
        admin_memberships: QuerySet of admin memberships
        member_memberships: QuerySet of member memberships
        announcement_form: Form for creating new announcements
    """
    room = get_object_or_404(Room, id=room_id)
    
    # Check if user can access this room
    if not room.can_access(request.user):
        messages.error(request, "You don't have permission to access this room.")
        return redirect('home')
    
    # Get all announcements for this room
    announcements = room.announcements.all()
    
    # Get user role and permissions
    user_role = room.get_user_role(request.user)
    is_owner = room.is_owner(request.user)
    is_admin = room.is_admin(request.user)
    
    # Get room memberships organized by role
    owner_membership = room.memberships.filter(role='owner').first()
    admin_memberships = room.memberships.filter(role='admin')
    member_memberships = room.memberships.filter(role='member')
    
    # Get current user's membership for role management
    current_user_membership = room.memberships.filter(user=request.user).first()
    
    # Forms
    announcement_form = None
    room_edit_form = None
    
    if is_admin:
        announcement_form = AnnouncementForm()
        room_edit_form = RoomEditForm(instance=room)
    
    # Handle POST requests
    if request.method == "POST":
        # Create announcement (admin+ only)
        if 'create_announcement' in request.POST and is_admin:
            announcement_form = AnnouncementForm(request.POST)
            if announcement_form.is_valid():
                announcement = announcement_form.save(commit=False)
                announcement.room = room
                announcement.author = request.user
                announcement.save()
                messages.success(request, "Announcement created successfully!")
                return redirect('room_detail', room_id=room.id)
        
        # Edit room details (admin+ only)
        elif 'edit_room' in request.POST and is_admin:
            room_edit_form = RoomEditForm(request.POST, instance=room)
            if room_edit_form.is_valid():
                room_edit_form.save()
                messages.success(request, "Room details updated successfully!")
                return redirect('room_detail', room_id=room.id)
        
        # Leave room (members and admins, but not owner)
        elif 'leave_room' in request.POST and not is_owner:
            if current_user_membership:
                current_user_membership.delete()
                messages.success(request, f"You have left {room.room_name}.")
                return redirect('home')
    
    # Get user's reactions for this room's announcements and prepare reaction data
    user_reactions = {}
    announcements_with_reactions = []
    
    if announcements:
        # Get user's specific reactions
        reactions = AnnouncementReaction.objects.filter(
            announcement__in=announcements, 
            user=request.user
        )
        user_reactions = {r.announcement_id: r.reaction_type for r in reactions}
        
        # Prepare announcements with reaction data
        for announcement in announcements:
            reaction_data = []
            for reaction_type, emoji in AnnouncementReaction.REACTION_CHOICES:
                count = announcement.reactions.filter(reaction_type=reaction_type).count()
                is_active = user_reactions.get(announcement.id) == reaction_type
                reaction_data.append({
                    'type': reaction_type,
                    'emoji': emoji,
                    'count': count,
                    'is_active': is_active,
                })
            
            announcement.reaction_data = reaction_data
            announcements_with_reactions.append(announcement)
    
    context = {
        'room': room,
        'announcements': announcements_with_reactions,
        'user_role': user_role,
        'is_owner': is_owner,
        'is_admin': is_admin,
        'owner_membership': owner_membership,
        'admin_memberships': admin_memberships,
        'member_memberships': member_memberships,
        'current_user_membership': current_user_membership,
        'announcement_form': announcement_form,
        'room_edit_form': room_edit_form,
        'user_reactions': user_reactions,
    }
    return render(request, 'announcements/room_detail.html', context)

@login_required
def create_room(request):
    """
    Handle room creation.
    
    GET: Display room creation form
    POST: Process form submission and create new room with user as owner
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered create room form or redirect to home on success
        
    Notes:
        - Automatically sets the current user as room owner
        - Generates unique room code automatically
        - Redirects to home page after successful creation
    """
    if request.method == "POST":
        form = RoomCreationForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            room.save()
            return redirect('home')  # Redirect to home or room details page
    else:
        form = RoomCreationForm()
    
    return render(request, 'announcements/create-room.html', {'form': form})

def logout_view(request):
    """
    Handle user logout.
    
    Logs out the current user and redirects to the landing page.
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Redirect to landing page
    """
    auth_logout(request)
    return redirect('landing_page')


@login_required
def account(request):
    """
    Display user account page with statistics and activity information.
    
    Shows comprehensive user data including:
    - Account statistics (rooms owned/joined, announcements, reactions)
    - List of owned rooms with member counts
    - List of joined rooms with user's role
    - Recent announcements activity
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered account page with user statistics
        
    Context:
        owned_rooms: Rooms created by the user
        joined_rooms: Rooms where user is a member (with role info)
        stats: Dictionary with user statistics
        recent_announcements: Latest announcements by the user
    """
    user = request.user
    
    # Get owned rooms
    owned_rooms = Room.objects.filter(created_by=user).prefetch_related('memberships', 'announcements')
    
    # Get joined rooms (as member or admin, not owner)
    joined_rooms = RoomMembership.objects.filter(user=user).exclude(
        room__created_by=user
    ).select_related('room').prefetch_related('room__memberships', 'room__announcements')
    
    # Calculate statistics
    owned_rooms_count = owned_rooms.count()
    joined_rooms_count = joined_rooms.count()
    announcements_count = Announcement.objects.filter(author=user).count()
    reactions_count = AnnouncementReaction.objects.filter(user=user).count()
    
    # Get recent activity
    recent_activity = []
    
    # Recent announcements created
    recent_announcements = Announcement.objects.filter(author=user).order_by('-created_at')[:3]
    for announcement in recent_announcements:
        recent_activity.append({
            'icon': '📢',
            'title': f'Created announcement "{announcement.title}"',
            'description': f'In {announcement.room.room_name}',
            'time': announcement.created_at,
        })
    
    # Recent reactions given
    recent_reactions = AnnouncementReaction.objects.filter(user=user).order_by('-created_at')[:3]
    for reaction in recent_reactions:
        emoji = dict(AnnouncementReaction.REACTION_CHOICES)[reaction.reaction_type]
        recent_activity.append({
            'icon': emoji,
            'title': f'Reacted to "{reaction.announcement.title}"',
            'description': f'In {reaction.announcement.room.room_name}',
            'time': reaction.created_at,
        })
    
    # Recent room joins
    recent_joins = RoomMembership.objects.filter(user=user).order_by('-joined_at')[:3]
    for membership in recent_joins:
        if membership.room.created_by != user:  # Don't include owned rooms
            recent_activity.append({
                'icon': '🚪',
                'title': f'Joined "{membership.room.room_name}"',
                'description': f'As {membership.get_role_display()}',
                'time': membership.joined_at,
            })
    
    # Recent rooms created
    recent_rooms = owned_rooms.order_by('-created_at')[:2]
    for room in recent_rooms:
        recent_activity.append({
            'icon': '🏫',
            'title': f'Created room "{room.room_name}"',
            'description': f'Room code: {room.room_code}',
            'time': room.created_at,
        })
    
    # Sort activity by time and limit to 8 items
    recent_activity.sort(key=lambda x: x['time'], reverse=True)
    recent_activity = recent_activity[:8]
    
    context = {
        'user': user,
        'owned_rooms': owned_rooms,
        'joined_rooms': joined_rooms,
        'owned_rooms_count': owned_rooms_count,
        'joined_rooms_count': joined_rooms_count,
        'announcements_count': announcements_count,
        'reactions_count': reactions_count,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'announcements/account.html', context)


@login_required
def toggle_reaction(request, announcement_id):
    """
    Toggle user's reaction on an announcement.
    
    If user has no reaction, creates a new one with the specified type.
    If user has a reaction of the same type, removes it.
    If user has a different reaction type, updates to the new type.
    
    Args:
        request (HttpRequest): The HTTP request object (must be POST)
        announcement_id (int): ID of the announcement to react to
        
    Returns:
        JsonResponse: Success/error status and reaction counts
        
    POST Parameters:
        reaction_type (str): Type of reaction ('like', 'love', 'laugh', etc.)
        
    Response Format:
        {
            'success': bool,
            'message': str,
            'reaction_counts': {reaction_type: count, ...},
            'user_reaction': str or null
        }
    """
    if request.method == "POST":
        announcement = get_object_or_404(Announcement, id=announcement_id)
        
        # Check if user can access this room
        if not announcement.room.can_access(request.user):
            messages.error(request, "You don't have permission to react to this announcement.")
            return redirect('home')
        
        reaction_type = request.POST.get('reaction_type')
        
        # Check if user already reacted
        existing_reaction = AnnouncementReaction.objects.filter(
            announcement=announcement, 
            user=request.user
        ).first()
        
        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                # Remove reaction if same type
                existing_reaction.delete()
                messages.info(request, "Reaction removed.")
            else:
                # Update reaction if different type
                existing_reaction.reaction_type = reaction_type
                existing_reaction.save()
                messages.success(request, "Reaction updated!")
        else:
            # Create new reaction
            AnnouncementReaction.objects.create(
                announcement=announcement,
                user=request.user,
                reaction_type=reaction_type
            )
            messages.success(request, "Reaction added!")
        
        return redirect('room_detail', room_id=announcement.room.id)
    
    return redirect('home')


@login_required
def delete_announcement(request, announcement_id):
    """
    Delete an announcement from a room.
    
    Only room admins and owners can delete announcements.
    
    Args:
        request (HttpRequest): The HTTP request object
        announcement_id (int): ID of the announcement to delete
        
    Returns:
        HttpResponse: Redirect to room detail page
        
    Permissions:
        - User must be admin or owner of the room
        - Displays appropriate error messages for unauthorized access
    """
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    # Check if user is admin of the room
    if not announcement.room.is_admin(request.user):
        messages.error(request, "You don't have permission to delete this announcement.")
        return redirect('room_detail', room_id=announcement.room.id)
    
    room_id = announcement.room.id
    announcement.delete()
    messages.success(request, "Announcement deleted successfully!")
    return redirect('room_detail', room_id=room_id)


@login_required
def kick_member(request, room_id, user_id):
    """
    Remove a member from a room.
    
    Implements role-based permission system where:
    - Owner can remove anyone except themselves
    - Admin can remove regular members only
    - Members cannot remove anyone
    
    Args:
        request (HttpRequest): The HTTP request object
        room_id (int): ID of the room
        user_id (int): ID of the user to remove
        
    Returns:
        HttpResponse: Redirect to room detail page
        
    Permissions:
        - User must be admin or owner of the room
        - Owner cannot be removed
        - Users cannot remove themselves
        - Only owner can remove admins
    """
    room = get_object_or_404(Room, id=room_id)
    
    # Check if user has admin privileges
    if not room.is_admin(request.user):
        messages.error(request, "You don't have permission to remove members.")
        return redirect('room_detail', room_id=room_id)
    
    # Get the membership to remove
    membership = get_object_or_404(RoomMembership, room=room, user_id=user_id)
    
    # Owner cannot be removed
    if membership.is_owner():
        messages.error(request, "The room owner cannot be removed.")
        return redirect('room_detail', room_id=room_id)
    
    # Users can't remove themselves
    if membership.user == request.user:
        messages.error(request, "You cannot remove yourself from the room.")
        return redirect('room_detail', room_id=room_id)
    
    # Only owner can remove admins
    if membership.is_admin() and not room.is_owner(request.user):
        messages.error(request, "Only the room owner can remove administrators.")
        return redirect('room_detail', room_id=room_id)
    
    username = membership.user.username
    role = membership.get_role_display()
    membership.delete()
    messages.success(request, f"{username} ({role}) has been removed from the room.")
    return redirect('room_detail', room_id=room_id)


@login_required
def promote_user(request, room_id, user_id):
    """
    Promote a regular member to admin role.
    
    Only the room owner can promote users to admin status.
    Admin users gain management privileges but remain below owner level.
    
    Args:
        request (HttpRequest): The HTTP request object
        room_id (int): ID of the room
        user_id (int): ID of the user to promote
        
    Returns:
        HttpResponse: Redirect to room detail page
        
    Permissions:
        - Only room owner can promote users
        - Can only promote members (not existing admins/owner)
        - Updates promotion timestamp and promoting user
    """
    room = get_object_or_404(Room, id=room_id)
    
    # Only owner can promote users
    if not room.is_owner(request.user):
        messages.error(request, "Only the room owner can promote users to admin.")
        return redirect('room_detail', room_id=room_id)
    
    # Get the membership to promote
    membership = get_object_or_404(RoomMembership, room=room, user_id=user_id)
    
    # Can only promote members to admin
    if membership.role != 'member':
        messages.error(request, f"{membership.user.username} is already an admin or owner.")
        return redirect('room_detail', room_id=room_id)
    
    # Promote to admin
    from django.utils import timezone
    membership.role = 'admin'
    membership.promoted_at = timezone.now()
    membership.promoted_by = request.user
    membership.save()
    
    messages.success(request, f"{membership.user.username} has been promoted to admin.")
    return redirect('room_detail', room_id=room_id)


@login_required
def demote_user(request, room_id, user_id):
    """
    Demote an admin user back to regular member.
    
    Only the room owner can demote admin users. Demoted users lose
    management privileges but remain as regular room members.
    
    Args:
        request (HttpRequest): The HTTP request object
        room_id (int): ID of the room
        user_id (int): ID of the user to demote
        
    Returns:
        HttpResponse: Redirect to room detail page
        
    Permissions:
        - Only room owner can demote users
        - Can only demote admins (not members or owner)
        - Clears promotion tracking information
    """
    room = get_object_or_404(Room, id=room_id)
    
    # Only owner can demote users
    if not room.is_owner(request.user):
        messages.error(request, "Only the room owner can demote administrators.")
        return redirect('room_detail', room_id=room_id)
    
    # Get the membership to demote
    membership = get_object_or_404(RoomMembership, room=room, user_id=user_id)
    
    # Cannot demote owner
    if membership.is_owner():
        messages.error(request, "The room owner cannot be demoted.")
        return redirect('room_detail', room_id=room_id)
    
    # Can only demote admins
    if membership.role != 'admin':
        messages.error(request, f"{membership.user.username} is not an admin.")
        return redirect('room_detail', room_id=room_id)
    
    # Demote to member
    membership.role = 'member'
    membership.promoted_at = None
    membership.promoted_by = None
    membership.save()
    
    messages.success(request, f"{membership.user.username} has been demoted to member.")
    return redirect('room_detail', room_id=room_id)


@login_required
def delete_room(request, room_id):
    """
    Delete a room and all associated data.
    
    Only the room owner can delete their room. This action removes:
    - The room itself
    - All memberships
    - All announcements in the room
    - All reactions to those announcements
    
    Args:
        request (HttpRequest): The HTTP request object
        room_id (int): ID of the room to delete
        
    Returns:
        HttpResponse: Redirect to home page
        
    Permissions:
        - Only room owner can delete the room
        - This is a destructive action that cannot be undone
        
    Warning:
        This permanently deletes all room data including announcements
        and member interactions. Use with caution.
    """
    room = get_object_or_404(Room, id=room_id)
    
    # Only owner can delete the room
    if not room.is_owner(request.user):
        messages.error(request, "Only the room owner can delete this room.")
        return redirect('home')
    
    room_name = room.room_name
    room.delete()
    messages.success(request, f"Room '{room_name}' has been deleted successfully!")
    return redirect('home')
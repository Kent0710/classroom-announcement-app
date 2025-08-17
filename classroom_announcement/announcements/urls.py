"""
URL Configuration for Classroom Announcement Application.

This module defines all URL patterns for the announcements app,
mapping URLs to their corresponding view functions.

URL Patterns:
    Authentication & Navigation:
        / - Landing page for anonymous users
        /home/ - User dashboard after login
        /account/ - User profile and statistics page
        /signup/ - User registration
        /signin/ - User authentication
        /logout/ - User logout
    
    Room Management:
        /create-room/ - Create new classroom room
        /join-room/ - Join existing room with code
        /rooms/<id>/ - Room detail view with announcements
        /rooms/<id>/delete/ - Delete room (owner only)
    
    Member Management:
        /rooms/<id>/kick/<user_id>/ - Remove member from room
        /rooms/<id>/promote/<user_id>/ - Promote member to admin
        /rooms/<id>/demote/<user_id>/ - Demote admin to member
    
    Announcement Management:
        /announcements/<id>/react/ - Toggle reaction on announcement
        /announcements/<id>/delete/ - Delete announcement

All URLs require appropriate permissions based on user roles and
room membership status.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication and main pages
    path("", views.landing_page, name="landing_page"),
    path("home/", views.home, name="home"),
    path("account/", views.account, name="account"),
    path("signup/", views.signUp, name="sign_up"),
    path("signin/", views.signIn, name="sign_in"),
    path("logout/", views.logout_view, name="logout"),
    
    # Room management
    path("create-room/", views.create_room, name="create_room"),
    path("join-room/", views.join_room, name="join_room"),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    
    # Member management (admin functions)
    path('rooms/<int:room_id>/kick/<int:user_id>/', views.kick_member, name='kick_member'),
    path('rooms/<int:room_id>/promote/<int:user_id>/', views.promote_user, name='promote_user'),
    path('rooms/<int:room_id>/demote/<int:user_id>/', views.demote_user, name='demote_user'),
    
    # Announcement interactions
    path('announcements/<int:announcement_id>/react/', views.toggle_reaction, name='toggle_reaction'),
    path('announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
]

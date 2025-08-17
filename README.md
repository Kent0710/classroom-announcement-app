# Classroom Announcement Application

A comprehensive Django-based web application for managing classroom announcements with multi-level user roles, real-time interactions, and a modern glassmorphism UI design.

## 🌟 Features

### Core Functionality
- **Room Management**: Create and manage classroom rooms with unique 6-character codes
- **Multi-Level Roles**: Owner, Admin, and Member hierarchy with appropriate permissions
- **Announcements**: Post, view, and interact with classroom announcements
- **Reaction System**: Express reactions to announcements with emoji-based feedback
- **User Accounts**: Comprehensive user profiles with statistics and activity tracking

### User Roles & Permissions

#### 🏆 Owner (Room Creator)
- Full control over the room
- Promote/demote members to/from admin status
- Remove any member from the room
- Delete the entire room
- All admin and member privileges

#### ⭐ Admin (Promoted by Owner)
- Manage regular members (kick only)
- Delete announcements
- Post announcements
- All member privileges

#### 👤 Member (Regular User)
- View room content and announcements
- Post new announcements
- React to announcements
- View member list

### Technical Features
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Glassmorphism UI**: Modern, translucent design with backdrop blur effects
- **Real-time Reactions**: Dynamic emoji reaction system
- **Activity Tracking**: Comprehensive user activity monitoring
- **Secure Access**: Role-based permission system with proper validation

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.0+
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd classroom-announcement-app
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django
   ```

4. **Database Setup**
   ```bash
   cd classroom_announcement
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access Application**
   - Open your browser and navigate to `http://127.0.0.1:8000`

## 📱 Usage Guide

### Getting Started
1. **Sign Up**: Create a new account on the landing page
2. **Create Room**: Use the "Create Room" button to establish a classroom
3. **Share Code**: Provide the 6-character room code to students
4. **Manage**: Use admin controls to manage members and content

### For Students
1. **Join Room**: Use the "Join Room" feature with the code provided by your teacher
2. **View Content**: Access announcements and participate in discussions
3. **React**: Express your thoughts using the emoji reaction system

### For Teachers/Admins
1. **Post Announcements**: Share important information with your class
2. **Manage Members**: Promote trusted students to admin status
3. **Moderate Content**: Remove inappropriate announcements or members
4. **Track Activity**: Monitor engagement through the account dashboard

## 🛠️ Project Structure

```
classroom_announcement/
├── manage.py                          # Django management script
├── db.sqlite3                        # SQLite database
├── classroom_announcement/           # Main project settings
│   ├── __init__.py
│   ├── settings.py                   # Django configuration
│   ├── urls.py                       # Main URL routing
│   ├── wsgi.py                       # WSGI configuration
│   └── asgi.py                       # ASGI configuration
└── announcements/                    # Main application
    ├── models.py                     # Database models
    ├── views.py                      # View functions
    ├── forms.py                      # Form definitions
    ├── urls.py                       # App URL patterns
    ├── admin.py                      # Admin interface
    ├── apps.py                       # App configuration
    ├── migrations/                   # Database migrations
    ├── static/announcements/         # CSS and static files
    └── templates/announcements/      # HTML templates
```

## 📊 Database Models

### Room Model
- **room_name**: Unique name for the classroom
- **room_code**: 6-character unique identifier
- **created_by**: Room owner (Foreign Key to User)
- **created_at/updated_at**: Timestamps

### RoomMembership Model
- **room**: Foreign Key to Room
- **user**: Foreign Key to User
- **role**: 'owner', 'admin', or 'member'
- **joined_at**: Join timestamp
- **promoted_at/promoted_by**: Promotion tracking

### Announcement Model
- **room**: Foreign Key to Room
- **author**: Foreign Key to User
- **title**: Announcement title
- **content**: Announcement body
- **created_at/updated_at**: Timestamps

### AnnouncementReaction Model
- **announcement**: Foreign Key to Announcement
- **user**: Foreign Key to User
- **reaction_type**: Emoji reaction type
- **created_at**: Reaction timestamp

## 🎨 Design System

### Color Scheme
- **Primary**: Green gradient (#4a956b to #5ba872)
- **Secondary**: Blue tones for contrast
- **Background**: Soft gradients with transparency
- **Text**: Dark grays for readability

### Typography
- Clean, modern fonts optimized for readability
- Hierarchical sizing for content organization
- Consistent spacing and line heights

### UI Components
- **Glassmorphism Cards**: Translucent panels with backdrop blur
- **Gradient Buttons**: Interactive elements with hover effects
- **Responsive Grids**: Flexible layouts for all screen sizes
- **Icon System**: Consistent emoji and symbol usage

## 🔧 API Endpoints

### Authentication
- `GET /` - Landing page
- `GET /signup/` - User registration form
- `POST /signup/` - Process registration
- `GET /signin/` - Login form
- `POST /signin/` - Process login
- `GET /logout/` - User logout

### Room Management
- `GET /home/` - User dashboard
- `GET /create-room/` - Room creation form
- `POST /create-room/` - Process room creation
- `GET /join-room/` - Join room form
- `POST /join-room/` - Process room joining
- `GET /rooms/<id>/` - Room detail view
- `POST /rooms/<id>/delete/` - Delete room

### Member Management
- `POST /rooms/<id>/kick/<user_id>/` - Remove member
- `POST /rooms/<id>/promote/<user_id>/` - Promote to admin
- `POST /rooms/<id>/demote/<user_id>/` - Demote to member

### Announcements & Reactions
- `POST /announcements/<id>/react/` - Toggle reaction
- `POST /announcements/<id>/delete/` - Delete announcement

### User Account
- `GET /account/` - User profile and statistics

## 🧪 Testing

### Manual Testing Checklist
- [ ] User registration and authentication
- [ ] Room creation with unique codes
- [ ] Room joining with valid/invalid codes
- [ ] Announcement posting and deletion
- [ ] Reaction system functionality
- [ ] Member management (kick, promote, demote)
- [ ] Permission-based access control
- [ ] Responsive design on various devices

### Automated Testing
To run tests (when implemented):
```bash
python manage.py test
```

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Set DEBUG=False and configure SECRET_KEY
2. **Database**: Consider PostgreSQL for production
3. **Static Files**: Configure static file serving
4. **Security**: Enable HTTPS and security headers
5. **Performance**: Add caching and optimize queries

### Deployment Steps
1. Configure production settings
2. Set up production database
3. Collect static files: `python manage.py collectstatic`
4. Deploy to hosting platform (Heroku, AWS, etc.)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Maintain consistent HTML/CSS formatting
- Comment complex logic and algorithms

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django framework for the robust backend
- Modern CSS techniques for the glassmorphism design
- Open source community for inspiration and resources

## 📞 Support

For support, questions, or feature requests:
- Create an issue in the repository
- Contact the development team
- Check the documentation and code comments

---

**Classroom Announcement Application** - Enhancing educational communication through modern web technology.

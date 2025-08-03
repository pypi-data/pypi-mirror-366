# Django Notification Manager (dj_notif)

[![PyPI version](https://badge.fury.io/py/dj-notif.svg)](https://badge.fury.io/py/dj-notif)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2+](https://img.shields.io/badge/django-5.2+-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Beta](https://img.shields.io/badge/Status-Beta-orange.svg)](https://github.com/Hexoder/DjangoNotification)

> ⚠️ **BETA VERSION** - This package is currently in beta. While functional, it may have breaking changes in future releases. Please test thoroughly in your development environment before using in production.



A comprehensive Django package for managing notifications with automatic dispatching and category-based organization.

## Features

- 🔔 **Real-time Notifications**: WebSocket-based instant notification delivery (live delivery active, management methods coming soon)
- 📱 **Category-based Organization**: Group notifications by type (task assignments, comments, etc.)
- 📢 **Broadcast Notifications**: Send notifications to all users with read tracking
- 🔐 **JWT Authentication**: Secure connections with JWT tokens
- 📊 **REST API**: Complete REST API for notification management
- 🎯 **Automatic Dispatching**: Notifications are automatically sent when models are saved
- 📝 **Read/Unread Tracking**: Mark notifications as read individually or by category
- 🔄 **Soft Delete**: Built-in soft delete functionality for data integrity
- 🎨 **Customizable**: Easy to extend with custom notification types

## Installation

### 1. Install the Package

```bash
pip install dj_notif
```

### 2. Add to Django Settings

Add `dj_notif` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'dj_notif',
]
```

### 3. Configure Channels

Add the following to your Django settings for WebSocket notification delivery:

```python
# Channels Configuration
ASGI_APPLICATION = 'your_project.asgi.application'

# Channel Layers (Redis backend recommended for production)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# JWT Settings for Authentication
CHANNEL_LAYERS_JWT_SECRET = 'your-secret-key'
```

### 4. Update ASGI Configuration

Update your `asgi.py` file to include the notification routing for WebSocket delivery:

```python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django_channels_jwt.middleware import JwtAuthMiddlewareStack
from dj_notif.routes import notification_urlpatterns

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(
            notification_urlpatterns  # Add your other URL patterns here
        ),
    ),
})
```

### 5. Include URLs

Add the notification URLs to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URL patterns
    path('api/', include('dj_notif.urls')),
]
```

The package provides the following URL endpoints:

**User Notifications:**
- `/api/notifications/user/` - Get all user notifications
- `/api/notifications/user/categories/` - Get unread count by category
- `/api/notifications/user/mark_all_as_read/` - Mark all user notifications as read
- `/api/notifications/user/category/{category}/` - Get user notifications by category
- `/api/notifications/user/category/{category}/mark_all_read` - Mark all user notifications in category as read
- `/api/notifications/user/category/{category}/mark_read/{id}/` - Mark specific user notification as read

**Broadcast Notifications:**
- `/api/notifications/broadcast/` - Get all broadcast notifications
- `/api/notifications/broadcast/category/{category}/` - Get broadcast notifications by category
- `/api/notifications/broadcast/category/{category}/mark_read/{id}/` - Mark specific broadcast notification as read

**WebSocket:**
- `/api/notifications/ws_auth/` - WebSocket authentication endpoint (requires authentication, returns UUID)

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Register Custom Notification Models and Serializers

The package automatically discovers notification models and serializers. Ensure your custom notification models and serializers are properly imported in your Django app's `__init__.py` or `apps.py`:

```python
# In your app's apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app'

    def ready(self):
        # Import your notification models and serializers to register them
        from .notifications import models, serializers
```

Or in your app's `__init__.py`:

```python
# In your app's __init__.py
default_app_config = 'your_app.apps.YourAppConfig'
```

#### How Auto-Discovery Works

The package uses Django's app registry to automatically discover:

1. **Notification Models**: All classes inheriting from `BaseNotificationModel`
2. **Notification Serializers**: All classes inheriting from `BaseNotificationSerializer`

The discovery happens when Django starts up and loads all apps. Each model and serializer must have a `notification_class_name` attribute that matches between the model and its corresponding serializer.

**Important**: Make sure your notification models and serializers are imported when Django starts, otherwise they won't be discovered by the package.

## Usage

### 1. Create Custom Notification Models

Create notification models by inheriting from `BaseNotificationModel`. You can define related models using either `PositiveIntegerField` (simple ID reference) or `ForeignKey` (full relationship). This example uses ForeignKey for better relationship management:

```python
from django.db import models
from dj_notif.models import BaseNotificationModel
from your_app.models import Task

class TaskNotification(BaseNotificationModel):
    class NotificationTitle(models.TextChoices):
        created = 'task_created'
        updated = 'task_updated'
        completed = 'task_completed'

    user = models.ForeignKey(User, related_name='task_notifications', on_delete=models.CASCADE)
    title = models.CharField(choices=NotificationTitle.choices, max_length=20)
    task = models.ForeignKey(Task, related_name='notifications', on_delete=models.SET_NULL)

    notification_class_name = 'task'  # Required!
```

### 2. Create Custom Serializers

Create serializers by inheriting from `BaseNotificationSerializer`:

```python
from dj_notif.serializers import BaseNotificationSerializer
from your_app.serializers import TaskSerializer

class TaskNotificationSerializer(BaseNotificationSerializer):
    notification_class_name = 'task'  # Must match model
    task = TaskSerializer(fields=['id', 'name'])

    class Meta:
        model = TaskNotification
        extra_fields = ['user', 'task', 'requested_user']
```

#### Broadcast Notification Serializers

For broadcast notifications, inherit from `BaseBroadcastNotificationSerializer`:

```python
from dj_notif.serializers import BaseBroadcastNotificationSerializer

class BroadcastNotificationSerializer(BaseBroadcastNotificationSerializer):
    notification_class_name = 'broadcast'  # Must match model

    class Meta:
        model = BroadcastNotification
        # No extra_fields needed for broadcast notifications
```

### 3. Using Notifications in Your Code

#### Creating Notifications

```python
# Single notification
TaskNotification.objects.create(
    user=user,
    title=TaskNotification.NotificationTitle.created,
    description=f'Task {task.name} has been created',
    level=1,  # 1=low, 2=medium, 3=high
    task=task
)

# Multiple notifications at once
TaskNotification.create_notifications(
    title='New Project Available',
    description='A new project has been created',
    level=2,
    users=[1, 2, 3, 4]  # List of user IDs
)

# Broadcast notifications (sent to all users)
BroadcastNotification.objects.create(
    title=BroadcastNotification.NotificationTitle.system_notification,
    description='System maintenance scheduled for tomorrow',
    level=2
)
```

#### Using in Your Views or Services

```python
# In your views.py or services
def create_task_notification(user_id, task, action):
    """Create a notification when a task is created, updated, or completed"""
    title_map = {
        'created': TaskNotification.NotificationTitle.created,
        'updated': TaskNotification.NotificationTitle.updated,
        'completed': TaskNotification.NotificationTitle.completed,
    }
    
    TaskNotification.objects.create(
        user=user_id,
        title=title_map[action],
        description=f'Task {task.name} has been {action}',
        level=1,
        task=task
    )

# Usage example
create_task_notification(
    user_id=user,
    task=task,
    action='created'
)
```

### 4. WebSocket Live Delivery

Notifications are automatically delivered via WebSocket when they are created. To connect to the WebSocket, you need to follow a two-step authentication process:

#### Step 1: Get WebSocket Authentication UUID

First, make a GET request to the `ws_auth` endpoint to get a UUID:

```javascript
// Get WebSocket authentication UUID
async function getWsAuthUuid() {
    const response = await fetch('/api/notifications/ws_auth/', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer your-jwt-token',
            'Content-Type': 'application/json',
        },
    });
    
    if (response.ok) {
        const data = await response.json();
        return data.uuid; // UUID for WebSocket connection
    } else {
        throw new Error('Failed to get WebSocket auth UUID');
    }
}
```

#### Step 2: Connect to WebSocket with UUID

Use the UUID as a query parameter when connecting to the WebSocket:

```javascript
// Connect to WebSocket with authentication UUID
async function connectToWebSocket() {
    try {
        // Get authentication UUID
        const uuid = await getWsAuthUuid();
        
        // Connect to WebSocket with UUID
        const ws = new WebSocket(`ws://localhost:8000/ws/notifications/?uuid=${uuid}`);
        
        ws.onopen = function() {
            console.log('WebSocket connected successfully');
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('New notification:', data);
            
            if (data.type === 'notifications') {
                // Handle notification data
                const notification = data.payload.notification;
                // Update UI, show toast, etc.
            }
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = function() {
            console.log('WebSocket connection closed');
        };
        
        return ws;
    } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
    }
}

// Usage
const wsConnection = connectToWebSocket();
```

**Note**: WebSocket methods for getting notifications and marking them as read are not yet implemented. Use the REST API endpoints for these operations.

#### Authentication Requirements

- The `ws_auth` endpoint requires `IsAuthenticated` permission
- You must include your JWT token in the Authorization header
- The returned UUID is valid for a limited time
- Use the UUID as a query parameter when connecting to the WebSocket

## Supported Notification Types

The package supports various notification types. Here are examples using ForeignKey relationships:

### Task Notifications
```python
from your_app.models import Task

class TaskNotification(BaseNotificationModel):
    class NotificationTitle(models.TextChoices):
        created = 'task_created'
        updated = 'task_updated'
        completed = 'task_completed'
    
    user = models.ForeignKey(User, related_name='task_notifications', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL)
    notification_class_name = 'task'
```

### Comment Notifications
```python
from your_app.models import Comment

class CommentNotification(BaseNotificationModel):
    class NotificationTitle(models.TextChoices):
        mention = 'mention'
        reply = 'reply'
    
    user = models.ForeignKey(User, related_name='comment_notifications', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL)
    notification_class_name = 'comment'
```

### Custom Notifications
```python
class CustomNotification(BaseNotificationModel):
    class NotificationTitle(models.TextChoices):
        info = 'info'
        warning = 'warning'
        error = 'error'
    
    user = models.ForeignKey(User, related_name='custom_notifications', on_delete=models.CASCADE)
    custom_data = models.JSONField(default=dict)  # Any additional data
    notification_class_name = 'custom'
```

### Broadcast Notifications
```python
class BroadcastNotification(BaseBroadcastNotificationModel):
    class NotificationTitle(models.TextChoices):
        system_notification = 'system_notification'
        admin_notification = 'admin_notification'
    
    title = models.CharField(choices=NotificationTitle.choices, max_length=50)
    description = models.CharField(max_length=200)
    level = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])
    # user_read_at_receipts field is automatically handled by BaseBroadcastNotificationModel
    notification_class_name = 'broadcast'
```

## API Endpoints

### REST API

The package provides two types of notification endpoints:

#### User Notifications
User-specific notifications that are sent to individual users. These notifications are tied to specific users and can be marked as read by the intended recipient.

#### Broadcast Notifications  
System-wide notifications that are sent to all users. These notifications use a `user_read_at_receipts` JSON field to track which users have read them, allowing multiple users to mark the same notification as read.

| Endpoint                                     | Method | Description |
|----------------------------------------------|--------|-------------|
| `/api/notifications/user/`                   | GET    | Get all user notifications for authenticated user |
| `/api/notifications/user/categories/`        | GET    | Get unread count by category for user notifications |
| `/api/notifications/user/mark_all_as_read/`  | POST   | Mark all user notifications as read |
| `/api/notifications/user/category/{category}/` | GET    | Get user notifications by category |
| `/api/notifications/user/category/{category}/mark_all_read` | POST   | Mark all user notifications in category as read |
| `/api/notifications/user/category/{category}/mark_read/{id}/` | POST   | Mark specific user notification as read |
| `/api/notifications/broadcast/`              | GET    | Get all broadcast notifications for authenticated user |
| `/api/notifications/broadcast/category/{category}/` | GET    | Get broadcast notifications by category |
| `/api/notifications/broadcast/category/{category}/mark_read/{id}/` | POST   | Mark specific broadcast notification as read |
| `/api/notifications/ws_auth/`                | GET    | WebSocket authentication endpoint |


### WebSocket Live Delivery

Notifications are automatically sent to connected clients when they are created. The WebSocket connection receives notifications in real-time without needing to send commands.

**Note**: WebSocket commands for getting notifications and marking them as read are not yet implemented. Use the REST API for these operations.

### API Usage Examples

#### User Notifications
```javascript
// Get all user notifications
const response = await fetch('/api/notifications/user/', {
    headers: { 'Authorization': 'Bearer your-jwt-token' }
});

// Get unread count by category
const categories = await fetch('/api/notifications/user/categories/', {
    headers: { 'Authorization': 'Bearer your-jwt-token' }
});

// Mark specific notification as read
await fetch('/api/notifications/user/category/task/mark_read/123/', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer your-jwt-token' }
});
```

#### Broadcast Notifications
```javascript
// Get all broadcast notifications
const response = await fetch('/api/notifications/broadcast/', {
    headers: { 'Authorization': 'Bearer your-jwt-token' }
});

// Get broadcast notifications by category
const systemNotifs = await fetch('/api/notifications/broadcast/category/pm_broadcast/', {
    headers: { 'Authorization': 'Bearer your-jwt-token' }
});

// Mark broadcast notification as read (for current user)
await fetch('/api/notifications/broadcast/category/pm_broadcast/mark_read/456/', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer your-jwt-token' }
});
```

## Configuration Options

### Notification Levels

```python
class NotificationLevel(models.IntegerChoices):
    low = 1
    medium = 2
    high = 3
```

### Channel Name Format

Notifications are sent to channels in the format: `notif_user_{user_id}`

## Dependencies

- Django >= 5.2
- Django REST Framework >= 3.15.2
- Django Channels >= 4.2.0
- django-channels-jwt >= 0.0.3
- Redis (for channel layers)

## Example Project Structure

```
your_project/
├── apps/
│   └── your_app/
│       ├── notifications/
│       │   ├── __init__.py
│       │   ├── models.py      # Custom notification models
│       │   └── serializers.py # Custom notification serializers
│       ├── models.py          # Your main models
│       ├── signals.py         # Django signals for notifications
│       ├── apps.py            # App configuration
│       └── __init__.py
├── your_project/
│   ├── asgi.py               # ASGI configuration with WebSocket routing
│   ├── settings.py           # Django settings with channels config
│   └── urls.py               # URL configuration
└── manage.py
```

### Recommended File Organization

1. **Create a `notifications/` subdirectory** in each app that needs notifications
2. **Place notification models** in `notifications/models.py`
3. **Place notification serializers** in `notifications/serializers.py`
4. **Import notifications** in your app's `apps.py` or `__init__.py`
5. **Use signals** in your main app's `signals.py` to trigger notifications

### Example App Structure

```python
# apps/your_app/notifications/__init__.py
# This file can be empty, but ensures the directory is a Python package

# apps/your_app/notifications/models.py
from dj_notif.models import BaseNotificationModel

class YourNotification(BaseNotificationModel):
    # Your notification model definition
    pass

# apps/your_app/notifications/serializers.py
from dj_notif.serializers import BaseNotificationSerializer

class YourNotificationSerializer(BaseNotificationSerializer):
    # Your notification serializer definition
    pass

# apps/your_app/apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app'

    def ready(self):
        # Import to register notifications
        from .notifications import models, serializers
        from . import signals  # Import signals to register them
```

## Best Practices

### 1. Notification Naming Conventions

- Use descriptive names for notification classes: `TaskAssignmentNotification`, `CommentMentionNotification`
- Use consistent naming for `notification_class_name`: lowercase with underscores
- Group related notifications in the same model with different titles

### 2. Signal Organization

- Keep signal handlers focused and lightweight
- Use transaction management for critical operations
- Handle exceptions gracefully to prevent signal failures
- Consider using `@receiver` decorators with `dispatch_uid` for unique signal handlers

### 3. Performance Considerations

- Use `bulk_create()` for multiple notifications when possible
- Consider using `select_related()` and `prefetch_related()` in serializers
- Implement pagination for notification lists
- Use database indexes on frequently queried fields

### 4. Security Best Practices

- Always validate user permissions before creating notifications
- Use proper authentication for WebSocket connections
- Sanitize notification content to prevent XSS attacks
- Implement rate limiting for notification creation

### 5. Testing Notifications

```python
from django.test import TestCase
from your_app.notifications.models import TaskNotification

class NotificationTestCase(TestCase):
    def setUp(self):
        self.user_id = 1  # Simple user ID
    
    def test_notification_creation(self):
        notification = TaskNotification.objects.create(
            user=self.user_id,
            title='task_created',
            description='Test notification',
            level=1,
            task_id=123
        )
        self.assertEqual(notification.user, self.user_id)
        self.assertEqual(notification.title, 'task_created')
        self.assertEqual(notification.task_id, 123)
    
    def test_notification_dispatch(self):
        # Test that notifications are dispatched when saved
        with self.assertNumQueries(1):  # Adjust based on your setup
            notification = TaskNotification.objects.create(
                user=self.user_id,
                title='task_created',
                description='Test notification',
                level=1,
                task_id=123
            )
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Fails**
   - Ensure Redis is running
   - Check JWT token validity
   - Verify ASGI configuration

2. **Notifications Not Sending**
   - Check channel layer configuration
   - Ensure `notification_class_name` is set in models
   - Verify serializer registration

3. **Migration Errors**
   - Run `python manage.py makemigrations dj_notif`
   - Ensure all custom notification models are in `INSTALLED_APPS`

### Debug Mode

Enable debug logging in settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'notification': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Deployment

### Production Considerations

1. **Redis Configuration**
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('your-redis-host', 6379)],
               "capacity": 1500,  # Maximum number of messages in a channel
               "expiry": 10,      # Message expiry in seconds
           },
       },
   }
   ```

2. **ASGI Server**
   - Use Daphne or Uvicorn for production
   - Configure proper worker processes
   - Set up load balancing for WebSocket connections

3. **Security**
   - Use HTTPS/WSS in production
   - Configure proper CORS settings
   - Implement rate limiting
   - Use secure JWT secrets

4. **Monitoring**
   - Monitor Redis memory usage
   - Track WebSocket connection counts
   - Set up alerts for notification failures
   - Log notification delivery rates

### Docker Deployment

```dockerfile
# Example Dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Option 1: Using Daphne (ASGI server for WebSocket support)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "your_project.asgi:application"]

# Option 2: Using Gunicorn with Uvicorn (ASGI server for WebSocket support)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "your_project.asgi:application"]
```

### Environment Variables

```bash
# Required environment variables
REDIS_URL=redis://your-redis-host:6379
CHANNEL_LAYERS_JWT_SECRET=your-secret-key
DJANGO_SECRET_KEY=your-django-secret

# Optional
REDIS_CAPACITY=1500
REDIS_EXPIRY=10
```

## Migration and Upgrades

### Upgrading from Previous Versions

When upgrading the package, follow these steps:

1. **Backup your database** before running migrations
2. **Update the package**: `pip install --upgrade dj_notif`
3. **Run migrations**: `python manage.py migrate`
4. **Test your notification system** thoroughly
5. **Update your code** if any breaking changes are introduced

### Breaking Changes

Check the [CHANGELOG.md](CHANGELOG.md) file for detailed information about breaking changes between versions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/dj_notif.git
cd dj_notif

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .
pip install -r requirements-dev.txt

# Run tests
python manage.py test dj_notif
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository or contact the maintainer.

## Changelog

### Version 0.2.0 (Latest)
- ✨ **Broadcast Notifications**: Added support for system-wide notifications sent to all users
- 🔄 **Separate ViewSets**: Split user notifications and broadcast notifications into separate ViewSets
- 📊 **Enhanced API Structure**: Reorganized API endpoints with `/user/` and `/broadcast/` prefixes
- 🎯 **Multi-user Read Tracking**: Broadcast notifications use `user_read_at_receipts` JSON field for read status
- 🔧 **Improved URL Routing**: Better organized URL structure for different notification types
- 📝 **BaseBroadcastNotificationModel**: New base model for broadcast notifications
- 📝 **BaseBroadcastNotificationSerializer**: New base serializer for broadcast notifications
- 🚀 **Auto-discovery Support**: Broadcast notifications work with the existing auto-discovery system

### Version 0.1.0
- 🎉 **Initial release**
- 🔔 **WebSocket-based real-time notifications**: Live notification delivery via WebSocket connections
- 📊 **REST API for notification management**: Complete CRUD operations for notifications
- 🔐 **JWT authentication support**: Secure authentication for both REST API and WebSocket connections
- ⚡ **Automatic notification dispatching**: Notifications are automatically sent when models are saved
- 📱 **Category-based notification organization**: Group notifications by type (task assignments, comments, etc.)
- 🔄 **Soft delete functionality**: Built-in soft delete for data integrity
- 🎨 **Customizable notification types**: Easy to extend with custom notification models and serializers
- 🔍 **Auto-discovery system**: Automatic discovery of notification models and serializers
- 📈 **Read/unread tracking**: Mark notifications as read individually or by category
- 🌐 **WebSocket authentication**: Secure WebSocket connections with JWT token validation

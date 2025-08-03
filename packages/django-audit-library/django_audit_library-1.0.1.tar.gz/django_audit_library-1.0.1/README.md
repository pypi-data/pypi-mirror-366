# Django Audit Library

A comprehensive Django audit logging library that provides automatic tracking of model changes, user actions, login attempts, data exports, and system events.

## Features

- **Automatic Model Tracking**: Automatically logs CREATE, UPDATE, and DELETE operations on all Django models
- **User Authentication Tracking**: Logs login/logout attempts and failures
- **Data Export Auditing**: Tracks data exports with metadata
- **System Event Logging**: Captures system errors, warnings, and performance issues
- **Security Monitoring**: Detects suspicious requests and activities
- **Admin Interface**: Beautiful Django admin interface for viewing audit logs
- **Thread-Safe**: Uses thread-local storage for request context
- **Migration-Safe**: Automatically detects and skips logging during migrations

## Installation

1. Install the package:
```bash
pip install django-audit-library
```

2. Add `audit` to your `INSTALLED_APPS` in Django settings:
```python
INSTALLED_APPS = [
    # ... your other apps
    'audit',
]
```

3. Add the audit middleware to your `MIDDLEWARE` setting:
```python
MIDDLEWARE = [
    # ... your other middleware
    'audit.middleware.AuditMiddleware',
    'audit.middleware.SecurityAuditMiddleware',  # Optional: for security monitoring
]
```

4. Run migrations:
```bash
python manage.py migrate audit
```

## Usage

### Automatic Logging

Once installed and configured, the library will automatically start logging:

- Model changes (create, update, delete)
- User login/logout events
- Failed login attempts
- System errors and exceptions

### Manual Logging

You can also manually log events using the utility functions:

```python
from audit.utils import log_audit_event, log_system_event, log_data_export

# Log a custom audit event
log_audit_event(
    user=request.user,
    action='CUSTOM_ACTION',
    content_object=some_model_instance,
    changes={'field': 'new_value'},
    reason='Custom reason',
    request=request
)

# Log a system event
log_system_event(
    event_type='INFO',
    title='Custom Event',
    description='Something important happened',
    user=request.user,
    request=request
)

# Log a data export
log_data_export(
    user=request.user,
    export_type='User Data',
    file_format='CSV',
    record_count=100,
    file_size=1024,
    filters={'active': True},
    request=request
)
```

### Using the Audit Mixin

For class-based views, you can use the `AuditMixin`:

```python
from audit.utils import AuditMixin
from django.views.generic import DetailView

class MyDetailView(AuditMixin, DetailView):
    model = MyModel
    
    def get_object(self):
        obj = super().get_object()
        self.log_view_access(self.request, obj)
        return obj
```

### Getting Audit Summaries

```python
from audit.utils import get_audit_summary

# Get system-wide summary for last 30 days
summary = get_audit_summary(days=30)

# Get summary for specific user
summary = get_audit_summary(user=request.user, days=7)
```

## Models

The library provides several models for different types of audit data:

### AuditLog
Tracks all model changes and user actions with:
- User who performed the action
- Action type (CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT, etc.)
- Object being modified (using generic foreign keys)
- Before/after values for changes
- IP address, user agent, session information
- Timestamp and additional metadata

### LoginAttempt
Tracks authentication attempts with:
- Username and status (SUCCESS, FAILED, BLOCKED)
- IP address and user agent
- Geographic information (optional)
- Failure reasons

### DataExport
Tracks data exports with:
- User and export type
- File format and size
- Record count and filters applied
- Download tracking

### SystemEvent
Tracks system-level events with:
- Event type (ERROR, WARNING, INFO, SECURITY, PERFORMANCE)
- Technical details (module, function, line number)
- Error codes and stack traces
- Resolution tracking

## Admin Interface

The library provides a comprehensive Django admin interface with:

- Read-only views for all audit data
- Advanced filtering and searching
- Formatted display of changes and technical details
- Date hierarchies for easy navigation
- Proper permissions (only superusers can delete)

## Configuration

### Settings

You can customize the behavior with these optional settings:

```python
# In your Django settings.py

# Skip auditing for specific models
AUDIT_SKIP_MODELS = [
    'auth.Session',
    'contenttypes.ContentType',
]

# Skip auditing for specific actions
AUDIT_SKIP_ACTIONS = ['VIEW']

# Custom user model (if you're using one)
AUTH_USER_MODEL = 'your_app.CustomUser'
```

### Middleware Options

The library includes two middleware classes:

1. **AuditMiddleware**: Core functionality for request tracking
2. **SecurityAuditMiddleware**: Additional security monitoring (optional)

## Performance Considerations

- The library uses efficient database queries and indexing
- Thread-local storage minimizes performance impact
- Automatic migration detection prevents issues during deployments
- Configurable to skip certain models or actions if needed

## Security Features

- Tracks suspicious request patterns
- Monitors unusual user agents
- Logs slow requests for performance monitoring
- Captures and logs system exceptions
- Geographic tracking for login attempts (optional)

## Requirements

- Django 3.2+
- Python 3.8+

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
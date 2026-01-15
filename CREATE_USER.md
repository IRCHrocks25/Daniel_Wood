# Creating a User Account

Since you're using DATABASE_URL, you need to create a user account in that database.

## Option 1: Use Django Admin (Recommended)

1. First, make sure the admin user exists:
   ```bash
   python manage.py seed_data
   ```
   This creates an admin user with:
   - Username: `admin`
   - Password: `admin123`

2. Log in to Django admin at `/admin/` with those credentials

3. Create a new user from the admin panel:
   - Go to "Users" → "Add user"
   - Enter username and password
   - Save and continue
   - Set permissions if needed

## Option 2: Create User via Django Shell

```bash
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import User

# Create a regular user
user = User.objects.create_user(
    username='your_username',
    email='your_email@example.com',
    password='your_password'
)
user.save()
print(f"User {user.username} created successfully!")

# Or create a superuser
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)
print(f"Admin user {admin.username} created!")
```

## Option 3: Use the Seed Command

The seed command automatically creates an admin user:
```bash
python manage.py seed_data
```

Then log in with:
- Username: `admin`
- Password: `admin123`

## Troubleshooting

If login still doesn't work:
1. Check if the user exists: `User.objects.filter(username='your_username').exists()`
2. Check if user is active: `User.objects.get(username='your_username').is_active`
3. Reset password: `user.set_password('new_password')` then `user.save()`


import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import PasswordResetCode
from django.contrib.auth import authenticate

print("--- Testing Password Reset Backend Logic ---")

# Clean up any existing test user
User.objects.filter(username='test_cradle_user').delete()

# Create test user
user = User.objects.create_user(username='test_cradle_user', email='test@cradle.com', password='old_password')
print(f"Created user: {user.username} with email {user.email}")

# Generate reset code
reset_code = PasswordResetCode.generate_code(user)
print(f"Generated Password Reset Code: {reset_code.code}")

# Validate code
print(f"Code is valid (time-check): {reset_code.is_valid()}")

# Perform the reset action
user.set_password('new_secure_password')
user.save()
reset_code.delete()
print("Password updated and reset code deleted.")

# Verify authentication with new password
auth_success = authenticate(username='test_cradle_user', password='new_secure_password')
print(f"Authentication with new password successful: {auth_success is not None}")

if auth_success:
    print("ALL TESTS PASSED SUCCESSFULLY.")
else:
    print("TEST FAILED.")

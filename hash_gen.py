# hash_gen.py
from app.core.security import get_password_hash  # Adjust this import to wherever your hash function sits

print(get_password_hash("AdminPassword123!"))
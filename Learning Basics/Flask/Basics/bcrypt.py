import bcrypt
def hash_password(password):
    # Convert the password to bytes
    password_bytes = password.encode('utf-8')

    # Generate a random salt
    salt = bcrypt.gensalt()

    # Hash the password
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    return hashed_password

def check_password(password, hashed_password):
    # Convert the password to bytes
    password_bytes = password.encode('utf-8')

    # Check if the provided password matches the stored hash
    return bcrypt.checkpw(password_bytes, hashed_password)

# Example usage:
if __name__ == "__main__":
    user_password = "password"
    stored_hash = hash_password(user_password)

    # Simulate user login
    entered_password = input("Enter your password: ")
    if check_password(entered_password, stored_hash):
        print("Access granted! Welcome.")
    else:
        print("Access denied! Incorrect password.")


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password_raw(plain_password, password_hash):
    # This is used for comparison where plain password is provided and hashed.
    # It doesn't verify against an existing hash, but hashes the input and returns it.
    # This should ONLY be used for testing purposes where the plain text password is known.
    return pwd_context.hash(plain_password) == password_hash


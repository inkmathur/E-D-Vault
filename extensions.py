
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Shared rate limiter for the application.
# In-memory storage is intended for local development.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
    strategy="fixed-window"
)

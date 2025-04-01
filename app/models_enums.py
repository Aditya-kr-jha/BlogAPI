from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    author = "author"
    reader = "reader"

class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"
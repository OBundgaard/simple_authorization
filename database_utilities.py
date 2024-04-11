import hashlib
from datetime import datetime

import jwt


class User:
    def __init__(self, user_id: int, username: str, password_hash: str, role_id: int = 0):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role_id = role_id


class Article:
    def __init__(self, article_id: int, title: str, content: str, author_id: int, created_at: datetime):
        self.article_id = article_id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.created_at = created_at


class Comment:
    def __init__(self, comment_id: int, content: str, article_id: int, user_id: int, created_at: datetime):
        self.comment_id = comment_id
        self.content = content
        self.article_id = article_id
        self.user_id = user_id
        self.created_at = created_at


def validate_jwt_token(token: str) -> dict:
    """
    A method to validate a JWT token
    :param token: the token.
    :return: The contents of the token
    """

    try:
        decoded_token = jwt.decode(token, 'secret', algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return {}
    except jwt.InvalidTokenError:
        return {}


def hash_string(value: str) -> str:
    """
    Hashes a string using SHA256 w/ provided salt
    :param value: The string we want to hash
    :return: A hashed string
    """

    # Set up algorithm
    hash_object = hashlib.sha256()

    # Hash the string
    hash_object.update(value.encode())
    return hash_object.hexdigest()

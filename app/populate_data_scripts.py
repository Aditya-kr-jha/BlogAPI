from typing import Dict, Tuple

import requests

# API base URL - Update this to your API's URL
BASE_URL = "http://localhost:8000"


users_data = [
    {
        "username": "admin_user",
        "password": "admin123",
        "email": "admin@example.com",
        "first_name": "Alice",
        "last_name": "Admin",
        "bio": "Manages the platform with utmost precision.",
        "profile_picture": None,
        "role": "admin",
        "status": "active",
    },
    {
        "username": "author_john",
        "password": "author123",
        "email": "john.author@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "Passionate about writing and storytelling.",
        "profile_picture": None,
        "role": "author",
        "status": "active",
    },
    {
        "username": "author_jane",
        "password": "author456",
        "email": "jane.author@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "bio": "Expert in technology and creative content.",
        "profile_picture": None,
        "role": "author",
        "status": "active",
    },
    {
        "username": "reader_mike",
        "password": "reader123",
        "email": "mike.reader@example.com",
        "first_name": "Mike",
        "last_name": "Brown",
        "bio": "Eager to explore new topics and ideas.",
        "profile_picture": None,
        "role": "reader",
        "status": "active",
    },
    {
        "username": "reader_sara",
        "password": "reader456",
        "email": "sara.reader@example.com",
        "first_name": "Sara",
        "last_name": "Wilson",
        "bio": "Loves engaging with innovative content.",
        "profile_picture": None,
        "role": "reader",
        "status": "active",
    },
]


# Function to create a user
def create_user(user_data: Dict) -> Tuple[bool, Dict]:
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 201:
            return True, response.json()
        else:
            print(f"Failed to create user {user_data['username']}: {response.text}")
            return False, {}
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False, {}


# Function to get auth token for a user
def get_auth_token(username: str, password: str) -> Tuple[bool, str]:
    try:
        auth_data = {"username": username, "password": password}
        response = requests.post(f"{BASE_URL}/token", data=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            return True, token_data["access_token"]
        else:
            print(f"Failed to authenticate user {username}: {response.text}")
            return False, ""
    except Exception as e:
        print(f"Error authenticating: {str(e)}")
        return False, ""


# Function to create a post for a user
def create_post(token: str, post_data: Dict) -> Tuple[bool, Dict]:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers)
        if response.status_code == 201:
            return True, response.json()
        else:
            print(f"Failed to create post: {response.text}")
            return False, {}
    except Exception as e:
        print(f"Error creating post: {str(e)}")
        return False, {}


def main():
    print("Starting database population script...")
    created_users = []

    # Create 5 users
    print("Creating users...")
    for user_data in users_data:
        success, user = create_user(user_data)
        if success:
            print(f"Created user: {user['username']}")
            created_users.append((user, user_data["password"]))
        else:
            print(f"Failed to create user: {user_data['username']}")

    # Create 2 posts for each user with an author or admin role
    print("\nCreating posts for each user...")
    for user, password in created_users:
        success, token = get_auth_token(user["username"], password)
        if not success:
            print(
                f"Skipping post creation for {user['username']} - couldn't authenticate"
            )
            continue

        if user["role"] in ["author", "admin"]:
            for i in range(1, 3):  # 2 posts per user
                post_data = {
                    "title": f"Insightful Post {i} by {user['username']}",
                    "content": f"This is a meaningful article for post {i} by {user['username']}. Expanding ideas and engaging with the audience.",
                    "view_count": i * 10,
                    "is_featured": i % 2 == 0,  # Every second post is featured
                    "allow_comments": True,
                    "likes_count": i * 5,
                }

                success, post = create_post(token, post_data)
                if success:
                    print(f"Created post: {post['title']} for user {user['username']}")
                else:
                    print(f"Failed to create post for {user['username']}")
        else:
            print(
                f"Skipping post creation for {user['username']} - user role is {user['role']}"
            )

    print("\nDatabase population complete!")


if __name__ == "__main__":
    main()

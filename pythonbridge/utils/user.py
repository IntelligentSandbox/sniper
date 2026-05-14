def get_user(users: list, user_id: int) -> dict:
    for user in users:
        if user["id"] == user_id:
            return user


def get_username(users: list, user_id: int) -> str:
    user = get_user(users, user_id)
    return user["name"].upper()

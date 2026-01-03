ADMIN_EMAILS = {
    "agiptek@gmail.com",
    "farhanchehaab@gmail.com",
}

def is_admin(user: dict) -> bool:
    if not user:
        return False

    if user.get("is_admin") is True:
        return True

    if user.get("role") == "admin":
        return True

    if user.get("email") in ADMIN_EMAILS:
        return True

    return False

import pwd

def user_exists(username: str) -> bool:
    try:
        entry = pwd.getpwnam(username)
    except KeyError:
        return False

    return True

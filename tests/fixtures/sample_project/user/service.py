from auth import login


def can_sign_in(user: str, pwd: str) -> bool:
    return login.login_user(user, pwd)

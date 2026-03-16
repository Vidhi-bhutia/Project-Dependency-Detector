from auth.login import login_user


def login_route(user: str, pwd: str) -> bool:
    return login_user(user, pwd)

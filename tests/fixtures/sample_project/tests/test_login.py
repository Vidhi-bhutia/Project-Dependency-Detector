from auth.login import login_user


def test_login_user() -> None:
    assert login_user("john", "secret")

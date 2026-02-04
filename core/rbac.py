def require_role(user: dict, allowed: tuple[str, ...]):
    return bool(user) and user.get('role') in allowed

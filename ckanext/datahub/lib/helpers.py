
def user_is_sysadmin():
    """
    Returns True if the current user is a user_is_sysadmin
    """
    from pylons import c
    if not c.userobj:
        return False
    return c.userobj.sysadmin
from pylons import c

def user_is_sysadmin():
    """
    Returns True if the current user is a user_is_sysadmin
    """
    if not c.userobj:
        return False
    return c.userobj.sysadmin

def user_moderation_required():
    """
    Based on the user's moderation status we will determine
    whether the current user can continue what they were doing
    or whether they are blocked until moderated.
    If the user_extra key 'moderated' has the value:
        False - the user has already posted something and therefore
                must wait for moderation
        True  - the user has been moderated
        Empty - the user has yet to post anything
    """
    if not c.userobj:
        return True

    from paste.deploy.converters import asbool
    mod = asbool(c.userobj.extras.get('moderation', True))
    return not mod
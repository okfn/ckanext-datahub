import ckan.model as model


def package_delete(context, data_dict):
    if model.User.get(context.get('user')):
        return {'success': True}

    return {'success': False,
            'msg': 'You are not authorized to delete packages.'}


def resource_delete(context, data_dict):
    if model.User.get(context.get('user')):
        return {'success': True}

    return {'success': False,
            'msg': 'You are not authorized to delete resources.'}


"""
def datahub_package_create(context, data_dict):
    from ckan.logic.action.create import package_create as default_create
    from paste.deploy.converters import asbool

    usr = model.User.get(context.get('user'))
    if usr:
        moderation = not asbool(usr.extras.get('moderation', True))
        if moderation:
            return {'success': False,
                    'msg': 'Your user account is pending moderation.'}

    return default_create(context, data_dict)
"""
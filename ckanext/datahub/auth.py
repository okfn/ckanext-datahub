import ckan.model as model


def package_delete(context, data_dict):
    if model.User.get(context.get('user')):
        return {'success': True}

    return {'success': False,
            'msg': 'You are not authorized to delete packages.'}

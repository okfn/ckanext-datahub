import ckan.model as model
import ckan.new_authz as new_authz
from ckan.common import _


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

def file_upload(context, data_dict=None):
    user = context['user']
    if not new_authz.auth_is_registered_user():
        return {'success': False, 'msg': _('User %s not authorized to create packages') % user}
    if not new_authz.has_user_permission_for_some_org(user, 'create_dataset'):
        return {'success': False, 'msg': _('User %s not authorized to upload data') % user}
    return {'success': True}

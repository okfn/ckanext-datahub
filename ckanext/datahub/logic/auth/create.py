'''
Authorization layer for the datahub extension.

Includes overrides of ckan core authorization layer, as well as authorization
functions specific to the datahub extension.
'''

from ckan.lib.base import _
import ckan.authz as authz


def datahub_paid_service_create(context, data_dict):
    '''Only allow sysadmins to create PaidServices'''
    user = context.get('user')

    if not authz.Authorizer().is_sysadmin(user):
        return {
            'success': False,
            'msg': _('User {user} is not authorized to create '
                     'new paid services.').format(user=str(user))
        }
    else:
        return {'success': True}

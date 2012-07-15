'''
Update actions specific to the datahub.

This can be overriding existing ckan core actions, or it can be the creation
of new actions.

All actions defined in here are exposed through the action API, as well as
being available with `get_action()`.
'''

import logging

_log = logging.getLogger(__name__)

import ckan
from ckan.lib.base import _
import ckan.logic as logic

import ckanext.datahub.models as dh_models

_check_access = logic.check_access
_error_summary = ckan.logic.action.error_summary
_get_action = logic.get_action
_get_or_bust = logic.get_or_bust
_validate = ckan.lib.navl.dictization_functions.validate

ValidationError = logic.ValidationError


def datahub_paid_service_add_user(context, data_dict):
    '''Add an existing user to an existing paid service'''

    _check_access('datahub_paid_service_add_user', context, data_dict)

    model = context['model']

    # Existing User
    username = _get_or_bust(data_dict, 'user')
    user = model.User.by_name(username)
    if not user:
        raise ValidationError(_('Unknown user {user}').format(user=username))

    # Existing PaidService
    paid_service_name = _get_or_bust(data_dict, 'paid_service')
    paid_service = dh_models.PaidService.by_name(paid_service_name)
    if not paid_service:
        raise ValidationError(_('Unknown paid service {paid_service}')
                                .format(paid_service=paid_service_name))

    user.paid_service = paid_service
    model.repo.commit()
    _log.debug('User %s paid service changed to %s',
               username, paid_service_name)

    extended_context = dict(include_users=True, **context)
    return _get_action('datahub_paid_service_show')(
        extended_context,
        {'name': paid_service_name})

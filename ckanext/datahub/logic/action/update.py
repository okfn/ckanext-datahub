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


def datahub_payment_plan_add_user(context, data_dict):
    '''Add an existing user to an existing payment plan'''

    _check_access('datahub_payment_plan_add_user', context, data_dict)

    model = context['model']

    # Existing User
    username = _get_or_bust(data_dict, 'user')
    user = model.User.by_name(username)
    if not user:
        raise ValidationError(_('Unknown user {user}').format(user=username))

    # Existing PaymentPlan
    payment_plan_name = _get_or_bust(data_dict, 'payment_plan')
    payment_plan = dh_models.PaymentPlan.by_name(payment_plan_name)
    if not payment_plan:
        raise ValidationError(_('Unknown payment plan {payment_plan}')
                                .format(payment_plan=payment_plan_name))

    user.payment_plan = payment_plan
    model.repo.commit()
    _log.debug('User %s payment plan changed to %s',
               username, payment_plan_name)

    extended_context = dict(include_users=True, **context)
    return _get_action('datahub_payment_plan_show')(
        extended_context,
        {'name': payment_plan_name})

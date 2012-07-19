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

import ckanext.datahub.logic.dictization as dh_dictization
import ckanext.datahub.models as dh_models

_check_access = logic.check_access
_error_summary = ckan.logic.action.error_summary
_get_action = logic.get_action
_get_or_bust = logic.get_or_bust
_validate = ckan.lib.navl.dictization_functions.validate

ValidationError = logic.ValidationError

#------------------------------------------------------------------------------
# Actions specific to the datahub extension
#------------------------------------------------------------------------------


def datahub_user_set_payment_plan(context, data_dict):
    '''Set the User's payment plan.

    You must have sufficient privelages to set a User's payment plan.

    A User can be removed from an existing PaymentPlan by setting their
    payment_plan to None.

    :param user: The name of the user
    :type user: string
    :param payment_plan: The name of the payment plan, or the null value.
    :type payment_plan: string or null value

    :returns: Dict with the old and new payment plans, inc. signed-up users.
    :rtype: dictionary
    '''

    _check_access('datahub_user_set_payment_plan', context, data_dict)

    model = context['model']
    session = context['session']

    extended_context = context.copy()
    extended_context.update(include_users=True)

    # Existing User
    username = _get_or_bust(data_dict, 'user')
    user = model.User.by_name(username)
    if not user:
        session.rollback()
        raise ValidationError(_('Unknown user {user}').format(user=username))
    old_payment_plan = dh_dictization.payment_plan_dictize(user.payment_plan,
                                                           extended_context)

    # Existing PaymentPlan
    payment_plan_name = _get_or_bust(data_dict, 'payment_plan')
    if isinstance(payment_plan_name, basestring):
        payment_plan = dh_models.PaymentPlan.by_name(payment_plan_name)
        if not payment_plan:
            session.rollback()
            raise ValidationError(_('Unknown payment plan {payment_plan}')
                                    .format(payment_plan=payment_plan_name))
    elif payment_plan_name is None:
        payment_plan =  None
    
    user.payment_plan = payment_plan
    model.repo.commit()
    _log.debug('User %s payment plan changed to %s',
               username, payment_plan_name)

    new_payment_plan = dh_dictization.payment_plan_dictize(payment_plan,
                                                           extended_context)

    # Return the old plan and the new plan
    return {
        'old_payment_plan': old_payment_plan,
        'new_payment_plan': new_payment_plan,
    }

#------------------------------------------------------------------------------
# Actions that overide default CKAN behaviour
#------------------------------------------------------------------------------


def user_update(context, data_dict):
    '''Override the core user_update() action.

    In addition to the normal update action, sysadmins can set the payment
    plan of a User.

    If there's a `payment_plan` field on the data_dict, then create the new
    User, adding them to that payment_plan.  This uses the
    `datahub_user_set_payment_plan` action, so that correct authorization rules
    are applied.

    If there's no `payment_plan` field then the action behaves no differently
    than ckan core's behaviour.

    Note that we don't allow users to set their own payment plan **at all**.
    Not even to downgrade or remove their payment plans: we don't want users to
    inadvertantly set their payment plan to None!

    Additional parameters:

    :param payment_plan: Optional.  The name of the payment plan.
    :type payment_plan: string or null value#

    :returns: Dict representing the update user.
    :rtype: dictionary
    '''

    session = context['session']

    is_payment_plan = 'payment_plan' in data_dict
    payment_plan = data_dict.pop('payment_plan', None)

    # The context for the core update_user action invocation.
    update_user_context = context.copy()
    update_user_context['defer_commit'] = is_payment_plan

    # Update the User as per usual.
    user = logic.action.update.user_update(update_user_context, data_dict)

    if is_payment_plan:
        # Note: The try-block is necessary as we've created the User
        # un-conditionally, and need to roll it back if the set_payment_plan
        # fails due to not being authorized.
        #
        # This is true even if we explicitely run
        # `_check_access('datahub_user_set_payment_plan')` beforehand, as there
        # may be other checks in the `set_payment_plan` action that we're not
        # aware of.
        try:
            _get_action('datahub_user_set_payment_plan')(
                context,
                {'user': user['name'],
                'payment_plan': payment_plan})

        except logic.NotAuthorized:
            session.rollback()
            raise
    return _get_action('user_show')(context, {'id': user['name']})

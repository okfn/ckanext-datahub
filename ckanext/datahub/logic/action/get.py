'''
Get actions specific to the datahub.

This can be overriding existing ckan core actions, or it can be the creation
of new actions.

All actions defined in here are exposed through the action API, as well as
being available with `get_action()`.
'''

import logging

_log = logging.getLogger(__name__)

import ckan
import ckan.logic as logic

import ckanext.datahub.models as dh_models
import ckanext.datahub.logic.dictization as dh_dictization

_check_access = logic.check_access
_error_summary = ckan.logic.action.error_summary
_get_action = logic.get_action
_get_or_bust = logic.get_or_bust
_validate = ckan.lib.navl.dictization_functions.validate

Authorizer = ckan.authz.Authorizer
ValidationError = logic.ValidationError
NotFound = logic.NotFound


@logic.side_effect_free
def datahub_payment_plan_show(context, data_dict):
    '''Show an existing PaymentPlan

    Identified by name.
    '''

    _check_access('datahub_payment_plan_show', context, data_dict)

    name = _get_or_bust(data_dict, 'name')
    payment_plan = dh_models.PaymentPlan.by_name(name)

    if not payment_plan:
        raise NotFound

    return dh_dictization.payment_plan_dictize(payment_plan, context)

@logic.side_effect_free
def datahub_payment_plan_list(context, data_dict):
    '''List existing PaymentPlans

    Optionally filtered by name.
    '''

    _check_access('datahub_payment_plan_list', context, data_dict)

    session = context['session']

    names = data_dict.get('names', [])
    if isinstance(names, basestring):
        names = [names]

    q = session.query(dh_models.PaymentPlan).\
                outerjoin(dh_models.PaymentPlan.users)
    if names:
        q = q.filter(dh_models.PaymentPlan.name.in_(names))

    extended_context = dict(include_users=True, **context)
    return dh_dictization.payment_plan_list_dictize(q, extended_context)

@logic.side_effect_free
def user_show(context, data_dict):
    '''Return standard user account, augmented with payment plan.

    Payment plan is only visible to sysadmins and the owner of the account.
    '''
    model = context['model']
    user = context['user']

    user_dict = logic.action.get.user_show(context, data_dict)
    user_obj = model.User.get(user_dict['id'])

    if Authorizer().is_sysadmin(unicode(user)) or user == user_obj.name:
        # Only attach payment plan information if sysadmin, or the owner of
        # the requested user.
        if 'payment_plan' in user_dict:
            raise Exception('Cannot attach payment_plan to user_dict as it '
                            'would clobber an existing item.')

        user_dict['payment_plan'] = dh_dictization.payment_plan_dictize(
            user_obj.payment_plan,
            context)

    return user_dict

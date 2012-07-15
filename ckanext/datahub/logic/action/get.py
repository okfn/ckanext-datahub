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

ValidationError = logic.ValidationError
NotFound = logic.NotFound


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

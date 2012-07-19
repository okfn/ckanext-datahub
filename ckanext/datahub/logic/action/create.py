'''
"Create" actions specific to the datahub.

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
import ckanext.datahub.schema as dh_schema

_check_access = logic.check_access
_error_summary = ckan.logic.action.error_summary
_get_action = logic.get_action
_get_or_bust = logic.get_or_bust
_validate = ckan.lib.navl.dictization_functions.validate

ValidationError = logic.ValidationError

#------------------------------------------------------------------------------
# Actions specific to the datahub extension
#------------------------------------------------------------------------------


def datahub_payment_plan_create(context, data_dict):
    '''Creates a new PaymentPlan

    You must be authorized to create new payment plans.

    Required arguments:

    :param name: the name of the new payment plan
    :type name: string

    :returns: a dictionary representation of the newly created payment plan.
    :rtype: dictionary
    '''

    _check_access('datahub_payment_plan_create', context, data_dict)

    model = context['model']
    session = context['session']

    schema = context.get('schema') or dh_schema.default_payment_plan_schema()

    data, errors = _validate(data_dict, schema, context=context)

    if errors:
        session.rollback()
        raise ValidationError(errors, _error_summary(errors))

    name = data.get('name')
    service = dh_models.PaymentPlan(name=name)
    session.add(service)

    if not context.get('defer_commit'):
        model.repo.commit()

    _log.debug('Created new PaymentPlan: %s', name)
    return _get_action('datahub_payment_plan_show')(context, {'name': name})

#------------------------------------------------------------------------------
# Actions that overide default CKAN behaviour
#------------------------------------------------------------------------------


def user_create(context, data_dict):
    '''Override ckan's `user_create` action to allow a payment plan to be set.

    If there's a `payment_plan` field on the data_dict, then create the new
    User, adding them to that payment_plan.  This uses the
    `datahub_user_set_payment_plan` action, so that correct authorization rules
    are applied.

    If there's no `payment_plan` field or if the payment_plan field value is
    None, then the action behaves no differently than ckan core's behaviour.

    Required parameters, over and above CKAN core's user_create action:

    :param payment_plan: Optional.  Name of the payment plan to add the user to
    :type payment_plan: string
    '''

    session = context['session']

    payment_plan = data_dict.pop('payment_plan', None)

    # The context for the core create_user action invocation.
    create_user_context = context.copy()
    create_user_context['defer_commit'] = payment_plan is not None

    # Create the User as per usual.
    user = logic.action.create.user_create(create_user_context, data_dict)

    if payment_plan is not None:
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

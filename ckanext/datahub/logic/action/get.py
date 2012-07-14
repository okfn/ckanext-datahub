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


def datahub_paid_service_show(context, data_dict):
    '''Show an existing PaidService

    Identified by name.
    '''

    _check_access('datahub_paid_service_show', context, data_dict)

    name = _get_or_bust(data_dict, 'name')
    paid_service = dh_models.PaidService.by_name(name)

    if not paid_service:
        raise NotFound

    return dh_dictization.paid_service_dictize(paid_service, context)

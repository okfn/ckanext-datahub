'''
Create actions specific to the datahub.

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


def datahub_paid_service_create(context, data_dict):
    '''Creates a new PaidService'''

    _check_access('datahub_paid_service_create', context, data_dict)

    model = context['model']
    session = context['session']

    schema = context.get('schema') or dh_schema.default_paid_service_schema()

    data, errors = _validate(data_dict, schema)

    if errors:
        session.rollback()
        raise ValidationError(errors, _error_summary(errors))

    name = data.get('name')
    service = dh_models.PaidService(name=name)
    session.add(service)

    model.repo.commit()
    _log.debug('Created new PaidService: %s', name)
    return _get_action('datahub_paid_service_show')(context, {'name': name})

'''
Schemas specific to the datahub plugin.
'''

import ckan.lib.navl.validators as navl_validators
import ckan.logic.validators as validators

import ckanext.datahub.validators as dh_validators

def default_paid_service_schema():
    return {
        'name': [navl_validators.not_empty,
                 unicode,
                 validators.name_validator,
                 dh_validators.paid_service_name_does_not_clash],
    }

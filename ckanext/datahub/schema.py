'''
Schemas specific to the datahub plugin.
'''

import ckan.lib.navl.validators as navl_validators
import ckan.logic.validators as validators

import ckanext.datahub.validators as dh_validators


def default_payment_plan_schema():
    return {
        'name': [navl_validators.not_empty,
                 unicode,
                 validators.name_validator,
                 dh_validators.payment_plan_name_does_not_clash],
    }

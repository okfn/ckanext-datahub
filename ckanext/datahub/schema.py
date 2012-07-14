'''
Schemas specific to the datahub plugin.
'''

from ckan.lib.navl.validators import not_empty
from ckan.logic.validators import name_validator


def default_paid_service_schema():
    return {
        'name': [not_empty, unicode, name_validator],
    }

'''
Dictization functions for domain models specific to the datahub extension.
'''

import ckan.lib.dictization.model_dictize as model_dictize


def paid_service_list_dictize(paid_services, context):
    return [ paid_service_dictize(p, context) for p in paid_services ]

def paid_service_dictize(paid_service, context):
    data = paid_service.as_dict()
    if context.get('include_users', False):
        data['users'] = model_dictize.user_list_dictize(paid_service.users,
                                                        context)
    return data

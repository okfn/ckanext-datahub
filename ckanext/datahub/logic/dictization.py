'''
Dictization functions for domain models specific to the datahub extension.
'''

import ckan.lib.dictization.model_dictize as model_dictize


def payment_plan_list_dictize(payment_plans, context):
    return [ payment_plan_dictize(p, context) for p in payment_plans ]

def payment_plan_dictize(payment_plan, context):

    if payment_plan is None:
        return None

    data = payment_plan.as_dict()
    if context.get('include_users', False):
        data['users'] = model_dictize.user_list_dictize(payment_plan.users,
                                                        context)
    return data

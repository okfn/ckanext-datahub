'''
Validator functions specific to the datahub extension.
'''
from ckan.lib.base import _
from ckan.lib.navl.dictization_functions import missing

import ckanext.datahub.models as dh_models


def payment_plan_name_does_not_clash(key, data, errors, context):
    session = context['session']
    payment_plan = context.get('payment_plan')

    query = session.query(dh_models.PaymentPlan.name).filter_by(name=data[key])
    if payment_plan:
        payment_plan_id = payment_plan.id
    else:
        payment_plan_id = data.get(key[:-1] + ('id',))
    if payment_plan_id and payment_plan_id is not missing:
        query = query.filter(dh_models.PaymentPlan.id != payment_plan_id)
    result = query.first()
    if result:
        errors[key].append(_('PaymentPlan name already exists in database'))

'''
Validator functions specific to the datahub extension.
'''
from ckan.lib.base import _
from ckan.lib.navl.dictization_functions import missing

import ckanext.datahub.models as dh_models

def paid_service_name_does_not_clash(key, data, errors, context):
    session = context['session']
    paid_service = context.get('paid_service')

    query = session.query(dh_models.PaidService.name).filter_by(name=data[key])
    if paid_service:
        paid_service_id = paid_service.id
    else:
        paid_service_id = data.get(key[:-1] + ('id',))
    if paid_service_id and paid_service_id is not missing:
        query = query.filter(dh_models.PaidService.id <> paid_service_id)
    result = query.first()
    if result:
        errors[key].append(_('PaidService name already exists in database'))

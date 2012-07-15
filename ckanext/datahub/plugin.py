import ckan.plugins as p

import ckanext.datahub.models as dh_models


class DataHub(p.SingletonPlugin):
    '''
    This plugin provides customisation specific to datahub.
    '''

    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')

    def configure(self, config):
        '''Ensure model tables are in place'''
        dh_models.setup()

    def get_actions(self):
        from ckanext.datahub.logic.action.get import (
            datahub_paid_service_show,
            datahub_paid_service_list)

        from ckanext.datahub.logic.action.create import (
            datahub_paid_service_create)

        from ckanext.datahub.logic.action.update import (
            datahub_paid_service_add_user)

        return {
            'datahub_paid_service_add_user': datahub_paid_service_add_user,
            'datahub_paid_service_create': datahub_paid_service_create,
            'datahub_paid_service_list': datahub_paid_service_list,
            'datahub_paid_service_show': datahub_paid_service_show,
        }

    def get_auth_functions(self):

        from ckanext.datahub.logic.auth.get import (
            datahub_paid_service_show,
            datahub_paid_service_list)

        from ckanext.datahub.logic.auth.create import (
            datahub_paid_service_create)

        from ckanext.datahub.logic.auth.update import (
            datahub_paid_service_add_user)

        return {
            'datahub_paid_service_add_user': datahub_paid_service_add_user,
            'datahub_paid_service_create': datahub_paid_service_create,
            'datahub_paid_service_list': datahub_paid_service_list,
            'datahub_paid_service_show': datahub_paid_service_show,
        }

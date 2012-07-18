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
            datahub_payment_plan_show,
            datahub_payment_plan_list,
            user_show)

        from ckanext.datahub.logic.action.create import (
            datahub_payment_plan_create,
            user_create)

        from ckanext.datahub.logic.action.update import (
            datahub_user_set_payment_plan,
            user_update)

        return {
            'datahub_user_set_payment_plan': datahub_user_set_payment_plan,
            'datahub_payment_plan_create': datahub_payment_plan_create,
            'datahub_payment_plan_list': datahub_payment_plan_list,
            'datahub_payment_plan_show': datahub_payment_plan_show,
            'user_create': user_create,
            'user_show': user_show,
            'user_update': user_update,
        }

    def get_auth_functions(self):

        from ckanext.datahub.logic.auth.get import (
            datahub_payment_plan_show,
            datahub_payment_plan_list)

        from ckanext.datahub.logic.auth.create import (
            datahub_payment_plan_create)

        from ckanext.datahub.logic.auth.update import (
            datahub_user_set_payment_plan)

        return {
            'datahub_user_set_payment_plan': datahub_user_set_payment_plan,
            'datahub_payment_plan_create': datahub_payment_plan_create,
            'datahub_payment_plan_list': datahub_payment_plan_list,
            'datahub_payment_plan_show': datahub_payment_plan_show,
        }

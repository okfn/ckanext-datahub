import ckan.plugins as p
import ckanext.datahub.auth as auth


class DataHub(p.SingletonPlugin):
    '''
    This plugin provides customisation specific to datahub.
    '''

    p.implements(p.IConfigurable)
    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers)

    def configure(self, config):
        from ckanext.datahub.model.user_extra import setup as model_setup
        model_setup()

    def update_config(self, config):
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('fanstatic', 'ckanext-datahub')


    def get_auth_functions(self):
        return {'package_delete': auth.package_delete,
                'resource_delete': auth.resource_delete,}
                #'package_create': auth.datahub_package_create}

    def get_helpers(self):
        """
        All functions, not starting with __ in the ckanext.datahub.lib
        module will be loaded and makde available as helpers to the
        templates.
        """
        from ckanext.datahub.lib import helpers
        from inspect import getmembers, isfunction

        helper_dict = {}

        funcs = [o for o in getmembers(helpers, isfunction)]
        return dict([(f[0],f[1],) for f in funcs if not f[0].startswith('__')])

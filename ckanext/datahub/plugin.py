import ckan.plugins as p
import ckanext.datahub.auth as auth


class DataHub(p.SingletonPlugin):
    '''
    This plugin provides customisation specific to datahub.
    '''

    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)

    def update_config(self, config):
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('fanstatic', 'ckanext-datahub')

    def get_auth_functions(self):
        return {'package_delete': auth.package_delete}

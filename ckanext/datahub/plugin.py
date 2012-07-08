import ckan.plugins as p

import ckanext.datahub.models as dh_models

class DataHub(p.SingletonPlugin):
    '''
    This plugin provides customisation specific to datahub.
    '''

    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')

    def configure(self, config):
        '''Ensure model tables are in place'''
        dh_models.setup()

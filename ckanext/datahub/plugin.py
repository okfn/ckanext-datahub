import ckan.plugins as p


# auth functions for read-only mode
#
# disable create/update of packages and groups for all users

def package_update(context, data_dict):
    return {'success': False}


def package_create(context, data_dict):
    return {'success': False}


def group_update(context, data_dict):
    return {'success': False}


def group_create(context, data_dict):
    return {'success': False}


class DataHub(p.SingletonPlugin):
    '''
    This plugin provides customisation specific to datahub.
    '''

    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')

    def get_auth_functions(self):
        return {'package_create': package_create,
                'package_update': package_update,
                'group_create': group_create,
                'group_update': group_update}

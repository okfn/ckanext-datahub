import ckan.model as model
import ckan.plugins as p


class DatahubCommand(p.toolkit.CkanCommand):
    '''Perform Datahub commands.

    Usage::

        paster datahub spammer <user name>

    Labels a given user as being a spammer, and marks all of the
    datasets that they have created as being spam.
    This deletes the user and any datasets that they have created.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(DatahubCommand, self).__init__(name)

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help'] or \
                len(self.args) != 2:
            print self.usage
            return

        cmd = self.args[0]
        self._load_config()

        user = p.toolkit.get_action('get_site_user')(
            {'model': model, 'ignore_auth': True}, {})
        self.user = user['name']

        if cmd == 'spammer':
            self._spammer(self.args[1])
        else:
            print 'Error: Command "{0}" not recognized'.format(cmd)
            print
            print self.usage

    def _spam_user(self, context, user_name):
        print 'Removing spam user: "{0}"'.format(user_name)
        # currently no user_delete logic function
        user = model.User.by_name(user_name)
        user.delete()
        model.repo.commit_and_remove()

    def _spam_dataset(self, context, dataset_name):
        print 'Removing dataset: {0}'.format(dataset_name)
        p.toolkit.get_action('package_delete')(context, {'id': dataset_name})

    def _spammer(self, user_name):
        try:
            user = p.toolkit.get_action('user_show')({}, {'id': user_name})
        except p.toolkit.ObjectNotFound:
            print 'Error: User "{0}" not found'.format(user_name)
            return

        context = {'model': model, 'user': self.user}

        datasets = user.get('datasets', [])
        self._spam_user(context, user['name'])

        print 'Removing {0} spam datasets created by "{1}":'.format(
            len(datasets), user_name)

        for dataset in datasets:
            self._spam_dataset(context, dataset['name'])

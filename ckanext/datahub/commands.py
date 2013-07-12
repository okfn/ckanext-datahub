import ckan.model as model
import ckan.lib.helpers as h
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
                not len(self.args) in [1, 2]:
            print self.usage
            return

        cmd = self.args[0]
        self._load_config()

        user = p.toolkit.get_action('get_site_user')(
            {'model': model, 'ignore_auth': True}, {})
        self.user = user['name']

        if cmd == 'spammer':
            self._spammer(self.args[1])
        elif cmd == 'find-spam':
            self._find_spam()
        else:
            print 'Error: Command "{0}" not recognized'.format(cmd)
            print
            print self.usage

    def _spam_user(self, context, data_dict):
        user_name = data_dict['name']
        print 'Removing spam user: "{0}"'.format(user_name)
        # currently no user_delete logic function
        user = model.User.by_name(user_name)
        user.delete()
        model.repo.commit_and_remove()

    def _spam_dataset(self, context, data_dict):
        dataset_title = data_dict.get('title', data_dict['name'])
        print 'Marking dataset "{0}" as spam'.format(dataset_title)

        spam = {'entity_id': data_dict['id'],
                'entity_type': 'package',
                'task_type': 'antispam',
                'key': 'spam',
                'value': True}
        p.toolkit.get_action('task_status_update')(context, spam)

        print 'Removing dataset: "{0}"'.format(dataset_title)
        p.toolkit.get_action('package_delete')(
            context, {'id': data_dict['id']})

    def _spammer(self, user_name):
        try:
            user = p.toolkit.get_action('user_show')({}, {'id': user_name})
        except p.toolkit.ObjectNotFound:
            print 'Error: User "{0}" not found'.format(user_name)
            return

        context = {'model': model, 'user': self.user}

        datasets = user.get('datasets', [])
        self._spam_user(context, user)

        print 'Removing {0} spam datasets created by "{1}":'.format(
            len(datasets), user_name)

        for dataset in datasets:
            self._spam_dataset(context, dataset)

    def _find_spam(self):
        context = {'model': model, 'user': self.user}

        dataset_names = p.toolkit.get_action('package_list')({}, {})
        num_datasets = len(dataset_names)
        page_size = 50
        num_pages = num_datasets / page_size
        spam_datasets = []

        try:
            for page in range(num_pages):
                datasets = p.toolkit.get_action('package_search')(
                    {}, {'rows': page_size, 'start': page})['results']
                for dataset in datasets:
                    if len(dataset.get('resources', [])) == 0:
                        print
                        print 'Name:', dataset['name']
                        print 'Title:', dataset.get('title')
                        print 'Description:',
                        print h.markdown_extract(dataset.get('notes'), 200)
                        is_spam = ''
                        while not is_spam in ['y', 'n']:
                            is_spam = raw_input('Spam? [y/n]  >> ')
                        if is_spam == 'y':
                            spam_datasets.append(dataset)
        except KeyboardInterrupt:
            print
        finally:
            for dataset in spam_datasets:
                self._spam_dataset(context, dataset)

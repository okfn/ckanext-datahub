import operator

from nose.tools import assert_equal, assert_raises

import ckan.logic as logic
import ckan.model as model
import ckan.tests

import ckanext.datahub.models as dh_models

CreateTestData = ckan.tests.CreateTestData


class TestPaidServiceActions(object):

    @classmethod
    def setup_class(cls):
        dh_models.setup()

        CreateTestData.create_user('alice', password='pass')
        CreateTestData.create_user('bob', password='pass')

    def setUp(self):
        CreateTestData.create_basic_test_data()

    def tearDown(self):
        CreateTestData.delete()

        for service in model.Session.query(dh_models.PaidService):
            service.purge()
        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(cls):
        model.Session.close_all()
        model.repo.clean_db()

    def test_create_new_paid_service_as_sysadmin(self):
        '''Sysadmins should be able to create new PaidServices'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        data_dict = {'name': 'enterprise-level'}
        result = logic.get_action('datahub_paid_service_create')(context, data_dict)
        assert_equal('enterprise-level', result['name'])

    def test_create_new_paid_service_as_normal_user(self):
        '''"Normal" logged-in users should not be able to create PaidServices'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('tester'),
        }

        data_dict = {'name': 'enterprise-level'}

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('datahub_paid_service_create'),
            context, data_dict)

    def test_create_new_paid_service_as_anonymous_user(self):
        '''Anonymous users should not be able to create PaidServices'''
        
        context = {
            'model': model,
            'session': model.Session,
        }

        data_dict = {'name': 'enterprise-level'}

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('datahub_paid_service_create'),
            context, data_dict)

    def test_create_paid_service_with_duplicate_name(self):
        '''PaidService names should be unique'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        data_dict = {'name': 'enterprise-level'}
        result = logic.get_action('datahub_paid_service_create')(context, data_dict)
        assert_equal('enterprise-level', result['name'])

        ## Now, try to create a new PaidService of the same name.
        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_paid_service_create'),
            context, data_dict)

    def test_create_paid_service_with_empty_name(self):
        '''PaidService names should not be empty'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        data_dict = {'name': ''}
        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_paid_service_create'),
            context, data_dict)

    def test_add_existing_user_to_existing_paid_service(self):
        '''Add user with no paid service to an existing paid service'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create the enterpise PaidService first.
        logic.get_action('datahub_paid_service_create')(
            context,
            {'name': 'enterprise'})

        # And add the User to it
        result = logic.get_action('datahub_paid_service_add_user')(
            context,
            {'paid_service': 'enterprise',
             'user': 'tester'})

        assert_equal(result['name'], 'enterprise')
        assert_equal(result['users'][0]['name'], 'tester') 

    def test_add_non_existant_user_to_existing_paid_service(self):
        '''Should fail if the user does not exist'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create the enterpise PaidService first.
        logic.get_action('datahub_paid_service_create')(
            context,
            {'name': 'enterprise'})

        # And add a non-existant User to it
        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_paid_service_add_user'),
            context,
            {'paid_service': 'enterprise',
             'user': 'i-do-not-exist'})

    def test_add_user_to_non_existant_paid_service(self):
        '''Should fail if the paid service does not exist'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_paid_service_add_user'),
            context,
            {'paid_service': 'does-not-exist',
             'user': 'tester'})

    def test_list_paid_service_lists_all_services(self):
        '''Lists all services and users which belong to them'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create some PaidServices first
        create_action = logic.get_action('datahub_paid_service_create')
        for name in 'enterprise small-business individual'.split():
            data_dict = {'name': name}
            create_action(context, data_dict)

        # Add some users to the PaidServices
        add_action = logic.get_action('datahub_paid_service_add_user')
        def add_user_to(paid_service_name, username):
            data_dict = {
                'paid_service': paid_service_name,
                'user': username,
            }
            add_action(context, data_dict)

        add_user_to('enterprise', 'tester')
        add_user_to('enterprise', 'joeadmin')
        add_user_to('individual', 'annafan')

        # Retrieve list of PaidServices
        data_dict = {}
        result = logic.get_action('datahub_paid_service_list')(
            context,
            data_dict)

        # Assertions
        assert_equal(len(result), 3) # 3 paid services.
        
        enterprise, individual, small_business = [ ps for ps in \
                sorted(result, key=operator.itemgetter('name')) ]

        assert_equal(len(enterprise['users']), 2)
        assert_equal(len(individual['users']), 1)
        assert_equal(len(small_business['users']), 0)
    
    def test_list_paid_service_lists_selected_services(self):
        '''Lists selected services and users which belong to them'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create some PaidServices first
        create_action = logic.get_action('datahub_paid_service_create')
        for name in 'enterprise small-business individual'.split():
            data_dict = {'name': name}
            create_action(context, data_dict)

        # Retrieve list of PaidServices
        data_dict = {'names': ['enterprise', 'small-business']}
        result = logic.get_action('datahub_paid_service_list')(
            context,
            data_dict)

        assert_equal(len(result), 2) # 2 paid services.

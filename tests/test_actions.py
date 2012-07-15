import operator

from nose.tools import assert_equal, assert_raises

import ckan.logic as logic
import ckan.model as model
import ckan.tests

import ckanext.datahub.models as dh_models

CreateTestData = ckan.tests.CreateTestData


class TestPaymentPlanActions(object):

    @classmethod
    def setup_class(cls):
        dh_models.setup()

        CreateTestData.create_user('alice', password='pass')
        CreateTestData.create_user('bob', password='pass')

    def setUp(self):
        CreateTestData.create_basic_test_data()

    def tearDown(self):
        CreateTestData.delete()

        for service in model.Session.query(dh_models.PaymentPlan):
            service.purge()
        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(cls):
        model.Session.close_all()
        model.repo.clean_db()

    def test_create_new_payment_plan_as_sysadmin(self):
        '''Sysadmins should be able to create new PaymentPlans'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        data_dict = {'name': 'enterprise-level'}
        result = logic.get_action('datahub_payment_plan_create')(context, data_dict)
        assert_equal('enterprise-level', result['name'])

    def test_create_new_payment_plan_as_normal_user(self):
        '''"Normal" logged-in users should not be able to create PaymentPlans'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('tester'),
        }

        data_dict = {'name': 'enterprise-level'}

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('datahub_payment_plan_create'),
            context, data_dict)

    def test_create_new_payment_plan_as_anonymous_user(self):
        '''Anonymous users should not be able to create PaymentPlans'''
        
        context = {
            'model': model,
            'session': model.Session,
        }

        data_dict = {'name': 'enterprise-level'}

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('datahub_payment_plan_create'),
            context, data_dict)

    def test_create_payment_plan_with_duplicate_name(self):
        '''PaymentPlan names should be unique'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        data_dict = {'name': 'enterprise-level'}
        result = logic.get_action('datahub_payment_plan_create')(context, data_dict)
        assert_equal('enterprise-level', result['name'])

        ## Now, try to create a new PaymentPlan of the same name.
        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_payment_plan_create'),
            context, data_dict)

    def test_create_payment_plan_with_empty_name(self):
        '''PaymentPlan names should not be empty'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        data_dict = {'name': ''}
        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_payment_plan_create'),
            context, data_dict)

    def test_add_existing_user_to_existing_payment_plan(self):
        '''Add user with no payment plan to an existing payment plan'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create the enterpise PaymentPlan first.
        logic.get_action('datahub_payment_plan_create')(
            context,
            {'name': 'enterprise'})

        # And add the User to it
        result = logic.get_action('datahub_user_set_payment_plan')(
            context,
            {'payment_plan': 'enterprise',
             'user': 'tester'})

        assert_equal(result['name'], 'enterprise')
        assert_equal(result['users'][0]['name'], 'tester') 

    def test_add_non_existant_user_to_existing_payment_plan(self):
        '''Should fail if the user does not exist'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create the enterpise PaymentPlan first.
        logic.get_action('datahub_payment_plan_create')(
            context,
            {'name': 'enterprise'})

        # And add a non-existant User to it
        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_user_set_payment_plan'),
            context,
            {'payment_plan': 'enterprise',
             'user': 'i-do-not-exist'})

    def test_add_user_to_non_existant_payment_plan(self):
        '''Should fail if the payment plan does not exist'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        assert_raises(
            logic.ValidationError,
            logic.get_action('datahub_user_set_payment_plan'),
            context,
            {'payment_plan': 'does-not-exist',
             'user': 'tester'})

    def test_remove_user_from_payment_plan(self):
        '''Remove a User from their payment plan.'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create the enterpise PaymentPlan first.
        logic.get_action('datahub_payment_plan_create')(
            context,
            {'name': 'enterprise'})

        # And add the User to it
        result = logic.get_action('datahub_user_set_payment_plan')(
            context,
            {'payment_plan': 'enterprise',
             'user': 'tester'})

        # Check they are a member of it.
        assert_equal(result['name'], 'enterprise')
        assert_equal(result['users'][0]['name'], 'tester') 

        # And now remove them from it.
        result = logic.get_action('datahub_user_set_payment_plan')(
            context,
            {'payment_plan': None,
             'user': 'tester'})
        
        # Check no payment plan was returned.
        assert_equal(result, None)

        # Check they are no longer a member of any payment plan.
        user = model.User.by_name('tester')
        assert_equal(user.payment_plan, None)

    def test_list_payment_plan_lists_all_services(self):
        '''Lists all services and users which belong to them'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create some PaymentPlans first
        create_action = logic.get_action('datahub_payment_plan_create')
        for name in 'enterprise small-business individual'.split():
            data_dict = {'name': name}
            create_action(context, data_dict)

        # Add some users to the PaymentPlans
        add_action = logic.get_action('datahub_user_set_payment_plan')
        def add_user_to(payment_plan_name, username):
            data_dict = {
                'payment_plan': payment_plan_name,
                'user': username,
            }
            add_action(context, data_dict)

        add_user_to('enterprise', 'tester')
        add_user_to('enterprise', 'joeadmin')
        add_user_to('individual', 'annafan')

        # Retrieve list of PaymentPlans
        data_dict = {}
        result = logic.get_action('datahub_payment_plan_list')(
            context,
            data_dict)

        # Assertions
        assert_equal(len(result), 3) # 3 payment plans.
        
        enterprise, individual, small_business = [ ps for ps in \
                sorted(result, key=operator.itemgetter('name')) ]

        assert_equal(len(enterprise['users']), 2)
        assert_equal(len(individual['users']), 1)
        assert_equal(len(small_business['users']), 0)
    
    def test_list_payment_plan_lists_selected_services(self):
        '''Lists selected services and users which belong to them'''

        context = {
            'model': model,
            'session': model.Session,
            'user': model.User.by_name('testsysadmin'),
        }

        # Create some PaymentPlans first
        create_action = logic.get_action('datahub_payment_plan_create')
        for name in 'enterprise small-business individual'.split():
            data_dict = {'name': name}
            create_action(context, data_dict)

        # Retrieve list of PaymentPlans
        data_dict = {'names': ['enterprise', 'small-business']}
        result = logic.get_action('datahub_payment_plan_list')(
            context,
            data_dict)

        assert_equal(len(result), 2) # 2 payment plans.

import operator

from nose.tools import (
        assert_equal,
        assert_raises,
        assert_not_equal,
        assert_not_in)

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

class TestUserActions(object):
    '''Tests for the override user_create and user_update actions.'''

    @classmethod
    def setup_class(cls):
        dh_models.setup()

    def setUp(self):
        CreateTestData.create_basic_test_data()

        individual_plan = dh_models.PaymentPlan(name='individual')
        model.Session.add(individual_plan)

        # Assign "russianfan" a payment plan
        russian_fan = model.User.by_name('russianfan')
        russian_fan.payment_plan = individual_plan
        model.repo.commit_and_remove()

    def tearDown(self):
        CreateTestData.delete()

        new_user = model.User.by_name('a-new-user')
        if new_user:
            new_user.purge()

        for service in model.Session.query(dh_models.PaymentPlan):
            service.purge()

        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(cls):
        model.Session.close_all()
        model.repo.clean_db()

    def test_user_create_without_payment_plan_as_sysadmin(self):
        '''Creating a new user without a payment plan set works as normal'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        logic.get_action('user_create')(
            context,
            {'name': 'a-new-user',
             'password': 'a-password',
             'email': 'a-user@example.com'})

        user = model.User.by_name('a-new-user')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)

    def test_user_create_with_null_payment_plan_as_sysadmin(self):
        '''Creating a new user without null payment plan works as normal'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        logic.get_action('user_create')(
            context,
            {'name': 'a-new-user',
             'password': 'a-password',
             'email': 'a-user@example.com',
             'payment_plan': None})

        user = model.User.by_name('a-new-user')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)

    def test_user_create_without_payment_plan_as_normal_user(self):
        '''Normal users should still be able to create new Users'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'tester',
        }

        logic.get_action('user_create')(
            context,
            {'name': 'a-new-user',
             'password': 'a-password',
             'email': 'a-user@example.com'})

        user = model.User.by_name('a-new-user')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)

    def test_user_create_with_payment_plan_as_sysadmin(self):
        '''Create a new user as sysadmin, belonging to a payment plan'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        # Create a payment plan first
        logic.get_action('datahub_payment_plan_create')(
            context,
            {'name': 'enterprise'})
        payment_plan = dh_models.PaymentPlan.by_name('enterprise')
        assert_not_equal(payment_plan, None)

        # Now create a User, belonging to the new payment plan.
        logic.get_action('user_create')(
            context,
            {'name': 'a-new-user',
             'password': 'a-password',
             'email': 'a-user@example.com',
             'payment_plan': 'enterprise'})

        user = model.User.by_name('a-new-user')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, payment_plan)

    def test_user_create_with_payment_plan_as_logged_in_user(self):
        '''Normal users cannot create new Users belonging to a payment plan'''

        sysadmin_context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        context = {
            'model': model,
            'session': model.Session,
            'user': 'tester',
        }

        # Create a payment plan (as sysadmin) first
        logic.get_action('datahub_payment_plan_create')(
            sysadmin_context,
            {'name': 'enterprise'})
        payment_plan = dh_models.PaymentPlan.by_name('enterprise')
        assert_not_equal(payment_plan, None)

        # Now try to create a User, belonging to the new payment plan.
        assert_raises(
            logic.NotAuthorized,
            logic.get_action('user_create'),
            context,
            {'name': 'a-new-user',
             'password': 'a-password',
             'email': 'a-user@example.com',
             'payment_plan': 'enterprise'})

        # And just double-check the User wan't created.
        user = model.User.by_name('a-new-user')
        assert_equal(user, None)

    def test_user_create_with_invalid_payment_plan(self):
        '''Cannot create user with non-existant payment plan'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        # Now try to create a User, belonging to the new payment plan.
        assert_raises(
            logic.ValidationError,
            logic.get_action('user_create'),
            context,
            {'name': 'a-new-user',
             'password': 'a-password',
             'email': 'a-user@example.com',
             'payment_plan': 'does-not-exist'})

        # And just double-check the User wan't created.
        user = model.User.by_name('a-new-user')
        assert_equal(user, None)

    def test_user_update_without_payment_plan_as_sysadmin(self):
        '''Updating an existing user as sysadmin works as usual.'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        anna_id = model.User.by_name('annafan').id

        logic.get_action('user_update')(
            context,
            {'name': 'annafan',
             'id': anna_id,
             'email': 'a-user@example.com'})

        user = model.User.by_name('annafan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)
        assert_equal(user.email, 'a-user@example.com')

    def test_user_update_without_payment_plan_as_the_user(self):
        '''A user can update their own User as usual.'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'annafan',
        }

        anna_id = model.User.by_name('annafan').id

        logic.get_action('user_update')(
            context,
            {'name': 'annafan',
             'id': anna_id,
             'email': 'a-user@example.com'})

        user = model.User.by_name('annafan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)
        assert_equal(user.email, 'a-user@example.com')

    def test_user_update_with_null_payment_plan_as_sysadmin(self):
        '''Removing a user's payment plan as sysadmin is allowed'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        user_id = model.User.by_name('russianfan').id

        logic.get_action('user_update')(
            context,
            {'name': 'russianfan',
             'id': user_id,
             'email': 'russian_fan@example.com',
             'payment_plan': None})

        user = model.User.by_name('russianfan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)
        assert_equal(user.email, 'russian_fan@example.com')

    def test_user_update_with_valid_payment_plan_as_sysadmin(self):
        '''Setting a user's payment plan as sysadmin is allowed.'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        anna_id = model.User.by_name('annafan').id

        logic.get_action('user_update')(
            context,
            {'name': 'annafan',
             'id': anna_id,
             'payment_plan': 'individual',
             'email': 'a-user@example.com'})

        individual_plan = dh_models.PaymentPlan.by_name('individual')
        assert_not_equal(None, individual_plan)

        user = model.User.by_name('annafan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, individual_plan)
        assert_equal(user.email, 'a-user@example.com')

    def test_user_update_with_null_payment_plan_as_that_user(self):
        '''A user cannot remove their own payment plan'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'russianfan',
        }

        user_id = model.User.by_name('russianfan').id

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('user_update'),
            context,
            {'name': 'russianfan',
             'id': user_id,
             'email': 'russian_fan@example.com',
             'payment_plan': None})

        # Double check the User object.
        user = model.User.by_name('russianfan')
        assert_not_equal(user, None)
        assert_not_equal(user.payment_plan, None)
        assert_not_equal(user.email, 'russian_fan@example.com')

    def test_user_update_with_valid_payment_plan_as_that_user(self):
        '''A user cannot set their own payment plan.'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'annafan',
        }

        anna_id = model.User.by_name('annafan').id

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('user_update'),
            context,
            {'name': 'annafan',
             'id': anna_id,
             'payment_plan': 'individual',
             'email': 'a-user@example.com'})

        # Check the User model hasn't changed
        user = model.User.by_name('annafan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)
        assert_not_equal(user.email, 'a-user@example.com')

    def test_user_update_with_no_payment_plan_as_other_user(self):
        '''A user cannot update another user.'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'russianfan',
        }

        anna_id = model.User.by_name('annafan').id

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('user_update'),
            context,
            {'name': 'annafan',
             'id': anna_id,
             'email': 'a-user@example.com'})

        # Check the User model hasn't changed
        user = model.User.by_name('annafan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)
        assert_not_equal(user.email, 'a-user@example.com')

    def test_user_update_with_null_payment_plan_as_other_user(self):
        '''A user cannot remove another user's payment plan'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'annafan',
        }

        russian_id = model.User.by_name('russianfan').id

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('user_update'),
            context,
            {'name': 'russianfan',
             'id': russian_id,
             'payment_plan': None,
             'email': 'a-user@example.com'})

        # Check the User model hasn't changed
        user = model.User.by_name('russianfan')
        assert_not_equal(user, None)
        assert_not_equal(user.payment_plan, None)
        assert_not_equal(user.email, 'a-user@example.com')

    def test_user_update_with_valid_payment_plan_as_other_user(self):
        '''A user cannot set the payment plan of another user.'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'russianfan',
        }

        anna_id = model.User.by_name('annafan').id

        assert_raises(
            logic.NotAuthorized,
            logic.get_action('user_update'),
            context,
            {'name': 'annafan',
             'id': anna_id,
             'payment_plan': 'individual',
             'email': 'a-user@example.com'})

        # Check the User model hasn't changed
        user = model.User.by_name('annafan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, None)
        assert_not_equal(user.email, 'a-user@example.com')

    def test_user_update_with_invalid_payment_plan_as_sysadmin(self):
        '''Cannot move a user to a non-existant payment plan'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        russian_id = model.User.by_name('russianfan').id

        assert_raises(
            logic.ValidationError,
            logic.get_action('user_update'),
            context,
            {'name': 'russianfan',
             'id': russian_id,
             'payment_plan': 'does-not-exist',
             'email': 'a-user@example.com'})

        individual_plan = dh_models.PaymentPlan.by_name('individual')
        assert_not_equal(None, individual_plan)

        user = model.User.by_name('russianfan')
        assert_not_equal(user, None)
        assert_equal(user.payment_plan, individual_plan)
        assert_not_equal(user.email, 'a-user@example.com')

    def test_user_show_gives_sysadmins_a_users_payment_plan(self):
        '''A sysadmin can view another user's payment plan.'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        result = logic.get_action('user_show')(
            context,
            {'id': 'russianfan'})

        assert_equal(result['name'], 'russianfan')
        assert_equal(result['payment_plan']['name'], 'individual')

    def test_user_show_gives_owner_their_payment_plan(self):
        '''A user can view their own payment plan.'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': 'russianfan',
        }

        result = logic.get_action('user_show')(
            context,
            {'id': 'russianfan'})

        assert_equal(result['name'], 'russianfan')
        assert_equal(result['payment_plan']['name'], 'individual')

    def test_user_show_does_not_display_others_payment_plans(self):
        '''A user cannot view another user's payment plan.'''

        context = {
            'model': model,
            'session': model.Session,
            'user': 'annafan',
        }

        result = logic.get_action('user_show')(
            context,
            {'id': 'russianfan'})

        assert_equal(result['name'], 'russianfan')
        assert_not_in('payment_plan', result)

    def test_user_show_has_null_payment_plan_when_not_signed_up_to_one(self):
        '''When showing a  user without a payment plan, it should be None'''
        
        context = {
            'model': model,
            'session': model.Session,
            'user': 'testsysadmin',
        }

        result = logic.get_action('user_show')(
            context,
            {'id': 'annafan'})

        assert_equal(result['name'], 'annafan')
        assert_equal(result['payment_plan'], None)

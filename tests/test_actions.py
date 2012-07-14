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


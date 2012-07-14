from nose.tools import assert_equal

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


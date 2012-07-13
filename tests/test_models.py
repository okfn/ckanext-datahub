'''Testing the domain models specific to the datahub'''

from nose.tools import assert_equal

import ckan.model as model
import ckan.tests

import ckanext.datahub.models as dh_models

CreateTestData = ckan.tests.CreateTestData


class TestPaidService(object):

    @classmethod
    def setup_class(cls):
        dh_models.setup()

        CreateTestData.create_user('alice', password='pass')
        CreateTestData.create_user('bob', password='pass')

        small_biz = dh_models.PaidService(name="small-business")
        enterprise = dh_models.PaidService(name="enterprise")
        model.Session.add(small_biz)
        model.Session.add(enterprise)
        model.repo.commit_and_remove()

    def setUp(self):
        '''Assign alice to no paid service, and bob to enterprise level'''
        alice = model.User.by_name('alice')
        bob = model.User.by_name('bob')
        enterprise_service = dh_models.PaidService.by_name('enterprise')

        alice.paid_service = None
        bob.paid_service = enterprise_service
        model.repo.commit_and_remove()

    @classmethod
    def teardown_class(cls):
        model.Session.close_all()
        model.repo.clean_db()

    def test_users_created_with_no_paid_service(self):
        '''User's are, by default, created without a PaidService'''
        alice = model.User.by_name('alice')
        assert_equal(alice.paid_service, None)

    def test_users_can_belong_to_a_paid_service(self):
        enterprise_service = dh_models.PaidService.by_name("enterprise")
        bob = model.User.by_name('bob')
        assert_equal(bob.paid_service, enterprise_service)

    def test_users_can_change_paid_service(self):
        small_business = dh_models.PaidService.by_name('small-business')
        enterprise_service = dh_models.PaidService.by_name('enterprise')
        bob = model.User.by_name('bob')
        assert_equal(enterprise_service, bob.paid_service)

        bob.paid_service = small_business
        model.repo.commit_and_remove()

        bob = model.User.by_name('bob')
        assert_equal(small_business.id, bob.paid_service.id)
        assert_equal(small_business.name, bob.paid_service.name)

    def test_users_can_be_removed_from_a_paid_sevice(self):
        bob = model.User.by_name('bob')
        bob.paid_service = None
        model.repo.commit_and_remove()

        # reload bob
        bob = model.User.by_name('bob')
        assert_equal(bob.paid_service, None)

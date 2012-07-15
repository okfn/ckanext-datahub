'''Testing the domain models specific to the datahub'''

from nose.tools import assert_equal

import ckan.model as model
import ckan.tests

import ckanext.datahub.models as dh_models

CreateTestData = ckan.tests.CreateTestData


class TestPaymentPlan(object):

    @classmethod
    def setup_class(cls):
        dh_models.setup()

        CreateTestData.create_user('alice', password='pass')
        CreateTestData.create_user('bob', password='pass')

        small_biz = dh_models.PaymentPlan(name="small-business")
        enterprise = dh_models.PaymentPlan(name="enterprise")
        model.Session.add(small_biz)
        model.Session.add(enterprise)
        model.repo.commit_and_remove()

    def setUp(self):
        '''Assign alice to no payment plan, and bob to enterprise level'''
        alice = model.User.by_name('alice')
        bob = model.User.by_name('bob')
        enterprise_service = dh_models.PaymentPlan.by_name('enterprise')

        alice.payment_plan = None
        bob.payment_plan = enterprise_service
        model.repo.commit_and_remove()

    @classmethod
    def teardown_class(cls):
        model.Session.close_all()
        model.repo.clean_db()

    def test_users_created_with_no_payment_plan(self):
        '''User's are, by default, created without a PaymentPlan'''
        alice = model.User.by_name('alice')
        assert_equal(alice.payment_plan, None)

    def test_users_can_belong_to_a_payment_plan(self):
        enterprise_service = dh_models.PaymentPlan.by_name("enterprise")
        bob = model.User.by_name('bob')
        assert_equal(bob.payment_plan, enterprise_service)

    def test_users_can_change_payment_plan(self):
        small_business = dh_models.PaymentPlan.by_name('small-business')
        enterprise_service = dh_models.PaymentPlan.by_name('enterprise')
        bob = model.User.by_name('bob')
        assert_equal(enterprise_service, bob.payment_plan)

        bob.payment_plan = small_business
        model.repo.commit_and_remove()

        bob = model.User.by_name('bob')
        assert_equal(small_business.id, bob.payment_plan.id)
        assert_equal(small_business.name, bob.payment_plan.name)

    def test_users_can_be_removed_from_a_payment_plan(self):
        bob = model.User.by_name('bob')
        bob.payment_plan = None
        model.repo.commit_and_remove()

        # reload bob
        bob = model.User.by_name('bob')
        assert_equal(bob.payment_plan, None)

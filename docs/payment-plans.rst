=============
Payment Plans
=============

Models
------

The datahub extension introduces a new domain model, ``PaymentPlan``.  This has
many-one relationship from ``User`` to ``PaymentPlan``.  Currently the
``PaymentPlan`` table only has a single field, ``PaymentPlan.name``, which is
unique to each ``PaymentPlan``.  Also, each ``PaymentPlan`` has a ``.users``
attribute, which is a lazily-loaded join on the ``User`` table.  ``User``
objects have a new attribute defined on them by the mapper:
``User.payment_plan``.  This is a lazily-loaded ``PaymentPlan`` instance, and
may be ``None``.

For more information about the models, see ``ckanext/datahub/models.py``.

Logic Layer
-----------

The datahub extension defines new actions for managing payment plans and
membership.

========= ================================= ===================================
Module    Name                              Description
========= ================================= ===================================
create.py ``datahub_payment_plan_create``   Creates a new ``PaymentPlan`` with
                                            the given name.

get.py    ``datahub_payment_plan_show``     Returns dictized representation of
                                            a ``PaymentPlan`` identified by
                                            name.  This includes the users that
                                            are members of the plan.

get.py    ``datahub_payment_plan_list``     Returns a list of dictized
                                            ``PaymentPlan`` objects.  The list
                                            can be optionally filtered by a
                                            list of names.

update.py ``datahub_user_set_payment_plan`` Set a user's payment plan.  The
                                            user is identified by name in the
                                            ``user`` parameter, and the payment
                                            plan is identified by the name in
                                            the ``payment_plan`` parameter.
                                            The ``payment_plan`` argument may
                                            be ``None``, in which case the user
                                            will be removed from an existing
                                            payment plan.  The return value is
                                            a dictized presentation of the old
                                            payment plan, and the new payment
                                            plan, **without** existing members
                                            listed.
========= ================================= ===================================

The datahub extension alsoa overrides a couple of CKAN's standard logic
actions:

========= =============== =====================================================
Module    Name            Description
========= =============== =====================================================
update.py ``user_update`` In addition to the normal update action, a sysadmin
                          can set the payment plan of a ``User`` with this
                          action.  By specifiying a ``payment_plan`` field in
                          the data_dict to either an existing payment plan's
                          name, or the ``None`` value, the user's payment will
                          be set (or removed) accordingly.  If a sysadmin omits
                          the ``payment_plan`` field, then the payment plan is
                          not changed, allowing a non-sysadmin to update their
                          own user profile according to the core authorization
                          layer.

create.py ``user_create`` As with the above, a sysadmin can specify a user's
                          payment plan upon creation.  The ``payment_plan``
                          field must be a valid payment plan's name, or the
                          ``None`` value.  Omitting the argument makes no
                          attempt to set the payment plan, and allows a
                          non-sysamdin to create a new user.

get.py    ``user_show``   Override the normal ``user_show`` action to augment
                          the returned user dict with the payment plan the user
                          belongs to.  This additional information is only
                          available to the sysadmin or the owner of the user
                          account.  The dictized representation of the payment
                          plan does not include any membership information.
                          If the user doesn't belong to a payment plan, then
                          the returned payment plan value is ``None``.
========= =============== =====================================================

Authorization
-------------

Each of the datahub-specific auth logic functions described above has a related
authorization function.  They have been set up so that:

- Only sysadmins can create new payment plans.
- Only sysadmins can view all the members of a payment plan.
- Only sysadmins can assign users to payment plans.
- Only sysadmins can remove users from payment plans.
- A user can view the payment plan they belong to (if any), but they cannot
  view the other members of that plan.

Paster Commands
---------------

Management of payment plans is also available through some paster commands.  In
short, paster commands are available to create new payment plans; add and
remove users to existing payment plans; and listing users by payment plan.
Please run: ::

  paster datahub -c ../ckan/development.ini --help

for more details.


'''
Definition of tables and DomainObjects specific to the datahub.
'''
import logging

import sqlalchemy as sql
import sqlalchemy.orm as sql_orm
import sqlalchemy.sql.functions as sql_func

import ckan.model as model
import ckan.model.meta as db

_log = logging.getLogger(__name__)

# See ``_define_datahub_tables()`` for the details of these tables.
_datahub_migration_table = None
_datahub_paid_service_table = None
_datahub_paid_service_to_users_table = None

_DATAHUB_TABLES_VERSION = 1


def setup():
    '''Call this to ensure datahub-specific db tables exist and up to date'''
    # Setup table definitions in memory if not done so already.
    if _datahub_migration_table is None:
        _define_datahub_tables()

    if model.repo.are_tables_created():

        if not _datahub_migration_table.exists():
            _log.info('No datahub-specific tables exist.')
            _run_migration_step(0)

        for version in range(_current_migration_version(),
                             _DATAHUB_TABLES_VERSION):
            _run_migration_step(version + 1)
    else:
        _log.info('Datahub-specific table creation deferred.')

### Domain Model Definitions ###


class _MigrationVersion(model.domain_object.DomainObject):
    pass


class PaidService(model.domain_object.DomainObject):
    pass

### Private module-level helper functions ###


def _define_datahub_tables():
    '''Define the datahub tables in memory.'''

    global _datahub_paid_service_table
    global _datahub_paid_service_to_users_table
    global _datahub_migration_table

    # This table is used to track what migration step the datahub-specific
    # tables are currently at.  It's intended to only have a single row.
    _datahub_migration_table = sql.Table(
        'datahub_migrations', db.metadata,
        sql.Column('current_version',
                   sql.types.Integer,
                   nullable=False,
                   default=0,
                   primary_key=True),
    )

    # This table is a table of paid-for service levels for the datahub.
    # It's meant to be a linear hierarchy of levels, eg.
    #
    # basic account -> small business account -> enterprise account
    _datahub_paid_service_table = sql.Table(
        'datahub_paid_services', db.metadata,
        sql.Column('id',
                   sql.types.UnicodeText,
                   default=model.types.make_uuid,
                   nullable=False,
                   primary_key=True),
        sql.Column('name',
                   sql.types.UnicodeText,
                   sql.CheckConstraint("""name <> ''"""),
                   unique=True,
                   nullable=False),
    )

    # This table tracks which users have a paid-for service account, and
    # which level that account is.  Each user can have up to one paid-for
    # account.
    _datahub_paid_service_to_users_table = sql.Table(
        'datahub_paid_service_to_users', db.metadata,
        sql.Column('user_id',
                   sql.types.UnicodeText,
                   sql.ForeignKey('user.id'),
                   primary_key=True),
        sql.Column('paid_service_id',
                   sql.types.UnicodeText,
                   sql.ForeignKey('datahub_paid_services.id'),
                   nullable=False),
    )

    # Define the mappings between tables and domain objects.
    db.mapper(
        _MigrationVersion,
        _datahub_migration_table,
    )

    # The mapping between a PaidService and Users is through the
    # `_datahub_paid_service_to_users_table` table, despite being a 1-many
    # relationship from PaidService to User.  The reason for this is that we
    # don't want to alter the User table, as it may be altered independantly
    # by CKAN core library in the future.  And by normalizing out the
    # PaidService table, we can store further information against each
    # PaidService if we need to.
    #
    # paid_service_instance.users is all the Users that have paid for the
    # given paid service.  It is lazily loaded.
    #
    # user_instance.paid_service is the PaidService that the User belongs to,
    # or None if the User has not paid for any service.  Again, this is loaded
    # lazily.
    db.mapper(
        PaidService,
        _datahub_paid_service_table,
        properties={
            'users': sql_orm.relation(
                model.User,
                secondary=_datahub_paid_service_to_users_table,
                backref=sql_orm.backref(
                    'paid_service',
                    uselist=False,
                    lazy=True),
                lazy=True,
            ),
        }
    )


def _current_migration_version():
    return db.Session.query(sql_func.max(_MigrationVersion.current_version)) \
                     .scalar() or 0


def _run_migration_step(version):
    _log.info('Running datahub migration step %d', version)
    if version == 0:
        _migration_step_0()
    elif version == 1:
        _migration_step_1()
    else:
        raise Exception('Cannot run datahub migration step %d' % version)
    _set_migration_version(version)


def _set_migration_version(version):
    assert version <= _DATAHUB_TABLES_VERSION
    m = _MigrationVersion(current_version=version)
    m.save()
    _log.info('Set datahub migration version to %d', version)

### Migration steps ###


def _migration_step_0():
    _create_table(_datahub_migration_table)


def _migration_step_1():
    _create_table(_datahub_paid_service_table)
    _create_table(_datahub_paid_service_to_users_table)


def _create_table(t):
    if not t.exists():
        _log.info('Creating %s table', t.name)
        t.create()

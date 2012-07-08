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
_user_account_levels_table = None

_DATAHUB_TABLES_VERSION = 1

def setup():
    # Setup table definitions in memory if not done so already.
    if _datahub_migration_table is None:
        _define_datahub_tables()

    if model.repo.are_tables_created():

        if not _datahub_migration_table.exists():
            import pdb;pdb.set_trace()
            _log.debug('No datahub-specific tables exist.')
            _datahub_migration_table.create()

            m = _MigrationVersion(current_version=0)
            m.save()
            _log.debug('Created datahub_migration table')

        for version in range(_current_migration_version(),
                             _DATAHUB_TABLES_VERSION):
            _run_migration_step(version+1)
    else:
        _log.debug('Datahub-specific table creation deferred.')

def _define_datahub_tables():
    '''Define the datahub tables in memory.'''

    global _user_account_levels_table
    global _datahub_migration_table

    # This table is used to track what migration step the datahub-specific
    # tables are currently at.  It's intended to only have a single row.
    _datahub_migration_table = sql.Table('datahub_migrations', db.metadata,
        sql.Column('current_version',
                   sql.types.Integer,
                   nullable=False,
                   default=0,
                   primary_key=True),
    )

    # This table tracks which users have an account level above an unpaid
    # account level.  And which level that is.  It is assumed that there is a
    # 1-1 mapping between users and paid accounts.
    _user_account_levels_table = sql.Table('user_account_levels', db.metadata,
        sql.Column('user_id',
                   sql.types.UnicodeText,
                   sql.ForeignKey('user.id'),
                   primary_key=True),
        sql.Column('account_level',
                   sql.types.UnicodeText,
                   nullable=False),
    )

    # Define the mappings between tables and domain objects.
    db.mapper(
        _MigrationVersion,
        _datahub_migration_table,
    )

    db.mapper(
        PaidAccount,
        _user_account_levels_table,
        properties = {
            'user': sql_orm.relation(
                model.User,
                backref=sql_orm.backref(
                    'paid_account',
                    uselist=False,
                    lazy='joined'),
                lazy=True,
            ),
        }
    )

def _current_migration_version():
    return db.Session.query(sql_func.max(_MigrationVersion.current_version)) \
                     .scalar() or 0

def _run_migration_step(version):
    _log.debug('Running migration step %d', version)
    if version == 1:
        _migration_step_1()
    else:
        raise Exception('Cannot run datahub migration step %d' % version)

def _migration_step_1():
    _log.debug('Creating user_paid_service table.')
    _user_account_levels_table.create()

class _MigrationVersion(model.domain_object.DomainObject):
    pass

class PaidAccount(model.domain_object.DomainObject):
    pass


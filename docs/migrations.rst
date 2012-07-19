==========
Migrations
==========

Since the datahub extension maintains its own set of tables, it maintains a
migration version separate to that CKAN one.

The general idea is quite simple: the database maintains the table
``datahub_migrations``, which contains the latest migration version.  And the
software maintains a version in
``ckanext.datahub.models._DATAHUB_TABLES_VERSION``.  If, when the plugin is
loaded, the two are out of sync, then the database is brought up to date by
running a set of steps in ``ckanext.datahub.models``.  It's very simplified.
Doesn't allow for rolling back (ie - only `up steps` are defined, not `down
steps`.

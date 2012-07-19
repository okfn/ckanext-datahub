DataHub Extension
=================

This plugin provides customisation for DataHub.

CKAN Version: 1.8a

Enbaling the plugin
-------------------

To enable the plugin, add ``datahub`` to your list of plugins in you .ini file.

Testing
-------

To run tests, from within the ckanext-datahub directory: ::

  nosetests --ckan --with-pylons=test-core.ini tests/

Paster commands
---------------

The datahub provides a set of paster commands, to view them, run the following
from within root of the ckanext-datahub extension: ::

  paster datahub -c ../ckan/development.ini --help


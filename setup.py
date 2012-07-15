from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-datahub',
	version=version,
	description="Data Hub",
	long_description="""\
    Customisations for thedatahub.org
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='okfn',
	author_email='',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.datahub'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	    datahub=ckanext.datahub.plugin:DataHub

        [paste.paster_command]
        datahub=ckanext.datahub.commands:DatahubCommand
	""",
)

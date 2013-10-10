from setuptools import setup, find_packages

version = '0.2'

setup(
    name='ckanext-datahub',
    version=version,
    description="CKAN Datahub Extension",
    long_description='Customisations for datahub.io',
    classifiers=[],
    keywords='',
    author='Open Knowledge Foundation',
    author_email='datahub@okfn.org',
    url='http://datahub.io',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.datahub'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points='''
        [ckan.plugins]
        datahub=ckanext.datahub.plugin:DataHub

        [paste.paster_command]
        datahub=ckanext.datahub.commands.datahub:DatahubCommand
        org_upgrade=ckanext.datahub.commands.upgrade:OrgUpgradeCommand
    ''',
)

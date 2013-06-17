from setuptools import setup, find_packages

version = '0.2'

setup(
    name='ckanext-datahub',
    version=version,
    description="Data Hub",
    long_description="""\
    Customisations for thedatahub.org
    """,
    classifiers=[],
    keywords='',
    author='okfn',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.datahub'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points=\
    """
        [ckan.plugins]
        datahub=ckanext.datahub.plugin:DataHub
    """,
)

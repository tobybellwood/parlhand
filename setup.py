import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-parl-hand',
    version='0.0.1a1',
    packages=['parlhand'],
    include_package_data=True,
    license='',  # example license
    description='',
    long_description=README,
    url='',
    author='',
    author_email='samuel.spencer@aph.gov.au',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        "Django>=1.7",
        'pytz',

        'django-model-utils',

        #Search requirements
        'django-haystack',
        'Whoosh',

        #Rich text editors
        #'django-ckeditor',
        'django-spaghetti-and-meatballs',
        
        #Geospatial
        'gdal',

        # Revision control
        "django-reversion>=1.8",
        'django-reversion-compare>=0.5.2',
        'diff-match-patch',

        # Fancy UI stuff
        'django-autocomplete-light',

        #API
        'djangorestframework',
        
        #importer libraries
        'lxml'
        'beautifulsoup4'

    ],

)

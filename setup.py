import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(HERE, 'README.md')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.md')).read()

setup(
    name='django-datastore',
    version=open(os.path.join(HERE, 'datastore', 'VERSION.md')).read().strip(),
    include_package_data=True,
    author='Makina Corpus',
    author_email='terralego-pypi@makina-corpus.com',
    description="Generic data store for Django Rest framework",
    long_description=README + '\n\n' + CHANGES,
    description_content_type="text/markdown",
    long_description_content_type="text/markdown",
    license="MIT, see LICENSE file.",
    packages=find_packages(),
    url='https://github.com/Terralego/django-datastore',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
    ],
    install_requires=[
        'django>=2.2',
        'psycopg2',  # postgres is required to use JSONField
        'djangorestframework',
        'python-magic>=0.4,<0.5',
    ],
    extras_require={
        'dev': [
            'flake8',
            'coverage',
        ]
    }
)

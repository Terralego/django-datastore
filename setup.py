
import os
from setuptools import setup, find_packages
import sys

file_setup = os.path.abspath(os.path.dirname(__file__))
import codecs

requires = ['Django>=2.0,<2.1', 'djangorestframework>=3.7,<3.8', 'python-magic>=0.4,<0.5']

setup(
        name='django-rest-datastore',
        version='0.1.dev0',
        author='Makina Corpus',
        author_email='terralego-pypi@makina-corpus.com',
        url='https://github.com/makinacorpus/django-datastore',
        download_url="",
        description="",
        long_description=codecs.open(
            os.path.join(
                file_setup, 'README.rst'), 'r', 'utf-8').read() + '\n\n' +
                         codecs.open(
                             os.path.join(file_setup, 'CHANGES'),
                             'r', 'utf-8').read(),
        license='MIT, see LICENSE file.',
        install_requires=requires,
        packages=find_packages(exclude=("tests",)),
        include_package_data=True,
        zip_safe=False,
        classifiers=['Topic :: Utilities',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Intended Audience :: Developers',
                     'Environment :: Web Environment',
                     'Framework :: Django',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7'],
)

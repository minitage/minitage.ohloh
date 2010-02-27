import os, sys
from setuptools import setup, find_packages
setupdir = os.path.abspath(
    os.path.dirname(__file__)
)
os.chdir(setupdir)

name='minitage.ohloh'
version = '1.0'

def read(*rnames):
    return open(
        os.path.join(setupdir, *rnames)
    ).read()

long_description = (
    read('README.txt')
    + '\n'\
    + read('CHANGES.txt')
    + '\n'
)


long_description = 'ohloh minitage helpers'

setup(
    name=name,
    version=version,
    description="",
    long_description= long_description,
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='ohloh',
    author='Mathieu Pasquet',
    author_email='kiorky@cryptelium.net',
    url='http://cheeseshop.python.org/pypi/%s' % name,
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['minitage', name],
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        'zc.buildout',
        'lxml',
        'elementtree',
        'windmill',
        'zope.testbrowser',
        #'oauth2',
    ],
    extras_require={'test': ['IPython', 'zope.testing', 'mocker']},
    entry_points = {
        'console_scripts' : [
            'ohloh.register_repo = %s.ohloh:register_repo' % name
        ]
    },
)



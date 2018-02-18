import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'readme.md')) as f:
    README = f.read()
with open(os.path.join(here, 'changes.md')) as f:
    CHANGES = f.read()

requires = [
    'alembic',
    'apache-libcloud',
    'bcrypt',
    'celery',
    'lockfile',
    'marshmallow',
    'Pillow',
    'plaster_pastedeploy',
    'pyexifinfo',
    'psycopg2',
    'python-memcached',
    'python-slugify',
    'pytz',
    'pyramid >= 1.9a',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_jwt',
    'pyramid_ipython',
    'pyramid_multiauth',
    'pyramid_retry',
    'pyramid_tm',
    'redis',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
]

setup(
    name='www',
    version='0.1',
    description='www',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Tom Peters',
    author_email='tjpeters@petersrock.com',
    url='https://www.github.com/',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = www:main',
        ],
        'console_scripts': [
            'initialize_www_db = www.scripts.initializedb:main',
            'test_data = www.scripts.testdata:main',
        ],
    },
)
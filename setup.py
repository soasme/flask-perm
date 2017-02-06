"""
A permission flask extension inspired by Django.
"""

from setuptools import setup


setup(
    name='Flask-Perm',
    version='0.2.8',
    url='https://github.com/soasme/flask-perm',
    license='MIT',
    author='Ju Lin',
    author_email='soasme@gmail.com',
    description='Flask Permission Management Extension',
    long_description=__doc__,
    packages=['flask_perm'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Bcrypt',
    ],
    classifiers=[
        'Framework :: Flask',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

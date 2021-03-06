from setuptools import setup, find_packages
from helga_quest import __version__ as version


setup(
    name='helga-quest',
    version=version,
    description=('Collaborative RPG consisting of user driven content'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat :: Internet Relay Chat'],
    keywords='irc bot quest',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    url='https://github.com/narfman0/helga-quest',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['helga_quest.plugin'],
    zip_safe=True,
    install_requires=['helga', 'jaraco.modb'],
    test_suite='tests',
    entry_points = dict(
        helga_plugins=[
            'quest = helga_quest.plugin:quest',
        ],
    ),
)

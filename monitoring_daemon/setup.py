import os
import subprocess
from setuptools.command.install import install
from setuptools import setup, Extension, Command, find_packages

PROJECT_NAME = 'monitoring_daemon'
PROJECT_VERSION = '0.3'
PROJECT_SETUP_DIR = os.path.abspath(os.path.dirname(__file__))


# Installation of psutil is broken
# forcing to use pip3
def _psutil_install():
    from subprocess import call
    call(['pip3', 'install', 'psutil'])


class InstallCommand(install):
    def run(self):
        self.execute(_psutil_install, [],
                     msg="Running installation of psutil")
        install.run(self)


class CleanCommand(Command):
    description = "Removes dist/build directories"
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system('rm -rf ./build ./dist')


setup(
    # package_dir={'': '..'},
    packages=find_packages(),
    scripts=['scripts/monitoring_daemon'],
    name=PROJECT_NAME,
    version=PROJECT_VERSION,
    author='Pace Francesco',
    author_email='francesco.pace@eurecom.fr',
    maintainer='Pace Francesco',
    maintainer_email='francesco.pace@eurecom.fr',
    platforms='Linux',
    # ext_modules=[Extension('processEvents',
    #                        [os.path.join(PROJECT_SETUP_DIR,'src', 'c', 'processEvents.c')])],
    setup_requires=[
    ],
    install_requires=[
        # Installation of psutil is broken
        # 'psutil>=4.0.0',
    ],
    cmdclass={
        'install': InstallCommand,
        'clean': CleanCommand,
    },
    zip_safe=True,
)

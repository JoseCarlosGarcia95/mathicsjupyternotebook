#!/usr/bin/env python

import sys
import subprocess

from distutils import log

from setuptools import setup
from setuptools.command.install import install

# General Requirements
SETUP_REQUIRES = ['ipython', 'ipykernel']

INSTALL_REQUIRES = ['mathics>=1.0.dev0'] + SETUP_REQUIRES


kernel_json = {
    'argv': [sys.executable,
             '-m', 'mathicsnotebook',
             '-f', '{connection_file}'],
    'display_name': 'MathicsKernel',
    'language': 'Mathematica',
    'name': 'mathicsnotebook',
}


class InstallIMathics(install):

    def run(self):
        # The recommended way is with the setup_requires argument to setup
        # This fails because ipython doesn't build under easy_install
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + SETUP_REQUIRES)

        # Unfortunately the recommended call to 'install.run(self)'
        # will completely ignore the install_requirements.
        # So we trick it by calling the underlying bdist_egg instead:
        self.do_egg_install()

        self.install_kernelspec()

    def install_kernelspec(self):
        from ipykernel.kernelspec import write_kernel_spec
        from jupyter_client.kernelspec import KernelSpecManager

        kernel_spec_manager = KernelSpecManager()

        log.info('Writing kernel spec')
        kernel_spec_path = write_kernel_spec(overrides=kernel_json)

        log.info('Installing kernel spec ' + kernel_spec_path)
        try:
            kernel_spec_manager.install_kernel_spec(
                kernel_spec_path,
                kernel_name=kernel_json['name'],
                user=self.user)
        except Exception as e:
            log.error(str(e.args))
            log.error('Failed to install kernel spec')
        else:
            return

        # retry with not self.user
        log.info('Retry install kernel spec')
        try:
            kernel_spec_manager.install_kernel_spec(
                kernel_spec_path,
                kernel_name=kernel_json['name'],
                user=not self.user)
        except Exception as e:
            log.error(str(e.args))
            log.error('Failed to install kernel spec')

setup(
    name="mathicsnotebook",
    cmdclass={'install': InstallIMathics},
    version='0.1',

    packages=['mathicsnotebook'],

    install_requires=INSTALL_REQUIRES,
)

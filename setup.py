from __future__ import print_function

import os
import stat
import shutil
import urllib
import zipfile
import platform

from distutils.command.build import build
from setuptools.command.install import install
from setuptools import setup, find_packages

def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# For building Malmo
class BuildMalmo(build):
    def run(self):
        from future.moves.urllib.request import urlretrieve

        if os.path.exists('minecraft_py/Malmo'):
            print("Removing existing Malmo folder...")
            shutil.rmtree('minecraft_py/Malmo')

        system = platform.system()
        bits, linkage = platform.architecture()
        if system == 'Linux':
            dist, version, vername = platform.linux_distribution()
            folder = 'Malmo-0.17.0-{}-{}-{}-{}'.format(system, dist, version, bits)
        else:
            folder = 'Malmo-0.17.0-{}-{}'.format(system, bits)
        url = 'https://github.com/Microsoft/malmo/releases/download/0.17.0/{}.zip'.format(folder)

        print("Downloading Malmo...")
        urlretrieve(url, 'Malmo.zip')
        
        print("Unzipping Malmo...")
        zip = zipfile.ZipFile('Malmo.zip')
        zip.extractall('minecraft_py')
        zip.close()
        
        print("Removing zip...")
        os.remove('Malmo.zip')
        print("Renaming folder...")
        os.rename(os.path.join('minecraft_py', folder), 'minecraft_py/Malmo')

        print("Changing permissions...")
        make_executable('minecraft_py/Malmo/Minecraft/gradlew')
        make_executable('minecraft_py/Malmo/Minecraft/launchClient.sh')

        build.run(self)


setup(name='minecraft-py',
      version='0.0.2',
      description='Python bindings for Malmo',
      url='https://github.com/tambetm/minecraft-py',
      author='Tambet Matiisen',
      author_email='tambet.matiisen@gmail.com',
      packages=find_packages(),
      cmdclass={'build_ext': BuildMalmo},
      setup_requires=['future'],
      include_package_data=True,
      zip_safe=False
)

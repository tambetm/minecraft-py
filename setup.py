from __future__ import print_function

import os
import sys
import stat
import time
import shutil
import urllib
import zipfile
import platform
import subprocess

from distutils.command.build import build
from setuptools.command.install import install
from setuptools import setup, find_packages


def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# For building Malmo


class BuildMalmo(build):
    def run(self):
        # abort if a global Malmo installation already exists and just use that
        if "MALMO_XSD_PATH" in os.environ:
            build.run(self)
            return

        # otherwise, install a new local Malmo
        from future.moves.urllib.request import urlretrieve

        malmo_ver = '0.37.0'

        if os.path.exists('minecraft_py/Malmo'):
            print("Removing existing Malmo folder...")
            shutil.rmtree('minecraft_py/Malmo')

        if os.path.exists('betterfps'):
            print("Removing existing betterfps folder...")
            shutil.rmtree('betterfps')

        system = platform.system()
        bits, linkage = platform.architecture()
        if system == 'Linux':
            dist, version, vername = platform.linux_distribution()
            folder = 'Malmo-{}-{}-{}-{}-{}'.format(
                malmo_ver, system, dist, version, bits)
        elif system == 'Darwin':
            folder = 'Malmo-{}-Mac-{}'.format(malmo_ver, bits)
        else:
            folder = 'Malmo-{}-{}-{}'.format(malmo_ver, system, bits)

        if malmo_ver in ['0.21.0', '0.22.0', '0.30.0']:
            folder += '_withBoost'
        elif int(malmo_ver.split('.')[1]) >= 31:
            # since 0.31.0
            folder += '_withBoost_Python{}.{}'.format(
                sys.version_info[0], sys.version_info[1])

        url = 'https://github.com/Microsoft/malmo/releases/download/{}/{}.zip'.format(
            malmo_ver, folder)

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

        # get betterfps
        betterfps_version = '1.4.5'
        betterfps_branch = '1.11'
        print('Downloading BetterFps for MC {}...'.format(betterfps_branch))
        urlretrieve('https://codeload.github.com/Guichaguri/BetterFps/zip/{}'.format(betterfps_branch), 'BetterFps.zip')

        print("Unzipping BetterFps...")
        zip = zipfile.ZipFile('BetterFps.zip')
        zip.extractall('.')
        zip.close()
        os.remove('BetterFps.zip')
        os.rename('BetterFps-{}'.format(betterfps_branch), 'betterfps')

        print("Copying gradlew for BetterFps...")
        shutil.copy('minecraft_py/Malmo/Minecraft/gradlew', 'betterfps')
        shutil.copy('minecraft_py/Malmo/Minecraft/gradlew.bat', 'betterfps')
        shutil.copytree('minecraft_py/Malmo/Minecraft/gradle', 'betterfps/gradle')

        if platform.system() == 'Windows':
            gradle = 'gradlew'
        else:
            gradle = './gradlew'

        print('Building deobfuscated betterfps jar...')
        os.chdir('betterfps')
        os.system(gradle + ' jar')
        os.chdir('..')

        print('Copying betterfps jar to mods folder...')
        os.makedirs('minecraft_py/Malmo/Minecraft/run/mods')
        shutil.copy('betterfps/build/libs/BetterFps-{}.jar'.format(betterfps_version), 'minecraft_py/Malmo/Minecraft/run/mods')

        print('Cleaning up build directory...')
        shutil.rmtree('betterfps')

        # Prevent race condition
        time.sleep(0.1)

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
      install_requires=['psutil'],
      include_package_data=True,
      zip_safe=False
      )

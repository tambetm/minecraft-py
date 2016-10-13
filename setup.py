from __future__ import print_function
from future.moves.urllib.request import urlretrieve
import os
import sys
import stat
import shutil
import shlex
import subprocess
import urllib
import zipfile

from distutils.command.build import build
from setuptools.command.install import install
from setuptools import setup, find_packages

def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def run_command(command, cwd=None, env=None):
    if env:
      origenv = os.environ.copy()
      origenv.update(env)
      env = origenv
    args = shlex.split(command)
    proc = subprocess.Popen(args, cwd=cwd, env=env)
    proc.wait()

# For building Malmo
class BuildMalmo(build):
    def run(self):

        if os.path.exists('minecraft_py/Malmo'):
            print("Removing existing Malmo folder...")
            shutil.rmtree('minecraft_py/Malmo')

        if os.path.exists('minecraft_py/MalmoPython.so'):
            print("Removing existing MalmoPython.so")
            os.remove("minecraft_py/MalmoPython.so")

        # TODO: should detect the OS?
        print("Downloading Malmo...")
        urlretrieve('https://github.com/Microsoft/malmo/releases/download/0.17.0/Malmo-0.17.0-Linux-Ubuntu-14.04-64bit.zip', 'Malmo.zip')
        
        print("Unzipping Malmo...")
        zip = zipfile.ZipFile('Malmo.zip')
        zip.extractall('minecraft_py')
        zip.close()
        
        print("Removing zip...")
        os.remove('Malmo.zip')
        print("Renaming folder...")
        os.rename('minecraft_py/Malmo-0.17.0-Linux-Ubuntu-14.04-64bit', 'minecraft_py/Malmo')

        print("Changing permissions...")
        make_executable('minecraft_py/Malmo/Minecraft/gradlew')
        make_executable('minecraft_py/Malmo/Minecraft/launchClient.sh')

        print("Moving MalmoPython.so...")
        shutil.move("minecraft_py/Malmo/Python_Examples/MalmoPython.so", "minecraft_py")

        build.run(self)

class InstallMalmo(install):
    def run(self):

        install.run(self)

        print("Precompiling...")
        run_command("./gradlew setupDecompWorkspace", cwd='minecraft_py/Malmo/Minecraft', env={'MALMO_XSD_PATH': 'minecraft_py/Malmo/Schemas'})
        run_command("./gradlew build", cwd='minecraft_py/Malmo/Minecraft', env={'MALMO_XSD_PATH': 'minecraft_py/Malmo/Schemas'})

setup(name='minecraft-py',
      version='0.0.1',
      description='Python bindings to Malmo',
      url='https://github.com/tambetm/minecraft-py',
      author='Tambet Matiisen',
      author_email='tambet.matiisen@gmail.com',
      packages=find_packages(),
      cmdclass={'build': BuildMalmo, 'install': InstallMalmo},
      include_package_data=True,
      zip_safe=False
)

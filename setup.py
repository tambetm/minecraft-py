import os
import sys
import stat
import shutil
import shlex
import subprocess
import urllib
import zipfile

from distutils.command.build import build as DistutilsBuild
from setuptools import setup, find_packages

def make_abs_path(path):
    return os.path.join(os.dirname(__file__), path)

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
class BuildMalmo(DistutilsBuild):
    def run(self):
        if os.path.exists('minecraft_py/Malmo'):
            print "Removing existing folder..."
            shutil.rmtree('minecraft_py/Malmo')

        # TODO: should detect the OS?
        print "Downloading Malmo..."
        urllib.urlretrieve('https://github.com/Microsoft/malmo/releases/download/0.17.0/Malmo-0.17.0-Linux-Ubuntu-14.04-64bit.zip', 'Malmo.zip')
        
        print "Unzipping Malmo..."
        zip = zipfile.ZipFile('Malmo.zip')
        zip.extractall('minecraft_py')
        zip.close()
        
        print "Removing zip..."
        os.remove('Malmo.zip')
        print "Renaming folder..."
        os.rename('minecraft_py/Malmo-0.17.0-Linux-Ubuntu-14.04-64bit', 'minecraft_py/Malmo')

        print "Changing permissions..."
        make_executable('minecraft_py/Malmo/Minecraft/gradlew')
        make_executable('minecraft_py/Malmo/Minecraft/launchClient.sh')

        print "Precompiling..."
        run_command("./gradlew setupDecompWorkspace", cwd='minecraft_py/Malmo/Minecraft', env={'MALMO_XSD_PATH': 'minecraft_py/Malmo/Schemas'})
        run_command("./gradlew build", cwd='minecraft_py/Malmo/Minecraft', env={'MALMO_XSD_PATH': 'minecraft_py/Malmo/Schemas'})

        DistutilsBuild.run(self)

setup(name='minecraft-py',
      version='0.0.1',
      description='Python bindings to Malmo',
      url='https://github.com/tambetm/minecraft-py',
      author='Tambet Matiisen',
      author_email='tambet.matiisen@gmail.com',
      packages=find_packages(),
      cmdclass={'build': BuildMalmo},
      package_data={'': [
          'Malmo/*',
          'Malmo/Minecraft/*',
          'Malmo/Minecraft/*/*',
          'Malmo/Minecraft/*/*/*',
          'Malmo/Minecraft/*/*/*/*',
          'Malmo/Mod/*',
          'Malmo/Schemas/*'
          ]},
      classifiers=['License :: OSI Approved :: MIT License'],
      zip_safe=False,
)

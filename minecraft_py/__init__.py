import os
import sys
import shlex
import logging
import subprocess
import signal
import socket
import platform

logger = logging.getLogger(__name__)

# determine Malmo location and executable name
malmo_dir = os.path.join(os.path.dirname(__file__), 'Malmo')
if sys.platform.startswith('win'):
    mc_command = os.path.join(malmo_dir, 'Minecraft', 'launchClient.bat')
else:
    mc_command = os.path.join(malmo_dir, 'Minecraft', 'launchClient.sh')

# set MALMO_XSD_PATH environment variable
malmo_xsd_path = os.path.join(malmo_dir, 'Schemas')
os.environ['MALMO_XSD_PATH'] = malmo_xsd_path

# add MalmoPython to PYTHONPATH
malmo_python_path = os.path.join(malmo_dir, 'Python_Examples')
sys.path.append(malmo_python_path)

def is_port_taken(port, address='0.0.0.0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((address, port))
        taken = False
    except socket.error as e:
        if e.errno == 98:
            taken = True
        else:
            raise e

    s.close()
    return taken

def start(port=None):
    # if no port was given, find the first free port starting from 10000
    if not port:
        port = 10000
        while is_port_taken(port):
            port += 1

    # start Minecraft process
    cmd = mc_command + " -port " + str(port)
    logger.info("Starting Minecraft process: " + cmd)
    args = shlex.split(cmd)
    proc = subprocess.Popen(args,
            # pipe entire output
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            # use process group, see http://stackoverflow.com/a/4791612/18576
            preexec_fn=os.setsid)
    # wait until Minecraft process has outputed "CLIENT enter state: DORMANT"
    while True:
        line = proc.stdout.readline()
        logger.debug(line)
        if not line:
            raise EOFError("Minecraft process finished unexpectedly")
        if b"CLIENT enter state: DORMANT" in line:
            break
    logger.info("Minecraft process ready")
    # supress entire output, otherwise the subprocess will block
    # NB! there will be still logs under Malmo/Minecraft/run/logs
    FNULL = open(os.devnull, 'w')
    proc.stdout = FNULL
    return proc, port

def stop(proc):
    # send SIGTERM to entire process group, see http://stackoverflow.com/a/4791612/18576
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    logger.info("Minecraft process terminated")

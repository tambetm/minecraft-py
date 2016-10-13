import os
import shlex
import logging
import subprocess
import signal

logger = logging.getLogger(__name__)

malmo_dir = os.path.join(os.path.dirname(__file__), 'Malmo')
mc_command = os.path.join(malmo_dir, 'Minecraft/launchClient.sh')

def start(port=None):
    cmd = mc_command
    if port:
        cmd += " -port %d" % port
	logger.info("Starting Minecraft process: " + cmd)
    FNULL = open(os.devnull, 'w')
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
        if "CLIENT enter state: DORMANT" in line:
            break
    logger.info("Minecraft process ready")
    # supress entire output, otherwise the subprocess will block
    proc.stdout = FNULL
    return proc

def stop(proc):
    # send SIGTERM to entire process group, see http://stackoverflow.com/a/4791612/18576
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    logger.info("Minecraft process terminated")

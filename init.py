import logging
logging.basicConfig(level=logging.DEBUG)

import minecraft_py

proc, port = minecraft_py.start()
minecraft_py.stop(proc)

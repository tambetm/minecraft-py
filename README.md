# minecraft_py

Python wrapper for [Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research built on top of Minecraft.

## Installation

1. Install the dependencies for your OS: [Windows](https://github.com/Microsoft/malmo/blob/master/doc/install_windows.md), [Linux](https://github.com/Microsoft/malmo/blob/master/doc/install_linux.md), [MacOSX](https://github.com/Microsoft/malmo/blob/master/doc/install_macosx.md). You can skip Torch, Mono and ALE parts.

2. Install the package itself:

  ```
git clone https://github.com/tambetm/minecraft-py.git
cd minecraft-py
pip install -e .
```

  Installation automatically downloads the appropriate Malmo version and unzips it to package directory.

3. To precompile Minecraft classes so that subsequent starts will be faster run following snippet:
  ```
import logging
logging.basicConfig(level=logging.DEBUG)

import minecraft_py

proc, port = minecraft_py.start()
minecraft_py.stop(proc)
```

  Basically Minecraft downloads and compiles everything on first start, this snippet just starts it in debug mode, so you can see if it gets stuck. You can use similar snippet later to start and stop the Minecraft process.

## Usage

`minecraft_py` module exposes following functions:
 * `proc, port = start(port=None)` - start a new Minecraft process. If port argument is given, it determines the port that Malmo is going to listen, otherwise the first free port starting from 10000 is used. Returns process object and port.
 * `stop(proc)` - stops Minecraft started previously with `start()`. Sends `SIGTERM` to entire process group.
 
In addition it adds `MalmoPython` module to `PYTHONPATH` that can be used to communicate with Minecraft process. `MalmoPython` API follows the [Malmo C++ API](http://microsoft.github.io/malmo/0.17.0/Documentation/annotated.html). You can also check the [tutorial](http://microsoft.github.io/malmo/0.17.0/Python_Examples/Tutorial.pdf) and [examples](https://github.com/Microsoft/malmo/tree/master/Malmo/samples/Python_examples).

## Known issues

 * Python 3 is not supported as Microsoft doesn't provide precompiled binaries for Python 3.

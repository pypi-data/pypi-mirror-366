# For Maintainers

The name of the package is `roverlib` which is the same as the module that is then imported by end users (`pip install roverlib` and `import roverlib` to keep consistency). 

The following directory structure aims to separate library code from testing code:
* `src/roverlib` - contains all source code of the library
* `tests/` - contains python files that will all be part of the testing process

This repository is self-contained and relies heavily on `uv` for dependency management and building packages. The most important commands are wrapped by Makefile targets:

* `make build` - builds the library to `dist/` and installs it locally for quick testing
* `make test` - runs all files in the `tests/` directory
* `make publish-test` - requires setting an external token with `export UV_PUBLISH_TOKEN=pypi-abc...` and uploads to pypi's test
* `make publish` - requires setting an external token with `export UV_PUBLISH_TOKEN=pypi-def...` and uploads to the official pypi index

Before running the `make publish*` targets, make sure to set the correct token depending on which index you are uploading to.


# What to do when the bootspec updates


Copy the roverd bootspec JSON schema from https://github.com/VU-ASE/rover/blob/main/spec/service-boot/schema.json. Then use the quicktype cJSON generator to generate the Python code at https://app.quicktype.io/. Use the following settings: 
- Make sure to specify:
    - Name = Service
    - Source type = JSON Schema

Paste it into [`src/roverlib/bootinfo.py`](https://github.com/VU-ASE/roverlib-python/blob/main/src/roverlib/bootinfo.py)

# What to do when rovercom updates

Copy and paste the contents from the [rovercom definitions](https://github.com/VU-ASE/rovercom/blob/main/packages/python/gen/protobuf_msgs.py) to the [`src/roverlib/rovercom.py`](https://github.com/VU-ASE/roverlib-python/blob/main/src/roverlib/rovercom.py) file.



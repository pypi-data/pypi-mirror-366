# Installation

:::info[Recommended approach]

It is not recommended to install this library manually. Instead, you can initialize a Python service using `roverctl` using [this command](https://ase.vu.nl/docs/framework/Software/rover/roverctl/usage/#initialize-a-service).

:::

The `roverlib-python` library comes installed by default on every Rover, but if for some reason it isn't, [ssh into the rover](https://ase.vu.nl/docs/tutorials/Fundamental%20Concepts/connecting) and run the following pip install command:

``` bash
# Install the latest version
pip install roverlib
# Install a specific version
pip install roverlib==1.2.3
```

Using the same commands, you can update or downgrade `roverlib-pyton` globally on the Rover. All available versions that can be installed can be found [here](https://pypi.org/project/roverlib/#history).

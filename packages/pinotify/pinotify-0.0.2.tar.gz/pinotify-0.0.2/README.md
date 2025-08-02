# RPi Pin Watcher

This is a small software for receiving notification of a Raspberry Pi (RPi)
pin change through [libgpiod][libgpiod]. This software monitor the voltage fall
of pin 17. Optionally, this software may run another application through the
`--command` flag.

Initially this was written for hooking a wireless doorbell receiver to an RPi
and then trying to capture electirc signal when the doorbell button is triggered.

The software make use of the new [libgpiod][libgpiod] interface with the
[official Python binding library][libgpiod-python].

[libgpiod]: https://libgpiod.readthedocs.io/
[libgpiod-python]: (https://libgpiod.readthedocs.io/en/latest/python_api.html)


## Installation

Clone the repository. Then install the requirements:

```
pip install -r requirements.txt
```


## Usage

```
usage: python3 -m pinotify [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--exec COMMAND] [--pin PIN]

Set logging level for the application.

options:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --exec COMMAND        Command to run when edge event is triggered. In JSON array format.
                        Example: '["echo", "bell rang!"]'.
  --pin PIN             Integer. Set the GPIO pin number to monitor. Default: 17.
```

## License

This software is licensed under the [MIT License](https://mit-license.org/).
A copy of the license can be obtained in the repository at [LICENSE.md](LICENSE.md).

import argparse
from collections.abc import Callable
from datetime import timedelta
import gpiod
import json
import logging
import subprocess
import sys
from typing import List
from gpiod.line import Bias, Edge
from .lib.graceful_actor import GracefulActor

def edge_type_str(event):
    if event.event_type is event.Type.RISING_EDGE:
        return "Rising"
    if event.event_type is event.Type.FALLING_EDGE:
        return "Falling"
    return "Unknown"

def print_event(event):
    logger.info(
        "line: {}  type: {:<7}  event #{}".format(
            event.line_offset, edge_type_str(event), event.line_seqno
        )
    )

def parse_json_list(string: str) -> List[str]:
    # Parse the JSON string
    parsed_list = json.loads(string)

    # Check if the parsed result is a list
    if isinstance(parsed_list, list):
        return parsed_list
    else:
        raise ValueError("Parsed JSON is not a list")

def command_runner(command: List[str], logger: logging.Logger):
    def cb(*args, **kwargs):
        try:
            # Run the command and capture the output
            logger.info("run_command: {}".format(command))
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            logger.debug("run_command output: {}".format(result.stdout))  # Print the standard output
        except subprocess.CalledProcessError as e:
            logger.error(f"An error occurred: {e.stderr}")  # Print the error if the command fails
    return cb

def watch_line(
    line: int,
    event_handler: Callable,
    consumer: str = '',
    chip_path: str = '/dev/gpiochip0',
    edge_detection: Edge = Edge.NONE,
    bias: Bias = Bias.AS_IS,
):
    with gpiod.request_lines(
        chip_path,
        consumer=consumer,
        config={
            line: gpiod.LineSettings(
                edge_detection=edge_detection,
                bias=bias,
                debounce_period=timedelta(milliseconds=10),
            )
        },
    ) as request:
        while True:
            for event in request.read_edge_events():
                event_handler(event)

if __name__ == '__main__':

    CHIP_PATH = '/dev/gpiochip0' # The default for RPi 5
    DEFAULT_LINE = 17 # Use the GPIO Pin 17 for this project

    parser = argparse.ArgumentParser(description="Set logging level for the application.")
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    )
    parser.add_argument(
        '--exec',
        type=str,
        default='["echo", "bell rang!"]',
        help="Command to run when edge event is triggered. In JSON array format. "
            "Example: '[\"echo\", \"bell rang!\"]'.",
    )
    parser.add_argument(
        '--pin',
        type=int,
        default=DEFAULT_LINE,
        help='Integer. Set the GPIO pin number to monitor. Default: 17.',
    )
    args = parser.parse_args(sys.argv[1:])

    # Setup for logging
    logger = logging.getLogger(__name__)
    logger.setLevel(args.log_level.upper())
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(args.log_level.upper())
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Parse args.command as JSON array
    exec = parse_json_list(args.exec)
    logger.debug('exec: {}'.format(args.exec))
    logger.debug('exec parsed: {}'.format(exec))

    # Check if the chip is ready
    if not gpiod.is_gpiochip_device(CHIP_PATH):
        logger.error('chip not found: {}'.format(CHIP_PATH))
        sys.exit(1)
    else:
        logger.info('chip ready: {}'.format(CHIP_PATH))

    # Log the chip information
    chip = gpiod.Chip(CHIP_PATH)
    logger.debug('chip info: %s' % (chip.get_info()))

    # Watch the specific chip line
    watch_line(
        chip_path=CHIP_PATH,
        line=args.pin,
        event_handler=GracefulActor(
            action=command_runner(
                command=exec,
                logger=logger,
            ),
            grace=10.0,
            logger=logger,
        ),
        consumer="Test Project",
        edge_detection=Edge.FALLING,
        bias=Bias.PULL_UP,
    )

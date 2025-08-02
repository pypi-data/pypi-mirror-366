import asyncio
from collections.abc import Callable
from datetime import timedelta
import logging
import time
from gpiod.line import Bias, Edge


class GracefulActor:
    """A grace-period guard for callable.

    A wrapper class to guard an action callable to only run distances more
    than the given grace period (second).
    """
    _grace: int
    _action: Callable
    _logger: logging.Logger
    __lock: asyncio.Lock
    __until: float

    def __init__(
        self,
        action: Callable,
        grace: float = 20.0,
        logger: logging.Logger = None,
    ):
        self._action = action
        self._grace = grace
        self._logger = logger
        self.__lock = asyncio.Lock()
        self.__until = 0.0

    def __call__(self, *args, **kwargs):
        asyncio.run(self.act(*args, **kwargs))
    
    async def act(self, *args, **kwargs):
        now = time.time()
        await self.__lock.acquire()
        try:
            if now > self.__until:
                # only act if is not within grace period
                self._logger.debug("act now! until = {}".format(self.__until))
                self._action(*args, **kwargs)
                self.__until = now + self._grace
            else:
                self._logger.debug("grace now! until = {}".format(self.__until))
        finally:
            self.__lock.release()

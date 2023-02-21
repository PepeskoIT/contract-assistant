import asyncio
import logging

from envs import APP_LOGGER_NAME
from logging_setup import load_logger_config
from sites.justjoinit.client import JustJoinJob
from sites.nofluffjobs.client import NoFluffJobsJob

load_logger_config()
logger = logging.getLogger(APP_LOGGER_NAME)


class NotSupported(Exception):
    pass


TASKS = [
    JustJoinJob,
    NoFluffJobsJob
]


async def runner():
    conf_fut = {
        asyncio.create_task(
            task().start(), name=task.readable_id
        )
        for task in TASKS
        }
    pending = conf_fut

    logger.debug("RUNNING JOBS!")
    while pending:
        finished, pending = await asyncio.wait(
            pending, return_when=asyncio.FIRST_EXCEPTION
        )
        for task in finished:
            exception = task.exception()
            task_name = task.get_name()
            if exception:
                logger.error(
                    f"Task '{task_name}' failed to execute. "
                    f"Got uncaught exception '{type(exception).__name__}': "
                    f"'{exception}'"
                )

        logger.info(
            f"IN PROGRESS: {len(pending)}: "
            f"{set(task.get_name() for task in pending)}")

    logger.info("No more pending jobs")

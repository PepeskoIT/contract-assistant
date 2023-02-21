import asyncio
from functools import wraps
from logging import getLogger

from envs import APP_LOGGER_NAME

logger = getLogger(APP_LOGGER_NAME)


def calc_loop(m_tries):
    if m_tries is None:
        return True
    else:
        return m_tries >= 1


def retry(error=Exception, delay=False, max_retries=None, retry_backoff=None):
    def decorator(f):
        @wraps(f)
        async def decorated(*args, **kwargs):
            # self = args[0]

            m_tries = max_retries
            m_backoff = retry_backoff

            last_exception = None
            last_exception_msg = None
            while calc_loop(m_tries):
                try:
                    return await f(*args, **kwargs)
                except error as e:
                    last_exception = e
                    msg = (
                        f"{type(e).__name__} '{e}' during execution of "
                        f"{f.__name__}(args={args}, kwargs={kwargs})"
                    )
                    if m_tries is not None:
                        m_tries -= 1
                        msg += f"Retry {max_retries-m_tries}/{max_retries}"
                    logger.warning(msg)
                    last_exception_msg = msg
                    if delay:
                        m_delay = 1  # TODO: parametrize me
                        if m_backoff:
                            m_delay += m_backoff
                            m_backoff += m_backoff
                        logger.debug(f"Retry delay {m_delay} seconds")
                        await asyncio.sleep(m_delay)
            else:
                msg = (
                    f"All {max_retries} retries were used up. "
                    f"Last recorded exception {type(last_exception).__name} - "
                    f"{last_exception_msg}"
                )
                logger.critical(msg)
                raise Exception
        return decorated
    return decorator

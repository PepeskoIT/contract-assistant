import logging
import socket
from contextlib import asynccontextmanager
from asyncio import current_task
from envs import (
    DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, APP_LOGGER_NAME
)
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker, async_scoped_session
)

logger = logging.getLogger(APP_LOGGER_NAME)

DB_ASYNC_DRIVER = "postgresql+psycopg"
DB_SYNC_DRIVER = "postgresql+psycopg"

DB_URL_TEMPLATE = (
    f"{{db_driver}}://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

DB_ASYNC_URL = DB_URL_TEMPLATE.format(db_driver=DB_ASYNC_DRIVER)
DB_SYNC_URL = DB_URL_TEMPLATE.format(db_driver=DB_SYNC_DRIVER)

ENGINE = create_async_engine(
    DB_ASYNC_URL, echo=True,
    pool_size=200, max_overflow=50, pool_recycle=3600, pool_timeout=60,
)

ASYNC_SESSION_FACTORY = async_sessionmaker(ENGINE, expire_on_commit=False)
ASYNC_SESSION = async_scoped_session(
    ASYNC_SESSION_FACTORY, scopefunc=current_task
)


class DbClientError(Exception):
    """Generic db client related error
    """
    pass


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    """Common session context to operate async db sessions.

    Raises:
        DbClientError: generic db related exception

    Yields:
        AsynSession: asyn db session object
    """

    async with ASYNC_SESSION_FACTORY.begin() as session:
        try:
            logger.debug("session ready")
            yield session
        except (socket.error, OSError, Exception) as e:
            logger.exception(
                f"Exception during handling session to DB {session}. "
                f"{e}"
                )
            raise DbClientError(e)
        finally:
            logger.debug("session closed")

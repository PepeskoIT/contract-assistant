import logging

import aiohttp

from envs import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)


class ApiClientError(Exception):
    pass


class AsyncApiClient:

    # TODO: add request retry

    def __init__(
        self, url: str, port: int = 443, login: str = None,
        password: str = None, session: aiohttp.ClientSession = None
    ) -> None:
        self.url = url
        self.port = port
        self.login = login
        self.password = password
        self.session = session

    def __getattr__(self, attr):
        if self.session is None:
            raise ApiClientError("Session is not present")
        return getattr(self.session, attr)

    def prepare_session(self):
        auth = None

        if self.login and self.password:
            auth = aiohttp.BasicAuth(self.login, self.password, 'utf-8')

        self.session = aiohttp.ClientSession(
            f"{self.url}",
            auth=auth,
            )

    def ensure_session(self):
        if self.session is None:
            logger.debug("Session is not present. Creating one now...")
            self.prepare_session()

    async def close(self):
        await self.session.close()
        self.session = None

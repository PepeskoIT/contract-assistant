import logging
from abc import abstractmethod

from sqlalchemy import select

from clients.db import get_db_session
from envs import APP_LOGGER_NAME
from schemas.ads import Ad, Company

logger = logging.getLogger(APP_LOGGER_NAME)


class DataProcessingError(Exception):
    pass


class CompanyProcessingError(DataProcessingError):
    pass


class ApiScrapJob:
    def __init__(self, web_session, db_session=None) -> None:
        self.web_session = web_session
        self.db_session = db_session

    @property
    def readable_id(self):
        return type(self).__name__

    @staticmethod
    @abstractmethod
    def build_company_model(entry):
        pass

    @staticmethod
    @abstractmethod
    def build_ad_model(entry):
        pass

    @abstractmethod
    async def get_data():
        pass

    async def process_entry(self, entry):
        company = self.build_company_model(entry)
        company_in_db = await self.get_company_from_db(company)
        ad = self.build_ad_model(entry)

        if company_in_db is not None:
            ad_in_db = await self.get_ad_from_db(ad)
            if ad_in_db is not None:
                # if ad_in_db not in company_in_db.company_ads:
                company_in_db.company_ads.append(ad_in_db)
            else:
                company_in_db.company_ads.append(ad)
            await self.db_session.merge(company_in_db)
        else:
            company.company_ads.append(ad)
            self.db_session.add(company)
        # # TODO: add mechanism to mark ad as expired

    async def start(self):
        self.web_session.ensure_session()
        data = await self.get_data()
        logger.debug(f"Aquired {len(data)} entries from {self.readable_id}")
        async with get_db_session() as session:
            self.db_session = session
            for entry in data:
                await self.process_entry(entry)
        self.db_session = None

    async def get_company_from_db(self, company):
        q_company_in_db = select(
            Company
        ).where(
            Company.company_name == company.company_name,
            # Company.company_hq_country == company.company_hq_country,
            # Company.company_hq_city == company.company_hq_city,
        )
        matching_company_in_db = (
            await self.db_session.execute(q_company_in_db)
        ).scalars().first()
        return matching_company_in_db

    async def get_ad_from_db(self, ad):
        q_is_ad_in_db = select(
            Ad
        ).where(
            Ad.ad_src == ad.ad_src,
            Ad.ad_url == ad.ad_url,
            Ad.ad_expired is not True
        )
        matching_ad_in_db = (
            await self.db_session.execute(q_is_ad_in_db)
        ).scalars().first()
        return matching_ad_in_db

    # async def check_if_ad_in_db(self, ad, session):
    #     q_is_ad_in_db = select(
    #         Ad
    #     ).where(
    #         Ad.ad_src == ad.ad_src,
    #         Ad.ad_url == ad.ad_url,
    #         Ad.ad_expired is not True
    #     ).exists()
    #     is_ad_in_db = (
    #         await session.execute(select(q_is_ad_in_db))
    #     ).scalars().first()
    #     return is_ad_in_db

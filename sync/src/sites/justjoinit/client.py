import logging

from iso3166 import countries

from base_api_client import AsyncApiClient
from enums import WebProtocol
from envs import APP_LOGGER_NAME
from schemas.ads import Ad, Company
from sites.base import ApiScrapJob
from sites.justjoinit.definitions import (API_PORT, API_ROOT_ENPOINT, BASE_URL,
                                          JOBS_SEARCH_ENDPOINT)

logger = logging.getLogger(APP_LOGGER_NAME)

JUSTJOINIT_HTTPS_URL = WebProtocol.HTTPS.value + "://" + BASE_URL

justjoinit = AsyncApiClient(
    url=JUSTJOINIT_HTTPS_URL, port=API_PORT
)
# curl 'https://justjoin.it/api/offers' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0' -H 'Accept: application/json, text/plain, */*' -H 'Content-Type: application/json' -H 'Referer: https://justjoin.it/?tab=with-salary'


def create_ad_url():
    pass


class JustJoinJob(ApiScrapJob):
    def __init__(self, **kwargs) -> None:
        super().__init__(justjoinit, **kwargs)

    @staticmethod
    def build_company_model(entry):
        company_name = entry["company_name"]
        # TODO: add some parsing mechanism for
        # company_size, company hq country and city
        company_url = entry["company_url"]

        return Company(
            company_name=company_name,
            company_url=company_url
        )

    @staticmethod
    def build_ad_model(entry):
        salary_kwargs = {}

        for employment_type in entry["employment_types"]:
            # TODO: DRY refactor ,dict maybe?
            salary = employment_type["salary"]
            if employment_type["type"] == "b2b":
                salary_kwargs["ad_b2b_available"] = True
                if salary:
                    salary_kwargs["ad_salary_b2b_from"] = (
                        employment_type["salary"]["from"]
                    )
                    salary_kwargs["ad_salary_b2b_to"] = (
                        employment_type["salary"]["to"]
                    )
                    salary_kwargs["ad_salary_b2b_currency"] = (
                        employment_type["salary"]["currency"].upper()
                    )
            if employment_type["type"] == "permanent":
                salary_kwargs["ad_permanent_available"] = True
                if salary:
                    salary_kwargs["ad_salary_permanent_from"] = (
                        employment_type["salary"]["from"]
                    )
                    salary_kwargs["ad_salary_permanent_to"] = (
                        employment_type["salary"]["to"]
                    )
                    salary_kwargs["ad_salary_permanent_currency"] = (
                        employment_type["salary"]["currency"].upper()
                    )
        ad_posted_date = entry["published_at"]
        ad_title = entry["title"]
        try:
            ad_main_technology = entry["marker_icon"].lower()
        except (AttributeError, KeyError) as e:
            logger.debug(
                "Main technology was either not valid or not provided at all. "
                f"Got exception: {type(e).__name__} - {str(e)}"
                f"Problematic entry: {entry}"
            )
            ad_main_technology = None

        ad_url = f"/offers/{entry['id']}"
        ad_fully_remote = entry["workplace_type"] == "remote"
        ad_online_intereview = entry["remote_interview"] == "true"

        # TODO: ad_category create some common enum and parsing

        return Ad(
            ad_posted_date=ad_posted_date,
            ad_title=ad_title,
            ad_main_technology=ad_main_technology,
            ad_url=ad_url,
            ad_src=BASE_URL,
            ad_fully_remote=ad_fully_remote,
            ad_online_intereview=ad_online_intereview,
            **salary_kwargs
        )

    async def get_data(self):
        response = await self.web_session.get(
            API_ROOT_ENPOINT + JOBS_SEARCH_ENDPOINT,
        )
        return await response.json()

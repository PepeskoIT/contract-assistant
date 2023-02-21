import logging
from datetime import datetime

from base_api_client import AsyncApiClient
from enums import WebProtocol
from envs import APP_LOGGER_NAME
from schemas.ads import Ad, Company
from sites.base import ApiScrapJob
from sites.nofluffjobs.definitions import (API_PORT, API_ROOT_ENPOINT,
                                           BASE_URL, JOBS_SEARCH_ENDPOINT)

logger = logging.getLogger(APP_LOGGER_NAME)

NOFLUFFJOBS_HTTPS_URL = WebProtocol.HTTPS.value + "://" + BASE_URL

nofluffjobs = AsyncApiClient(
    url=NOFLUFFJOBS_HTTPS_URL, port=API_PORT
)
# curl 'https://nofluffjobs.com/api/search/posting?offset=0&salaryCurrency=PLN&salaryPeriod=month' -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0' -H 'Accept: application/json' -H 'Content-Type: application/json' --data-raw '{"rawSearch":"requirement=Python","page":1}'


class NoFluffJobsJob(ApiScrapJob):
    def __init__(self, **kwargs) -> None:
        super().__init__(nofluffjobs, **kwargs)

    @staticmethod
    def build_company_model(entry):
        # TODO: add some parsing mechanism for
        # company_size, company hq country and city, company url

        company_name = entry["name"]

        return Company(
            company_name=company_name,
        )

    @staticmethod
    def build_ad_model(entry):
        salary_kwargs = {}
        # for employment_type in entry["employment_types"]:
        # TODO: DRY refactor ,dict maybe?
        salary = entry["salary"]
        if salary["type"] == "b2b":
            salary_kwargs["ad_b2b_available"] = True
            salary_kwargs["ad_salary_b2b_from"] = salary["from"]
            salary_kwargs["ad_salary_b2b_to"] = salary["to"]
            salary_kwargs["ad_salary_b2b_currency"] = (
                salary["currency"].upper()
            )
        if salary["type"] == "permanent":
            salary_kwargs["ad_permanent_available"] = True
            salary_kwargs["ad_salary_permanent_from"] = salary["from"]
            salary_kwargs["ad_salary_permanent_to"] = salary["to"]
            salary_kwargs["ad_salary_permanent_currency"] = (
                salary["currency"].upper()
            )

        ad_title = entry["title"]
        try:
            # DRY me
            ad_main_technology = entry["technology"].lower()
        except (AttributeError, KeyError) as e:
            logger.debug(
                "Main technology was either not valid or not provided at all. "
                f"Got exception: {type(e).__name__} - {str(e)}"
                f"Problematic entry: {entry}"
            )
            ad_main_technology = None

        ad_posted_date = datetime.utcfromtimestamp(entry["posted"]/1000)
        ad_url = f"/offers/{entry['url']}"
        ad_fully_remote = entry["fullyRemote"]
        ad_online_intereview = entry["onlineInterviewAvailable"]
        # TODO: ad_category = entry["category"]
        # Create some common enum and parsing

        return Ad(
            ad_posted_date=ad_posted_date,
            ad_title=ad_title,
            ad_main_technology=ad_main_technology,
            ad_url=ad_url,
            ad_src=BASE_URL,
            ad_fully_remote=ad_fully_remote,
            ad_online_intereview=ad_online_intereview,
            # ad_category=ad_category,
            **salary_kwargs
        )

    async def get_data(self):
        request_data = {"rawSearch": "requirement=Python", "page": 1}
        request_params = {
            "offset": 0, "salaryCurrency": "PLN", "salaryPeriod": "month"
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }
        response = await self.web_session.post(
            API_ROOT_ENPOINT + JOBS_SEARCH_ENDPOINT,
            json=request_data,
            params=request_params,
            headers=headers
        )
        return (await response.json())["postings"]

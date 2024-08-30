import asyncio
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from tabulate import tabulate


@shared_task(bind=True)
def scrape_itu_data(self, filter_date):
    progress_recorder = ProgressRecorder(self)

    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async def process_country(session, value, filter_date):
        link = f"https://www.itu.int/oth/{value}/en"
        html = await fetch(session, link)
        soup = BeautifulSoup(html, "html.parser")

        posted_date = soup.find_all("b")
        country = soup.find("title")

        update_date = None
        for i in range(8, 11):
            try:
                if check_date_format(posted_date[i].text.strip()):
                    update_date = posted_date[i].text.strip()
                    break
            except:
                continue

        if update_date:
            if update_date > filter_date:
                return [country.text.strip(), update_date, link]
        return None

    async def main():
        url = "https://www.itu.int/oth/T0202.aspx?lang=en&parent=T0202"

        async with aiohttp.ClientSession() as session:
            html = await fetch(session, url)
            soup = BeautifulSoup(html, "html.parser")
            dropdown = soup.find(
                "select", {"id": "ctl00_ContentPlaceHolder1_ctl01_lstCountryPrefix"}
            )

            tasks = []
            total_countries = len(dropdown.find_all("option"))
            for i, option in enumerate(dropdown.find_all("option")):
                value = option.get("value")
                if value:
                    tasks.append(process_country(session, value, filter_date))
                progress_recorder.set_progress(i + 1, total_countries)

            results = await asyncio.gather(*tasks)
            data_list = [result for result in results if result]

        return data_list

    def check_date_format(date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    data_list = asyncio.run(main())
    country_updated = len(data_list)

    result = ""
    if len(data_list) >= 2:
        result += "\n\n"
        result += tabulate(data_list, headers=["Country", "Date", "Link"], tablefmt="github")

    result += f"\n\n{country_updated} countries have new updates"
    return result

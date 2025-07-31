import asyncio
from urllib.parse import urlencode
import logging
from typing import Any
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import re

from contracts import PARSER_HEADERS, AbstractIntegration, JobVacancy


class AsyncDjinniVacancyParser(AbstractIntegration):
    def __init__(self, search_params: dict[str, Any] = {}):
        self._search_params = urlencode(search_params, doseq=True)
        self._base_url = "https://djinni.co"
        self._jobs_url = "https://djinni.co/jobs/?"
        self._headers = PARSER_HEADERS

    async def fetch_page(
        self, client: httpx.AsyncClient, url: str
    ) -> BeautifulSoup | None:
        """Fetch and parse a webpage asynchronously"""
        try:
            response = await client.get(url, headers=self._headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except httpx.RequestError as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_job_id(self, li_element) -> int | None:
        """Extract job ID from li element's id attribute"""
        job_id_attr = li_element.get("id", "")
        match = re.search(r"job-item-(\d+)", job_id_attr)
        return int(match.group(1)) if match else None

    def extract_vacancy_data(self, li_element) -> dict:
        """Extract vacancy information from li element"""
        job_id = self.extract_job_id(li_element)

        # Extract title and link - looking for the main job link
        title_link = li_element.find("a", href=re.compile(r"/jobs/\d+"))
        title = title_link.get_text(strip=True) if title_link else "No title"
        print("EXTRACTING VACANCY", title)

        # Construct full URL for the job
        link = ""
        if title_link and title_link.get("href"):
            href = title_link.get("href")
            if href.startswith("/"):
                link = self._base_url + href
            else:
                link = href

        # Extract job details from the text content
        text_content = li_element.get_text()

        # Extract view count, application count, and date
        stats_pattern = r"(\d+)\s*views?\s*·\s*(\d+)\s*applications?\s*·\s*"

        stats_match = re.search(stats_pattern, text_content, re.IGNORECASE)
        # remove stats from text content to avoid further mismatches
        text_content = re.sub(stats_pattern, "", text_content, re.IGNORECASE)

        views = 0
        applications = 0
        date_str = ""
        date = None

        if stats_match:
            views = int(stats_match.group(1))
            applications = int(stats_match.group(2))

        date_regex = re.compile(r"(\d{1,2}:\d{1,2})\s(\d{2}\.\d{2}\.\d{4})")
        date_str = li_element.find("span", {"title": date_regex})["title"]
        date = datetime.strptime(date_str, "%H:%M %d.%m.%Y")
        details_pattern = r"""(?P<employment>(?:Full|Partial|Hybrid|Remote|Office)[^\n·]*)\s*·\s*
(?P<location>.+?)\s*·\s*
(?P<experience>\d+\+?\s+years? of experience)"""

        details_match = re.search(
            details_pattern, text_content, re.DOTALL | re.IGNORECASE
        )
        print("MATCH", details_match)
        location = ""
        experience = ""
        employment = ""

        if details_match:
            experience = details_match.group("experience")
            location = details_match.group("location")
            employment = details_match.group("employment")

        # Extract salary if mentioned
        salary_pattern = r"to\s*\$(\d+(?:,\d+)?)"
        salary_match = re.search(salary_pattern, text_content)
        salary = salary_match.group(1) if salary_match else ""

        # Extract description - get text content and clean it up
        description_parts = []

        # Look for description in various elements
        for element in li_element.find_all(["p", "div"], limit=3):
            desc_text = element.get_text(strip=True)
            if desc_text and len(desc_text) > 50:  # Only substantial text
                description_parts.append(desc_text)

        description = " ".join(description_parts[:2])  # Take first 2 substantial parts

        # Clean up description - remove stats and metadata
        description = re.sub(
            r"\d+\s*views?\s*·\s*\d+\s*applications?\s*·\s*\d+[dw]", "", description
        )
        description = re.sub(r"More#job-item-\d+", "", description)
        description = description.strip()

        return {
            "id": job_id,
            "title": title,
            "location": location,
            "employment": employment,
            "experience": experience,
            "salary": salary,
            "views": views,
            "applications": applications,
            "date_str": date_str,
            "date": date,
            "description": description[:500] + "..."
            if len(description) > 500
            else description,
            "link": link,
        }

    def should_include_vacancy(
        self, vacancy: dict, since_date: datetime | None, last_id: int | None
    ) -> bool:
        """Determine if vacancy should be included based on filters"""
        job_id = vacancy["id"]

        # Filter by ID - include jobs with ID greater than last_id
        if last_id is not None and job_id is not None:
            if job_id <= last_id:
                return False

        # Filter by date - include jobs newer than since_date
        if since_date is not None and vacancy["date"]:
            if vacancy["date"] <= since_date:
                return False

        return True

    async def fetch_page_vacancies(
        self, client: httpx.AsyncClient, page: int = 1
    ) -> list[dict]:
        """Fetch vacancies from a specific page"""
        page_url = self._jobs_url
        query_added = False
        if page > 1:
            page_url += f"page={page}"
            query_added = True
        if self._search_params:
            if query_added:
                page_url += "&"
            page_url += self._search_params
        print("FETCHING FROM", page_url)
        soup = await self.fetch_page(client, page_url)
        if not soup:
            return []

        vacancies = []

        # Find all job listing elements
        job_items = soup.find_all("li", id=re.compile(r"job-item-\d+"))

        for li_element in job_items:
            try:
                vacancy_data = self.extract_vacancy_data(li_element)
                if vacancy_data["id"]:  # Only include if we successfully extracted ID
                    vacancies.append(vacancy_data)
            except Exception as e:
                logging.exception(f"Error processing vacancy: {e}")
                continue

        return vacancies

    async def parse_vacancies(
        self,
        since_date: datetime | None = None,
        last_id: int | None = None,
    ) -> list[JobVacancy]:
        """
        Parse vacancies from Djinni.co website asynchronously

        Args:
            since_date: Only jobs created after this date will be included
            last_id: Last processed job ID

        Returns:
            List of vacancy dictionaries matching the criteria
        """

        filtered_vacancies = []
        max_pages = 1

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create tasks for concurrent page fetching
            tasks = []
            for page in range(1, max_pages + 1):
                tasks.append(self.fetch_page_vacancies(client, page))

            # Execute all requests concurrently
            pages_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for page_num, result in enumerate(pages_results, 1):
                if isinstance(result, BaseException):
                    logging.exception(f"Error fetching page {page_num}: {result}")
                    continue

                found_matching = False

                for vacancy in result:
                    if self.should_include_vacancy(vacancy, since_date, last_id):
                        filtered_vacancies.append(vacancy)
                        found_matching = True

                # If we found matching vacancies on this page, continue
                # If not, we might have reached older content
                if not found_matching and (since_date or last_id):
                    print(
                        f"No matching vacancies found on page {page_num}, stopping pagination"
                    )
                    break

        filtered_vacancies.sort(key=lambda x: x["date"], reverse=True)

        return filtered_vacancies

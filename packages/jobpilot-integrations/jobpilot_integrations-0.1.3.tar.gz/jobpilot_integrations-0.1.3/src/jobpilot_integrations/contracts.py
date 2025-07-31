from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from typing import Literal, NamedTuple

PARSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


class SalaryRange(NamedTuple):
    range: tuple[int, int | None]
    unit: Literal["month", "year"]


@dataclass
class JobVacancy:
    """
    Represents a job vacancy

    Fields:
        name (str): The job title/position name
        salary_range (SalaryRange | None): Represents salary range in USD + unit (per year/month) or None if not specified
        description (str): Job description text
        location (str): Job location (country, city, "Remote", "Worldwide")
        apply_url (str): Original URL of the job posting on jobs website
        date (datetime): Date when vacancy was posted
    """

    id: str
    name: str
    description: str
    location: str
    apply_url: str
    date: datetime
    salary_range: SalaryRange | None = None


class AbstractIntegration(ABC):
    @abstractmethod
    async def parse_vacancies(
        self, since_date: datetime | None = None
    ) -> list[JobVacancy]: ...

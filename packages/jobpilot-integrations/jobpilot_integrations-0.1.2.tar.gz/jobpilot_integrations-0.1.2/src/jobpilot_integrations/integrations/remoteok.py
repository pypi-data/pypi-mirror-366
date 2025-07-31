from datetime import UTC, datetime
import httpx
from contracts import PARSER_HEADERS, AbstractIntegration, JobVacancy, SalaryRange


class RemoteOKAPIIntegration(AbstractIntegration):
    def __init__(self) -> None:
        super().__init__()
        self._base_url = "https://remoteok.com/api"
        self._headers = PARSER_HEADERS

    def _should_include_vacancy(
        self, vacancy: JobVacancy, since_date: datetime | None
    ) -> bool:
        """Determine if vacancy should be included based on filters"""

        if since_date is not None:
            if vacancy.date <= since_date:
                return False
        return True

    async def parse_vacancies(
        self, since_date: datetime | None = None
    ) -> list[JobVacancy]:
        if since_date:
            since_date = since_date.replace(tzinfo=UTC)
        parsed: list[JobVacancy] = []
        async with httpx.AsyncClient() as client:
            resp = await client.get(self._base_url, headers=self._headers)
            vacancies = resp.json()[1:]
            for vac in vacancies:
                annual_salary_range = (
                    vac.get("salary_min", 0),
                    vac.get("salary_max", None),
                )
                job_vacancy = JobVacancy(
                    id=vac["id"],
                    name=vac["position"],
                    salary_range=SalaryRange(annual_salary_range, "year")
                    if annual_salary_range != (0, None)
                    else None,
                    description=vac["description"],
                    location=vac["location"],
                    apply_url=vac["apply_url"],
                    date=datetime.fromtimestamp(vac["epoch"], UTC),
                )
                parsed.append(job_vacancy)
                if not self._should_include_vacancy(job_vacancy, since_date):
                    break
        return parsed

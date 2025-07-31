"""Module for testing parsers usage"""

from datetime import datetime, timedelta
from integrations.remoteok import RemoteOKAPIIntegration
import asyncio


async def main():
    """Example usage of the parser"""
    # parser = AsyncDjinniVacancyParser(
    # {
    #     "primary_keyword": [
    #         "JavaScript",
    #         "React.js",
    #         "Markup",
    #         "Fullstack",
    #         "Python",
    #         "Node.js",
    #         "React Native",
    #         "Golang",
    #         "Ruby",
    #     ],
    #     "exp_level": ["no_exp", "1y", "2y"],
    #     "employment": "remote",
    # }
    # )
    parser = RemoteOKAPIIntegration()

    # Example 1: Get all vacancies newer than a specific date
    print("Fetching vacancies newer than 2024-01-01...")
    vacancies = await parser.parse_vacancies(datetime.now() - timedelta(days=7))

    print(f"Found {len(vacancies)} vacancies")
    for vacancy in vacancies[:5]:  # Show first 5
        print(vacancy)

    # # Example 2: Get vacancies with ID greater than a specific number
    # print(f"\nFetching vacancies with ID > 250000...")
    # vacancies = await parser.parse_vacancies(last_id=250000, max_pages=2)
    #
    # print(f"Found {len(vacancies)} vacancies")
    # for vacancy in vacancies[:3]:  # Show first 3
    #     print(f"ID: {vacancy['id']}, Title: {vacancy['title']}")
    #
    # # Example 3: Export to JSON
    # if vacancies:
    #     with open("djinni_vacancies.json", "w", encoding="utf-8") as f:
    #         json.dump(vacancies, f, indent=2, ensure_ascii=False, default=str)
    #     print(f"\nExported {len(vacancies)} vacancies to djinni_vacancies.json")


if __name__ == "__main__":
    asyncio.run(main())

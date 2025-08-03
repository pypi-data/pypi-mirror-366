from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup as bs
from decimal import Decimal


LIST_TYPE = 3
BASE_URL = "https://webappcenter.nbs.rs/ExchangeRateWebApp/ExchangeRate/IndexByDate"
URL_QUERY = "?isSearchExecuted=true&Date={request_date}.&ExchangeRateListTypeID={list_type}"


@dataclass
class ValueData:
    short_name: str
    value_key: int
    country: str
    valid_for: int
    value: Decimal


def generate_url(request_date: str, list_type: int = LIST_TYPE) -> str:
    return BASE_URL + URL_QUERY.format(request_date=request_date, list_type=list_type)


def get_html(request_url: str) -> str:
    response = requests.get(request_url)
    return response.content


def get_values_from_nbs(page_content: str) -> list[ValueData]:
    result = list()
    soup = bs(page_content, "html.parser")
    table_rows = soup.find_all("tr")
    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) != 5:
            continue
        value = cells[4].text.replace(",", ".")
        result.append(
            ValueData(
                short_name=cells[0].text,
                value_key=int(cells[1].text),
                country=cells[2].text,
                valid_for=int(cells[3].text),
                value=Decimal(value),
            )
        )

    return result


def get_all_currency_values(request_date: str) -> list[ValueData]:
    nbs_url = generate_url(request_date=request_date)
    html_content = get_html(request_url=nbs_url)
    return get_values_from_nbs(page_content=html_content)

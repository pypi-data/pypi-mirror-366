from decimal import Decimal
from unittest.mock import patch, MagicMock

from nbs_kurs.get_values_from_nbs import generate_url, get_html, get_values_from_nbs, ValueData, get_all_currency_values


def test_init():
    url = generate_url("1.2.3", 1)
    assert url == (
        "https://webappcenter.nbs.rs/ExchangeRateWebApp/ExchangeRate/IndexByDate?isSearchExecuted=true&Date=1.2.3."
        "&ExchangeRateListTypeID=1"
    )


def test_get_html():
    request_mock = MagicMock()
    get_mock = request_mock.get()
    get_mock.content = "<h1>test</h1>"
    with patch("nbs_kurs.get_values_from_nbs.requests", request_mock):
        result = get_html(request_url="https://dontexist.com")
    assert result == "<h1>test</h1>"


def test_get_values_from_nbs_empty():
    res = get_values_from_nbs("<div></div>")
    assert res == []


def test_get_values_from_nbs():
    html_content = """
    <tr>
    <td>USD</td>
    <td>1</td>
    <td>Russia</td>
    <td>1</td>
    <td>1,23</td>
    </tr>
    """
    res = get_values_from_nbs(html_content)
    assert res == [ValueData(short_name="USD", value_key=1, country="Russia", valid_for=1, value=Decimal("1.23"))]


def test_get_all_currency_values():
    request_mock = MagicMock()
    request_mock.get().content = b"""
    <tr>
    <td>USD</td>
    <td>1</td>
    <td>Russia</td>
    <td>1</td>
    <td>1,23</td>
    </tr>
    <tr>
    <td>EUR</td>
    <td>1</td>
    <td>Europe</td>
    <td>1</td>
    <td>110,23</td>
    </tr>
    """
    with patch("nbs_kurs.get_values_from_nbs.requests", request_mock):
        res = get_all_currency_values(request_date="1.2.3")
    assert res == [
        ValueData(short_name="USD", value_key=1, country="Russia", valid_for=1, value=Decimal("1.23")),
        ValueData(short_name="EUR", value_key=1, country="Europe", valid_for=1, value=Decimal("110.23")),
    ]

import argparse

from nbs_kurs.data_helper import get_value_by_currency
from nbs_kurs.date_helper import current_date
from nbs_kurs.get_values_from_nbs import get_all_currency_values
from nbs_kurs.presentation_helper import print_results

parser = argparse.ArgumentParser(description="My Package - A simple Python package", prog="my-package")

parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

parser.add_argument("--date", help="Datum za koji zelite da vidite kurs u formatu DD.MM.YYYY", default=current_date())
parser.add_argument("--currency", help="Kurs za koji zelite da vidite vrednost", default="all")


def main():
    parse_args = parser.parse_args()
    selected_date = parse_args.date
    currency = parse_args.currency.split(",")
    all_values = get_all_currency_values(request_date=selected_date)
    if "all" not in currency:
        all_values = get_value_by_currency(short_names=currency, data=all_values)
    print_results(all_values)

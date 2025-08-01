from nbs_kurs.get_values_from_nbs import ValueData
from rich.console import Console
from rich.table import Table

console = Console()


def _init_table() -> Table:
    return Table(show_header=True, header_style="bold magenta", title="SREDNJA VREDNOST")


def _create_table_columns(table: Table) -> None:
    table.add_column("Oznaka valute", justify="center", style="cyan", no_wrap=True)
    table.add_column("Sifra valute", justify="center", style="cyan", no_wrap=True)
    table.add_column("Zemlja", justify="center", style="cyan", no_wrap=True)
    table.add_column("Vazi za", justify="center", style="cyan", no_wrap=True)
    table.add_column("Srednji kurs", justify="center", style="cyan", no_wrap=True)


def print_results(value_data: list[ValueData]) -> None:
    table = _init_table()
    _create_table_columns(table)
    for value in value_data:
        table.add_row(value.short_name, str(value.value_key), value.country, str(value.valid_for), str(value.value))
    console.print(table)

# NBS Srednji Kurs

## O projektu

Ovo je Python paket koji omogućava jednostavno preuzimanje i prikaz zvaničnog srednjeg kursa valuta Narodne Banke Srbije (NBS). Aplikacija preuzima najnovije podatke sa zvaničnog sajta NBS i prikazuje ih u preglednom tabelarnom formatu.

### Funkcionalnosti

- Preuzimanje aktuelnog srednjeg kursa za sve valute
- Mogućnost filtriranja prikaza za određene valute
- Pregled kursa za određeni datum
- Pregledan tabelarni prikaz rezultata u terminalu

## Instalacija

### Preduslovi

- Python 3.12 ili noviji
- pip (Python Package Installer)

### Postupak instalacije

Instalirajte `nbs-srednji-kurs` koristeći sledeću komandu:

```shell
pip install nbs-srednji-kurs
```

## Kako koristiti

### Osnovne komande

1. Prikaz svih valuta za današnji dan:
   ```shell
   nbskurs
   ```

2. Prikaz svih dostupnih opcija i pomoći:
   ```shell
   nbskurs -h
   ```

### Napredne opcije

1. Prikaz kursa za određeni datum:
   ```shell
   nbskurs --date 01.08.2025
   ```

2. Prikaz kursa samo za određene valute:
   ```shell
   nbskurs --currency EUR,USD,CHF
   ```

3. Kombinovanje opcija:
   ```shell
   nbskurs --date 01.08.2025 --currency EUR,USD
   ```

### Korišćenje u Python projektu

Paket možete koristiti i programski u vašim Python projektima:

1. Prvo uvezite potrebne funkcije:
   ```python
   from nbs_kurs import get_all_currency_values, get_value_by_currency, get_currency_by_name
   ```

2. Preuzimanje svih kurseva za određeni datum:
   ```python
   # Format datuma: DD.MM.YYYY
   kursevi = get_all_currency_values("01.08.2025")
   print(f"Broj preuzetih valuta: {len(kursevi)}")
   ```

3. Filtriranje kurseva za određene valute:
   ```python
   # Prvo preuzmite sve kurseve
   svi_kursevi = get_all_currency_values("01.08.2025")
   
   # Zatim filtrirajte samo željene valute
   filtrirani_kursevi = get_value_by_currency(["EUR", "USD", "CHF"], svi_kursevi)
   
   # Prikaz rezultata
   for kurs in filtrirani_kursevi:
       print(f"{kurs.short_name}: {kurs.value} RSD za {kurs.valid_for} {kurs.country}")
   ```

4. Preuzimanje pojedinačne valute po imenu:
   ```python
   # Prvo preuzmite sve kurseve
   svi_kursevi = get_all_currency_values("01.08.2025")
   
   # Zatim pronađite specifičnu valutu po njenom kratkom imenu
   euro = get_currency_by_name("EUR", svi_kursevi)
   
   if euro:
       print(f"Kurs za {euro.short_name}: {euro.value} RSD za {euro.valid_for} {euro.country}")
   else:
       print("Valuta nije pronađena")
   ```

## Tehnički detalji

Paket koristi sledeće biblioteke:
- beautifulsoup4 - za parsiranje HTML sadržaja
- requests - za preuzimanje podataka sa sajta NBS
- rich - za formatiran prikaz rezultata u terminalu

## Autor

Ivan Miletić (milemik68@gmail.com)

## Licenca

Ovaj projekat je dostupan pod MIT licencom.

## Doprinos projektu

Doprinosi su dobrodošli! Ako želite da doprinesete projektu, molimo vas da:
1. Napravite fork repozitorijuma
2. Kreirate novu granu za vašu funkcionalnost
3. Pošaljete pull request

## Kontakt

Za sva pitanja i sugestije, možete kontaktirati autora putem email adrese navedene iznad.
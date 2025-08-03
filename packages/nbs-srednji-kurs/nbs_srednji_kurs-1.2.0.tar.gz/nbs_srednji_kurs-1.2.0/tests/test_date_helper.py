import freezegun

from nbs_kurs.date_helper import current_date


def test_current_date():
    with freezegun.freeze_time("2021-01-01"):
        res = current_date()
    assert res == "01.01.2021"

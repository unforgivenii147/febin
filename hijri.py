import datetime

from dh import georgian_to_hijri
from print_persian import print_persian


def get_current_ymd():
    today = datetime.date.today()
    return (today.year, today.month, today.day)


y, m, d = get_current_ymd()
print_persian(f"{georgian_to_hijri(y, m, d)}")

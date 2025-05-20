from . import controllers
from . import models

from odoo.addons.base.models.res_currency import CurrencyRate


def _disable_currency_rate_unique_name_per_day():
    # Remove unique_name_per_day constraint in res.currency.rate model in base module
    # It doesn't delete constraint on database server
    for el in CurrencyRate._sql_constraints:
        if el[0] == 'unique_name_per_day':
            CurrencyRate._sql_constraints.remove(el)
            break

def post_load():
    _disable_currency_rate_unique_name_per_day()

from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Currencytype(EpBunch):
    """If CurrencyType is not specified, it will default to USD and produce $ in the reports."""

    Monetary_Unit: Annotated[Literal['USD', 'AFN', 'ALL', 'ANG', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BGN', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BWP', 'BYR', 'BZD', 'CAD', 'CHF', 'CLP', 'CNY', 'COP', 'CRC', 'CUP', 'CZK', 'DKK', 'DOP', 'EEK', 'EGP', 'EUR', 'FJD', 'GBP', 'GHC', 'GIP', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IRR', 'ISK', 'JEP', 'JMD', 'JPY', 'KGS', 'KHR', 'KPW', 'KRW', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LTL', 'LVL', 'MKD', 'MNT', 'MUR', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'SAR', 'SBD', 'SCR', 'SEK', 'SGD', 'SHP', 'SOS', 'SRD', 'SVC', 'SYP', 'THB', 'TRL', 'TRY', 'TTD', 'TVD', 'TWD', 'UAH', 'UYU', 'UZS', 'VEF', 'VND', 'XCD', 'YER', 'ZAR', 'ZWD'], Field(default=...)]
    """The commonly used three letter currency code for the units of money for the country or region."""
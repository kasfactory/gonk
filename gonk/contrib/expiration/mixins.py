from dateutil.relativedelta import relativedelta


class WeekExpirationMixin:
    expiration = relativedelta(weeks=1)


class MonthExpirationMixin:
    expiration = relativedelta(months=1)


class QuarterExpirationMixin:
    expiration = relativedelta(months=3)


class YearExpirationMixin:
    expiration = relativedelta(years=1)

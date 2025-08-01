###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import numpy as np

from everysk.core.fields import TupleField, IntField, ListField, FloatField, StrField

ENGINES_EXPRESSION_DEFAULT_DATA_TYPES = TupleField(default=('cpp_var', 'str_var'), readonly=True)
ENGINES_CACHE_EXECUTION_EXPIRATION_TIME = IntField(default=14400, readonly=True)
ENGINES_MARKET_DATA_TICKER_TYPES = ListField(default=('everysk_symbol', 'everysk_id', None), readonly=True)

MARKET_DATA_PUBLIC_URL = StrField(
    default='https://public-market-data-1088321674060.us-central1.run.app',
    readonly=True
)
USER_CACHE_LOCK_EXPIRATION_TIME = FloatField(default=10.0, readonly=True)
USER_CACHE_LOCK_MIN_EXPIRATION_TIME = FloatField(default=0.01, readonly=True)
USER_CACHE_LOCK_MAX_EXPIRATION_TIME = FloatField(default=60.0, readonly=True)

ENGINES_EMPTY_CELL = {'value': '-', 'format': 'S'}
ENGINES_OPERATORS = {
    '=': np.ndarray.__eq__,
    '!=': np.ndarray.__ne__,
    '>': np.ndarray.__gt__,
    '<': np.ndarray.__lt__,
    '>=': np.ndarray.__ge__,
    '<=': np.ndarray.__le__,
    'in': lambda data, filter: __in_operator(data, filter),
}

def __in_operator(data, filter):
    _filter = filter.split(',')
    _filter = set([x.strip() for x in _filter])
    return np.array([x in _filter for x in data])   # np.in1d

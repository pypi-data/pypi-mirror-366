# Copyright (c) 2025 Dimetor GmbH.
#
# NOTICE: All information contained herein is, and remains the property
# of Dimetor GmbH and its suppliers, if any. The intellectual and technical
# concepts contained herein are proprietary to Dimetor GmbH and its
# suppliers and may be covered by European and Foreign Patents, patents
# in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from
# Dimetor GmbH.


from functools import wraps
from time import process_time

meter_unit_conversion = {'m': lambda v: v,
                         'km': lambda v: v / 1_000,
                         'feet': lambda v: v * 3.28084
                         }

dBm_unit_conversion = {'dBm': lambda v: v,
                       'mW': lambda v: 10 ** (v / 10),
                       'W': lambda v: 10 ** (v / 10) / 1_000
                       }

dBi_unit_conversion = {'dBi': lambda v: v,
                       'dBd': lambda v: v - 2.15
                       }

MHz_unit_conversion = {'MHz': lambda v: v,
                       'kHz': lambda v: v * 1_000,
                       'Hz': lambda v: v * 1_000_000
                       }


def show_duration(_logger):
    def decorator(func):
        """
        Decorator which shows the execution time of a function.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            t1 = process_time()
            result = func(*args, **kwargs)
            t2 = process_time()
            duration = round(t2 - t1, 2)
            d_min = int(duration) // 60
            d_sec = round(duration % 60, 2)
            _logger.info(f'PERF_STATS: {func.__name__} took {d_min} min {d_sec} sec')
            return result

        return wrapper

    return decorator

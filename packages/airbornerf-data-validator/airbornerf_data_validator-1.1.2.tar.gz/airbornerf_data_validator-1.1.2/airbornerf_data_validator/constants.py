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

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorMessages:
    non_numeric = 'non_numeric_value'
    non_int = 'non_integer_value'
    out_of_range = 'out_of_range_numeric_value'
    unexpected_value = 'not_allowed_value'
    empty_str = 'empty_string'
    non_unique = 'non_unique_string'

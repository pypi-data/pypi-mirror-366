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


# top-level keys match possible values of '--category' option
#
# Explanation of conditional logic in 'if' (used only with run-time options):
#   example: 'if': [{'runtime_opt1': True, 'runtime_opt2': True}, {'runtime_opt3': False}]
#   means AND between dict items, OR between list items
#
# Explanation of conditional logic in 'skip_if' (used only with column names):
#   tells to skip current column if enumerated column(s) exist
#   'skip_if': [{'eci'}, {'cell_id', 'eNodeB'}],
#   means AND between items of sets, OR between items of list

# all strings in data are always converted to lower case to match with 'enum' which must also have lower case values

rules_4g = {
    'cells': {
        'rat': {
            'type': 'str',
            'enum': ['4g'],
            'unique': False
        },
        'latitude': {
            'type': 'flt',
            # based on run-time option \'--epsg-code\' the range is updated dynamically
            'low': -90.0,
            'high': 90.0
        },
        'longitude': {
            'type': 'flt',
            # based on run-time option \'--epsg-code\' the range is updated dynamically
            'low': -180.0,
            'high': 180.0
        },
        'mcc': {
            'type': 'int',
            'low': 1,
            'high': 999
        },
        'mnc': {
            'type': 'int',
            'low': 0,
            'high': 999
        },
        'equip_manufacturer': {
            'type': 'str',
            'enum': [],
            'unique': False
        },
        'mno_owner_flag': {
            'type': 'str',
            'enum': ['true', 'false'],
            'unique': False
        },
        'ecgi': {
            'type': 'int',
            'skip_if': [{'eci'}, {'cell_id', 'eNodeB'}],
            # This is a parameter that varies across MNOs. Thus, it is always assembled by AirborneRF.
            # The range is per the ecgi assembly methodology in AirborneRF.
            'low': 1099511627776,
            'high': 1098680551604223
        },
        'eci': {
            'type': 'int',
            'skip_if': [{'ecgi'}, {'cell_id', 'eNodeB'}],
            'low': 0,
            'high': 268435455
        },
        'eNodeB': {
            # In AirborneRF, the short 20 bits version is used; by LTE standards it can be one of 20 or 28 bits.
            'type': 'int',
            'skip_if': [{'ecgi'}, {'eci'}],
            'low': 0,
            'high': 1048575
        },
        'cell_id': {
            'type': 'int',
            'skip_if': [{'ecgi'}, {'eci'}],
            'low': 0,
            'high': 255
        },
        'pci': {
            'type': 'int',
            'low': 0,
            'high': 503
        },
        'm_down_tilt': {
            'type': 'int',
            'unit': 'degree',
            'low': -90,
            'high': 90
        },
        'height': {
            'type': 'flt',
            'unit': 'meter',
            'low': 0.0,
            'high': 1000.0
        },
        'azimuth': {
            'type': 'int',
            'unit': 'degree',
            'low': 0,
            'high': 359
        },
        'max_cell_range': {
            'type': 'int',
            'unit': 'meter',
            'low': 1000,
            'high': 110000
        },
        'rs_power': {
            'type': 'flt',
            'unit': 'dBm',
            'low': -60.0,
            'high': 50.0
        },
        'max_tx_power': {
            'type': 'flt',
            'unit': 'dBm',
            'low': -43.0,
            'high': 100.0
        },
        'dl_tx_antennae': {
            'type': 'int',
            'skip_if': [{'transmission_scheme'}],
            'enum': [1, 2, 4, 8]
        },
        'ul_rx_antennae': {
            'type': 'int',
            'skip_if': [{'transmission_scheme'}],
            'enum': [1, 2, 4, 8]
        },
        'transmission_scheme': {
            'type': 'str',
            'skip_if': [{'dl_tx_antennae', 'ul_rx_antennae'}],
            'enum': [],
            'unique': False
        },
        'tx_losses': {
            'type': 'flt',
            'unit': 'dB',
            'low': 0.0,
            'high': 15.0
        },
        'offset_traffic': {
            'type': 'flt',
            'unit': 'dB',
            'low': -12.0,
            'high': 12.0
        },
        'offset_control': {
            'type': 'flt',
            'unit': 'dB',
            'low': -12.0,
            'high': 12.0
        },
        'offset_sync': {
            'type': 'flt',
            'unit': 'dB',
            'low': -12.0,
            'high': 12.0
        },
        'offset_broadcast': {
            'type': 'flt',
            'unit': 'dB',
            'low': -12.0,
            'high': 12.0
        },
        'outdoor_flag': {
            'type': 'str',
            'enum': ['true', 'false'],
            'unique': False
        },
        'cell_name': {
            'type': 'str',
            'unique': False,
            'enum': []
        },
        'carrier_name': {
            # this condition means a full file is being verified and no need for cross-reference multiple files
            # this condition corresponds enforces
            'skip_if': [{'cell_name', 'frequency_band'}],
            'type': 'str',
            'enum': [],
            'unique': False
        },
        'pattern_name': {
            # this condition means a full file is being verified and no need for cross-reference multiple files
            'skip_if': [{'horizontal_pattern', 'vertical_pattern', 'cell_name'}],
            'type': 'str',
            'enum': [],
            'unique': False
        },
        'tdd_ul_dl_configuration': {
            'if': [{'disable_tdd': False}],
            'type': 'int',
            'low': 0,
            'high': 6
        },
        'tdd_special_subframe_config': {
            'if': [{'disable_tdd': False}],
            'type': 'int',
            'low': 0,
            'high': 8
        }
    },
    # loads are not included in --category=full
    'loads': {
        # cell_name or ecgi is used for cross-reference
        'cell_name': {
            'skip_if': [{'ecgi'}],
            'type': 'str',
            'unique': True,
            'enum': []
        },
        'ecgi': {
            'skip_if': [{'cell_name'}],
            'type': 'int',
            'low': 1099511627776,
            'high': 1098680551604223
        },
        'date_time': {
            'type': 'str',
            'enum': [],
            'unique': False
        },
        'dl_cell_load': {
            'type': 'flt',
            'unit': 'percentage',
            'low': 0.0,
            'high': 1.0
        },
        'ul_cell_load': {
            'type': 'flt',
            'unit': 'percentage',
            'low': 0.0,
            'high': 1.0
        },
        'ul_interference': {
            'unit': 'dBm',
            'type': 'flt',
            'low': -126.0,
            'high': -75.0
        },
        'dl_active_users': {
            'type': 'flt',
            'low': 0,
            'high': 1000.0
        },
        'ul_active_users': {
            'type': 'flt',
            'low': 0,
            'high': 1000.0
        }
    },
    'carriers': {
        'carrier_name': {
            # this condition means a full file is being verified and no need for cross-reference multiple files
            'skip_if': [{'cell_name', 'frequency_band'}],
            'type': 'str',
            'enum': [],
            'unique': True
        },
        'frequency_band': {
            'type': 'int',
            'low': 1,
            'high': 103
        },
        'dl_bandwidth': {
            'type': 'flt',
            'unit': 'MHz',
            'enum': [1.4, 3.0, 5.0, 10.0, 15.0, 20.0]
        },
        'ul_bandwidth': {
            'type': 'flt',
            'unit': 'MHz',
            'enum': [1.4, 3.0, 5.0, 10.0, 15.0, 20.0]
        },
        'dl_earfcn': {
            'type': 'int',
            'low': 0,
            'high': 70655
        },
        'ul_earfcn': {
            'type': 'int',
            'low': 18000,
            'high': 134291
        },
        'dss_flag': {
            'if': [{'disable_dss': False}],
            'type': 'str',
            'enum': ['true', 'false'],
            'unique': False
        }
    },
    'transmitters': {
        'pattern_name': {
            # this condition means a full file is being verified and no need for cross-reference multiple files
            'skip_if': [{'horizontal_pattern', 'vertical_pattern', 'cell_name'}],
            'type': 'str',
            'enum': [],
            'unique': True
        },
        'horizontal_pattern': {
            # this condition means a full file is being verified
            'skip_if': [{'pattern_name'}, {'cell_name'}],
            'type': 'str',
            'enum': [],
            'unique': False
        },
        'vertical_pattern': {
            # this condition means a full file is being verified
            'skip_if': [{'pattern_name'}, {'cell_name'}],
            'type': 'str',
            'enum': [],
            'unique': False
        },
        # Not approved yet in data requirements document
        # 'antenna_pafx_file': {
        #     'skip_if': [{'horizontal_pattern', 'vertical_pattern'}],
        #     'type': 'str',
        #     'enum': [],
        #     'unique': False
        # },
        # 'antenna_msi_file': {
        #     'skip_if': [{'horizontal_pattern', 'vertical_pattern'}],
        #     'type': 'str',
        #     'enum': [],
        #     'unique': False
        # },
        'gain': {
            'type': 'flt',
            'unit': 'dBi',
            'low': 0.0,
            'high': 30.0
        },
        'e_down_tilt': {
            'type': 'int',
            'unit': 'degree',
            'low': -90,
            'high': 90
        },
        'polarization': {
            'type': 'str',
            'enum': ['cross', 'horizontal', 'vertical'],
            'unique': False
        }
    }
}

rules_5g = {}

all_rules = {'4g': rules_4g,
             '5g': rules_5g}

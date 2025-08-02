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


import logging

import pandas as pd
from pyproj import Transformer

from airbornerf_data_validator.constants import ErrorMessages
from airbornerf_data_validator.utils import show_duration

logger = logging.getLogger(__name__)


class Validator:
    """
    Validator class for performing structured checks on a dataset against parameter rules.
    Handles numeric, string, and geospatial validations.
    """

    def __init__(self, df, params):
        """
        Initialize the Validator with a DataFrame, and validation rules.

        :param df: pandas DataFrame containing the dataset
        :param params: dictionary of parameter validation rules
        :param epsg_code: EPSG integer code for input coordinate system
        """

        self.df = df
        self.params = params
        self.bad_rows = set()
        self.results = {'errors': {ErrorMessages.non_numeric: {},
                                   ErrorMessages.non_int: {},
                                   ErrorMessages.out_of_range: {},
                                   ErrorMessages.unexpected_value: {},
                                   ErrorMessages.empty_str: {},
                                   ErrorMessages.non_unique: {}
                                   },
                        'missing_parameters': [],
                        'ignored_parameters': [],
                        'duplicated_rows': [],
                        'stats': {'missing_parameters': 0,
                                  'errors': 0,
                                  'total_rows': df.shape[0],
                                  'bad_rows': 0,
                                  'duplicated_rows': 0,
                                  'good_rows': 0
                                  }
                        }

    def process_result(self, df_bad, error_msg):
        """
        Update result object with errors and statistics.

        :param df_bad: A one column DataFrame containing the failed rows.
        :param error_msg: Error category string as per ErrorMessages
        :return:
        """
        if not df_bad.empty:
            logger.debug(f'STATUS: {error_msg} in column {df_bad.columns[0]}, number of bad rows {df_bad.shape[0]}')
            self.results['errors'][error_msg].update(df_bad.to_dict())
            self.bad_rows = self.bad_rows | set(df_bad.index.to_list())
            self.results['stats']['errors'] += df_bad.shape[0]
            self.results['stats']['bad_rows'] = len(self.bad_rows)

        self.results['stats']['good_rows'] = (self.results['stats']['total_rows'] - len(self.bad_rows)
                                              - self.results['stats']['duplicated_rows'])

    @show_duration(logger)
    def check_num_params(self, params_to_check, _type):
        """
        Validate numeric parameters for expected type (int/float), value ranges, enums, and reprojection.

        :param params_to_check: List of numeric parameter names.
        :param _type: str one of 'flt' or 'int', represents type of the parameters
        :return:
        """
        for param_name in params_to_check:
            if param_name in {'latitude', 'longitude'} and self.params['epsg_code'] != 4326:
                # skip original lat/lon checks if non-standard CRS is used
                continue

            # Determine errors due to non-numerical values, identify empty rows and keep only numeric data.
            df_buf = pd.to_numeric(self.df[param_name], errors='coerce').to_frame()
            df_non_numeric = self.df[[param_name]][df_buf[param_name].isna() & self.df[param_name].notna()]
            self.process_result(df_non_numeric, ErrorMessages.non_numeric)
            df_numeric = df_buf[~df_buf[param_name].isna()]

            if df_numeric.empty:
                logger.debug(f'No numeric values in {param_name}. Skipping values check.')
                continue

            if _type == 'int':
                # Check column values for floats, if found: report and remove from set.
                df_non_integer = df_numeric[(df_numeric[param_name] - df_numeric[param_name].astype(int) != 0)]
                self.process_result(df_non_integer, ErrorMessages.non_int)

                if len(df_non_integer) == len(df_numeric):
                    logger.debug(f'All numbers in the {param_name} column are float values when integer values are '
                                 f'expected. The range / value check is therefore skipped for the entire column.')
                    continue
                df_numeric = df_numeric[~df_numeric.index.isin(df_non_integer.index)].astype(int)

            enum_params = self.params[_type][param_name].get('enum')
            if enum_params:
                df_bad_value = df_numeric[~df_numeric[param_name].isin(enum_params)]
                self.process_result(df_bad_value, ErrorMessages.unexpected_value)
            else:
                low = self.params[_type][param_name]['low']
                high = self.params[_type][param_name]['high']
                df_bad_value = df_numeric[~df_numeric[param_name].between(low, high)]
                self.process_result(df_bad_value, ErrorMessages.out_of_range)

            # Delete DataFrames to avoid problems below since the same variables are used below for understanding.
            del df_buf, df_non_numeric, df_numeric

        # When a different projection is provided, this becomes a special case. The process:
        # - transform coordinates,
        # - compare transformed coordinates to EPSG bounds which were set during the building of params_to_check,
        # - reported are:
        #   - the original data that are not in the bounds OR that are empty or wrong,
        #   - the reprojected values can be optionally printed as well,
        #   - if one dumps the params_to_check, only the EPSG:4326 bounds are available.
        if {'latitude', 'longitude'}.issubset(params_to_check) and self.params['epsg_code'] != 4326:
            # Determine errors due to non-numerical values, identify empty rows and keep only numeric data.
            df_buf = pd.DataFrame()
            df_buf['latitude'] = pd.to_numeric(self.df['latitude'], errors='coerce')
            df_buf['longitude'] = pd.to_numeric(self.df['longitude'], errors='coerce')

            for param_name in {'latitude', 'longitude'}:
                df_non_numeric = self.df[param_name][df_buf[param_name].isna() & self.df[param_name].notna()]
                self.process_result(df_non_numeric, ErrorMessages.non_numeric)

            # Only transform rows where both latitude and longitude exist.
            valid_mask = ~df_buf['latitude'].isna() & ~df_buf['longitude'].isna()
            df_numeric = df_buf[valid_mask]

            # TODO: add feedback to the report about coordinate that are not transformed due to invalid tuples.

            try:
                transformer = Transformer.from_crs(self.params['epsg_code'], 4326, always_xy=True)
            except Exception as e:
                # This block is for unexpected issues (e.g. transformer misconfiguration), not bad input values.
                logger.exception('Unexpected error during coordinate transformation (not due to input values). Check EPSG code!')
                exit()

            if valid_mask.any():
                df_numeric['longitude_trans'], df_numeric['latitude_trans'] = transformer.transform(
                    df_numeric['longitude'][valid_mask].values,
                    df_numeric['latitude'][valid_mask].values
                )
                logger.info(f'Reprojected {len(df_numeric)} coordinates to EPSG:4326.')

                # TODO: implement method to catch 'inf' errors from transform.
            else:
                # TODO: add feedback to the report that no coordinates were transformed
                logger.warning('No valid latitude/longitude pairs to reproject. Skipping values check.')
                return

            # Validate reprojected values against CRS bounds set when creating params.
            for param_name in {'latitude_trans', 'longitude_trans'}:
                low = self.params[_type][param_name.removesuffix('_trans')]['low']
                high = self.params[_type][param_name.removesuffix('_trans')]['high']

                # Report bad rows in original projection
                df_bad_value = df_numeric.loc[~df_numeric[param_name].between(low, high), [param_name.removesuffix('_trans')]]
                self.process_result(df_bad_value, ErrorMessages.out_of_range)

                # Report bad rows per reprojected coordinates - optional
                if self.params['show_reprojected']:
                    df_bad_value = df_numeric.loc[~df_numeric[param_name].between(low, high), [param_name]]
                    self.process_result(df_bad_value, ErrorMessages.out_of_range)

    @show_duration(logger)
    def check_str_params(self, params_to_check):
        """
        Validate string parameters for allowed values, emptiness, and uniqueness.

        :param params_to_check: List of parameter names
        :return:
        """
        for param_name in params_to_check:
            # detect empty or whitespace-only strings
            df_empty_str = self.df[self.df[param_name].eq('') | self.df[param_name].str.isspace()][[param_name]]
            self.process_result(df_empty_str, ErrorMessages.empty_str)

            enums_params = self.params['str'][param_name]['enum']
            if enums_params:
                df_param = self.df[param_name].str.lower()
                df_bad_value = self.df[~df_param.isin(enums_params)][[param_name]]
                self.process_result(df_bad_value, ErrorMessages.unexpected_value)
            elif self.params['str'][param_name]['unique']:
                df_duplicated = self.df[self.df.duplicated(subset=[param_name], keep=False)][[param_name]]
                self.process_result(df_duplicated, ErrorMessages.non_unique)

    @show_duration(logger)
    def run_check(self):
        """
        Run the full validation process:
        - remove duplicated rows,
        - identify missing parameters,
        - group delivered parameters by their type,
        - execute respective checks.
        :return: dict result with errors and statistics
        """
        duplicated_rows = self.df[self.df.duplicated()].index.to_list()
        self.df = self.df.drop(duplicated_rows)

        self.results['duplicated_rows'] = duplicated_rows
        self.results['stats']['duplicated_rows'] = len(duplicated_rows)

        delivered_params = set(self.df.columns)
        missing_params = self.params['names'] - delivered_params

        # Determine parameters to skip based on "skip_if" conditions, see rules.py for explanation.
        to_skip = set()
        for param in self.params['names']:
            skip_if = self.params[param].get('skip_if', ())
            if not skip_if:
                continue
            # loop is logical "OR" - if one of the conditions is true then "param" can be skipped
            for required_params in skip_if:
                if len(required_params & delivered_params) == len(required_params):
                    to_skip.add(param)
                    break

        missing_params = missing_params - to_skip
        ignored_params = delivered_params - self.params['names']

        logger.debug(f'ignored parameters: {ignored_params or None}')
        logger.debug(f'missing parameters: {missing_params or None}')

        # Data sorting to have consistent results for easier analysis down the road.
        self.results['missing_parameters'].extend(sorted(missing_params))
        self.results['ignored_parameters'].extend(sorted(ignored_params))

        self.results['stats']['missing_parameters'] = len(self.results['missing_parameters'])

        present_params_int = sorted(self.params['int'].keys() & delivered_params)
        self.check_num_params(present_params_int, 'int')

        present_params_float = sorted(self.params['flt'].keys() & delivered_params)
        self.check_num_params(present_params_float, 'flt')

        present_params_str = sorted(self.params['str'].keys() & delivered_params)
        self.check_str_params(present_params_str)

        return self.results

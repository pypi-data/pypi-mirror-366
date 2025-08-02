#!/bin/env python3
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


import io
import json
import logging
import os
from contextlib import redirect_stderr
from copy import deepcopy

import click
import pandas as pd
from pyproj import CRS

from airbornerf_data_validator.core import Validator
from airbornerf_data_validator.rules import all_rules
from airbornerf_data_validator.utils import show_duration, meter_unit_conversion, dBm_unit_conversion, \
    dBi_unit_conversion, MHz_unit_conversion

logger = logging.getLogger(__name__)

def save_run_params(run_params, json_file):
    """
    Save run_params to a json file.

    :param run_params: dict with run_params
    :param json_file: path to file where to save run_params as json
    :return:
    """
    with open(json_file, 'w') as jf:
        json.dump(run_params, jf, indent=4, default=list)


def print_run_params(run_params):
    """
    Print run_params to terminal

    :param run_params: dict with run_params
    :return:
    """
    print('\nRUN PARAMS:\n')
    print(json.dumps(run_params, indent=4, default=list), '\n')
    print('\n')


def present_result(result, json_file):
    """
    Print result or save it to a file.

    :param result: dict with results
    :param json_file: path to file where to save results as json
    :return:
    """
    if json_file:
        with open(json_file, 'w') as jf:
            json.dump(result, jf, indent=4)
    else:
        print('\nREPORT:\n')
        print(json.dumps(result, indent=4), '\n')


def create_config(run_opts):
    """
    The runtime options are assembled into the config json required by the Validator class.
    :param run_opts: dict with run-time options
    :return: dict with relevant parameters for current validation session
    """
    params = {
        'int': {},
        'flt': {},
        'str': {},
        'names': set(),
        'epsg_code': run_opts['epsg_code'],
        'show_reprojected': run_opts['show_reprojected']
    }
    # 5G is not implemented yet; but the idea so far is that one of 4G/5G is validated at a time.
    technology = '4g' if run_opts['file_4g'] else '5g'
    rules = all_rules[technology]

    if run_opts['category'] == 'full':
        run_rules = {}
        for name, rule in rules.items():
            if name != 'loads':
                run_rules.update(deepcopy(rule))
        run_rules['carrier_name']['unique'] = False
        run_rules['pattern_name']['unique'] = False
    else:
        run_rules = deepcopy(rules[run_opts['category']])

    # Parse 'if' condition in each rule which depends on run-time options
    # if none of conditions is met then parameter is not included and outer loop continues
    for param_name, rule in run_rules.items():
        conditions = rule.get('if', [])
        if conditions:
            for condition in conditions:
                for cond_key, cond_val in condition.items():
                    if run_opts[cond_key] != cond_val:
                        break
                else:
                    break
            else:
                continue

        params[rule['type']][param_name] = rule
        params['names'].add(param_name)
        params[param_name] = rule

    # Set value range according to run-time EPSG code
    if params['flt'].get('latitude') and not(run_opts['relax_crs_bounds']):
        crs = CRS.from_epsg(run_opts['epsg_code'])

        # Get area of use bounds in geographic coordinates (EPSG:4326)
        west_lon, south_lat, east_lon, north_lat = crs.area_of_use.bounds

        params['flt']['latitude']['low'] = south_lat
        params['flt']['latitude']['high'] = north_lat
        params['flt']['longitude']['low'] = west_lon
        params['flt']['longitude']['high'] = east_lon

    # Convert validation ranges from AirborneRF default units to configuration specified units.
    # Converting just the ranges is more performant than converting all dataset values.
    for param, conversion in [('height', meter_unit_conversion),
                              ('rs_power', dBm_unit_conversion),
                              ('max_tx_power', dBm_unit_conversion),
                              ('gain', dBi_unit_conversion),
                              ('max_cell_range', meter_unit_conversion),
                              ('dl_bandwidth', MHz_unit_conversion),
                              ('ul_bandwidth', MHz_unit_conversion)]:
        if param not in run_rules:
            continue

        _type = run_rules[param]['type']
        unit = run_opts[f'{param}_unit']
        if unit == params[_type][param]['unit']:
            # no need to convert default unit
            continue

        enum_values = params[_type][param].get('enum')
        if enum_values:
            params[_type][param]['enum'] = [conversion[unit](ev) for ev in enum_values]
        else:
            new_low = conversion[unit](params[_type][param]['low'])
            new_high = conversion[unit](params[_type][param]['high'])
            if _type == 'int':
                new_low = int(new_low)
                new_high = int(new_high)
            params[_type][param]['low'] = new_low
            params[_type][param]['high'] = new_high

    return params


@show_duration(logger)
def read_csv(filename, delimiter):
    """
    Read csv with detection of parsing issues.

    :param filename: str path to csv file
    :param delimiter: str delimiter character
    :return: (dataFrame, dict) dataFrame object and parsing errors
    """

    # 1. Read the file and check all rows for any length inconsistencies, ie the number of values.
    # By default, the Pandas csv reader terminates upon encountering a bad line (on_bad_lines='error).
    # Instead, the following implementation intercepts the pandas warning (on_bad_lines='warnings') to perform the
    # full file check.
    with redirect_stderr(io.StringIO()) as f:
        df = pd.read_csv(filename, engine='c', sep=delimiter, dtype='string', na_filter=False, index_col=False,
                         encoding_errors='replace', encoding='unicode_escape', on_bad_lines='warn')
    errors = f.getvalue()

    if 'ParserWarning: Length of header' in errors:
        errors = ['Length of the header does not match length of data']
    elif 'ParserWarning: Skipping' in errors:
        errors = errors.split('\n')
        # cut off non-relevant payload
        split_idx = errors.index('')
        errors = errors[:split_idx]
        errors[0] = errors[0].split('ParserWarning: ')[-1]
    else:
        errors = list(errors)

    # 2. Detect duplicated column names.
    duplicated_cols = df.columns[df.columns.str.find('.') > 0].to_list()
    if duplicated_cols:
        duplicated_cols = [v.split('.')[0] for v in duplicated_cols]
        df = None
    else:
        # 3. re-index to keep original lines numbers as index for easier understanding of validation results
        # with line number in "errors" above.
        # line number 1 - header line in csv
        # line number 2 - first row with values; so 2 is the first index value in the dataFrame
        df = df.set_axis(range(2, len(df) + 2))
        df.index = df.index.map(str)

    parsing_result = {'duplicated_columns': duplicated_cols,
                      'invalid_lines': errors}

    return df, parsing_result


def main(run_opts):
    """
    Read csv and call validation. If there were csv parsing errors the program will terminate.

    :param run_opts: dict with run-time options
    :return:
    """
    logging.basicConfig(level=run_opts['log_level'],
                        format='[%(asctime)s] <> %(levelname)-8s <> %(name)s:%(lineno)d <> %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S'
                        )

    if os.path.isfile(run_opts['save_json_result_file']):
        logger.error(f'Output file {run_opts["save_json_result_file"]} already exists')
        return {}

    if not run_opts['file_4g']:
        logger.error('No csv file provided.')
        return {}

    logger.debug(f'started with {run_opts}')
    df, parsing_result = read_csv(run_opts['file_4g'], run_opts['delimiter'])

    if parsing_result['invalid_lines'] or parsing_result['duplicated_columns']:
        # These are serious errors and it is very unreliable to work with such dataset.
        logger.error('Terminating. Parsing the file was finished with errors.')
        return parsing_result

    run_params = create_config(run_opts)
    validator = Validator(df, run_params)

    # For debugging / keeping track of parameters used for checking.
    if run_opts['save_json_run_params']:
        save_run_params(run_params, run_opts['save_json_run_params'])

    if run_opts['print_json_run_params']:
        print_run_params(run_params)


    validation_result = validator.run_check()
    return validation_result


@click.command('cli', context_settings={'show_default': True, 'max_content_width': 120})
@click.option('--file-4g', type=click.Path(exists=True), help='path to file with 4G data')
@click.option('--delimiter', default=';', help='Delimiter character in the csv file')
@click.option('--category', type=click.Choice(['full', 'cells', 'carriers', 'transmitters', 'loads']), required=True,
              help='Which category of parameters to validate in the provided file. "full" does not include "loads"')
@click.option('--disable-dss', is_flag=True, help='Disable validation of DSS related parameters')
@click.option('--disable-tdd', is_flag=True, help='Disable validation of TDD related parameters')
@click.option('--log-level', type=click.Choice(['INFO', 'DEBUG', 'ERROR', 'WARNING']), default='ERROR')
@click.option('--epsg-code', default=4326, help='EPSG code of provided coordinates')
@click.option('--show-reprojected', is_flag=True, help='--epsg-code option to print reprojected coordinates as well.')
@click.option('--relax-crs-bounds', is_flag=True, help='--epsg-code option to use world coordinates instead of the CRS bounds coordinates.')
@click.option('--height-unit', type=click.Choice(['m', 'feet']), default='m')
@click.option('--max-cell-range-unit', type=click.Choice(['m', 'km', 'feet']), default='m')
@click.option('--rs-power-unit', type=click.Choice(['dBm', 'mW', 'W']), default='dBm')
@click.option('--max-tx-power-unit', type=click.Choice(['dBm', 'mW', 'W']), default='dBm')
@click.option('--dl-bandwidth-unit', type=click.Choice(['MHz', 'kHz', 'Hz']), default='MHz')
@click.option('--ul-bandwidth-unit', type=click.Choice(['MHz', 'kHz', 'Hz']), default='MHz')
@click.option('--gain-unit', type=click.Choice(['dBi', 'dBd']), default='dBi')
@click.option('--save-json-result-file', default='', help='File name where to save json report (optional)')
@click.option('--save-json-run-params', default='', help='File name where to save json run params (optional)')
@click.option('--print-json-run-params', is_flag=True, help='Print json run params to terminal (optional)')
@click.version_option(package_name='airbornerf-data-validator')
def cli(**run_opts):
    """ Validate cells parameters from csv file.
    Only mandatory parameters are supported for now, optional parameters are not implemented.

    Supported compression:  ‘.gz’, ‘.bz2’, ‘.zip’, ‘.xz’, ‘.zst’, ‘.tar’, ‘.tar.gz’, ‘.tar.xz’ or ‘.tar.bz2’.
    The compressed file must contain only one data file to be read in.

    The result is presented in json format with structure:\n
    {\n
        "errors": {\n
            "error_type": {\n
                "parameter_name": {\n
                    "line_number": value\n
                }\n
            }\n
        }\n
        with additional information in other keys\n
    }\n
    """
    result = main(run_opts)
    if result:
        present_result(result, run_opts['save_json_result_file'])


if __name__ == '__main__':
    cli()

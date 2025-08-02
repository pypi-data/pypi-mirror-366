# Changelog
## 1.1.2
- bug fix: `tx_losses range` to check
- bug fix: the `--epsg-code` functionality was not working as intended
- added the `--show-reprojected` flag which allows for outputting the reprojected parameters when using `--epsg-code`  
- added the `--relax-crs-bounds` flag which changes the CRS bounds coordinates to the entire world when using `--epsg-code`
- added `--save-json-run-params` flag which allow for outputting the run parameters to a json file
- added `--print-json-run-params` flag which allow for outputting the run parameters to terminal

## 1.1.1
- fix bug in output formatting where integer values were shown as floats 

## 1.1.0
- rename flag `--enable-dss` to `--disable-dss`; now DSS parameters are included in verification by default
- add TDD parameters which can be skipped by setting flag `--disable-tdd` 

## 1.0.2
Relaxed the `max_tx_power` parameter from [0.0, 100.0] to [-43.0, 100.0].

Modified the README

## 1.0.1
Fixed variable `ul_tx_antennae` to `ul_rx_antennae` per "4G Cell Data Requirements".

## 1.0.0
First release

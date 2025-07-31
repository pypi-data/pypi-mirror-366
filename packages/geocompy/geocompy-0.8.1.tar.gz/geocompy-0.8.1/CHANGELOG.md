# Changelog

## v0.8.1

### Added

- new methods for `SerialConnection` wrapper:
  - `send_binary`
  - `receive_binary`
  - `exchange_binary`
- `precision` property for the GeoCom definition

### Changed

- GeoCom TMC `get_angle_correction_status` was renamed to
  `get_angle_correction`
- GeoCom TMC `switch_angle_correction` was renamed to `set_angle_correction`
- GeoCom `get_double_precision` was moved to COM
- GeoCom `set_double_precision` was moved to COM

### Fixed

- method docstrings were rendered wrong in some cases due to missing new lines
- GSI Online DNA settings commands were parsing boolean value incorrectly
- GeoCom AUT `set_search_area` command would not execute due to incorrect
  parameter serialization when sending the request to the instrument

## v0.8.0

All CLI applications were migrated to a new package called
[Instrumentman](https://github.com/MrClock8163/Instrumentman). Further
development happens there.

### Added

- Component swizzling in vectors and coordinates

### Changed

- Wait/delay times are now expected in seconds instead of milliseconds,
  where possible

## v0.7.0

### Added

- `retry` option to `open_serial`
- Morse CLI application (`geocompy.apps.morse`)
- Interactive Terminal CLI application (`geocompy.apps.terminal`)
- Set Measurement CLI applications (`geocompy.apps.setmeasurement...`)

## v0.6.0

### Added

- GeoCom
  - Digital Level
    - LS10/15 GeoCom support through new `dna` subsytem (LS10/15 also responds
      to GSI Online DNA commands)
  - Central Services
    - `get_firmware_creation_date` command (RPC 5038)
    - `get_datetime_new` command (RPC 5051)
    - `set_datetime_new` command (RPC 5050)
    - `setup_listing` command (RPC 5072)
    - `get_maintenance_end` command (RPC 5114)
  - Theodolite Measurement and Calculation
    - `get_complete_measurement` command (RPC 2167)

### Fixed

- `morse.py` example script was not using the most up-to-date methods
- GeoCom File Transfer subsystem commmands were missing from the command name
  lookup table

## v0.5.1

### Added

- Missing GeoCom `abort` command
- Discovered GeoCom RPC 11009 (unknown true function name, implemented as
  `switch_display`)

### Fixed

- GeoCom `get_internal_temperature` returned `int` instead of `float`
- GeoCom `get_user_prism_definition` had incorrect return param parsers

## v0.5.0

Initial release on PyPI.

Notable features:

- Serial communication handler
- Utility data types
- GeoCom commands from TPS1000, 1100, 1200 and VivaTPS instruments
  (and any other with overlapping command set)
- GSI Online commands for DNA instruments

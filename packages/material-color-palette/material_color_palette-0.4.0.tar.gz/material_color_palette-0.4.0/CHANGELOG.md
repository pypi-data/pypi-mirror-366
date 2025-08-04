# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project tries to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.4.0] - 2025-08-03

### Changed

- Rename project and package from `material-2014-colors` to `material-color-palette`


## [0.3.0] - 2025-07-26

### Added

- Allow space instead of underscore when constructing `Color` with two-word name
- Error messages: better formatting, sort color names
- Docs: bring README up to date, simplify


## [0.2.0] - 2025-06-20

### Added

-  `Color.name`, `shade` attributes; `hex`, `r`, `g`, `b` properties 

### Changed

- Revised public API: non-public items prefixed with underscore 


## [0.1.1] - 2025-06-20

### Added

- Support for type checking with `py.typed` marker
- Docstrings
- CI: Check with ruff

### Changed

- Tests import the installed package, not source


## [0.1.0] - 2025-06-18

Initial release


[0.4.0]: https://github.com/elliot-100/material-color-palette/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/elliot-100/material-color-palette/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/elliot-100/material-color-palette/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/elliot-100/material-color-palette/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/elliot-100/material-color-palette/releases/tag/v0.1.0
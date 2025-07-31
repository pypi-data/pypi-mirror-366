# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-07-31

### Fixed
- Fixed package metadata configuration for PyPI compatibility
- Resolved license file inclusion issues

### Changed
- Updated package name to `ngits-iot-db`
- Improved build configuration

## [0.1.0] - 2025-07-30

### Added
- Initial release of IoT Database Models
- SQLAlchemy models for IoT sensor data:
  - ElectricityMeasurement and usage models
  - WaterMeasurement and usage models  
  - HeatMeasurement and usage models
  - TemperatureMeasurement model
  - RawMeasurement model for unprocessed data
- Alembic migrations support with existing migration history
- Multi-tenant support via tenant UUID field
- Type-safe enums for sensor types (electricity, water, heat, temperature)
- Helper functions for model mapping
- Full type annotations with py.typed marker

### Features
- PostgreSQL backend support
- Automatic timestamping (created_ts, updated_ts)  
- Unique constraints to prevent duplicate measurements
- Daily and monthly usage aggregation models
- Raw sensor data storage with JSON fields
- External system integration support via external_id and meter_id

### Migration History Included
- 78371c256762_init_schema.py - Initial database schema
- fc391d505594_add_temperature.py - Temperature sensor support
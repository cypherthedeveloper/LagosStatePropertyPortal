# Changelog

All notable changes to the Lagos State Property Portal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Refactored root URL configuration to enforce `/api/v1/` versioning and improve clarity.
- Switched from `mysqlclient` to `PyMySQL` for database connectivity to simplify setup and improve cross-platform compatibility.

### Fixed
- Removed redundant `django-rest-framework` dependency from `requirements.txt`.

### Added
- Initial project setup
- User management system with multi-role support
- Property listing and management features
- Favorites functionality
- Leads and messaging system
- Payment processing with multiple payment methods
- Compliance tracking and reporting
- API documentation with Swagger/ReDoc
- Project documentation

## [0.1.0] - 2023-12-01

### Added
- Initial release with core functionality
- User authentication and authorization
- Basic property management
- Simple search and filter capabilities
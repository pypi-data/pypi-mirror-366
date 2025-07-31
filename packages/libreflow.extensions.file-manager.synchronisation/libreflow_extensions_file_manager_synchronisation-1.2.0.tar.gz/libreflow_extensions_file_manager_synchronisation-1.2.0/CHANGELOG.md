# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)[^1].

<!---
Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

-->

## [Unreleased]

## [1.2.0] - 2025-07-30

* Restore the automatic source site selection for `MultiRequestRevisions` action.

## [1.1.3] - 2024-06-25

### Fixed

* The request session now have the new session arguments for redis cluster replica.

## [1.1.1-2] - 2024-06-13

### Removed

* Old session arguments related to layout management.

## [1.1.0] - 2024-06-03

### Added

* A command-line session which periodically requests file revisions according to request rules. A rule provides a set of target files, and an OID pattern: each revision matching this pattern will be requested for download towards the specified sites.  
One can specify a delay before restarting the requests with the session's command line argument `--delay` (in seconds, default is `180`). A lifetime limit can also be specified to exclude newer revisions with the argument `--lifetime-limit` (in seconds, default is `600`).

## [1.0.0] - 2024-05-15

### Added

* Actions to request file revisions at project, sequence and shot scopes given a revision OID pattern in the wildcard format.

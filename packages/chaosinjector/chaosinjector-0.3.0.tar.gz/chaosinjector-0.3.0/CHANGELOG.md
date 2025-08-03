# CHANGELOG

All notable changes to ChaosInjector will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Русская версия / Russian version](CHANGELOG.ru.md)

## [Unreleased]

- No changes yet. Contributions welcome for upcoming features like async support or custom no-op handlers.

## [0.3.0] - 2025-08-02

### Added
- Support for asynchronous attributes: for coroutines in no-op mode, returns an awaitable stub that yields None after await to avoid crashes in async code (#11).
- Bypass for attributes requested from dunder methods (caller co_name __*__) to prevent breaking internal operations of magic methods, such as __anext__ or __aenter__ (#12).
- @wraps decorator on the wrapper in __handle to preserve __getattribute__ metadata.

### Changed
- Refactored __handle: added inspect.iscoroutinefunction check for handling async callables, with lambda returning __async_stub() instead of simple None (#13).
- Updated wrapper logic to use inspect.currentframe() for bypassing chaos inside dunder callers, ensuring state stability (e.g., self.i in __anext__).

### Fixed
- Fixed potential incompatibility with async callables: previously, no-op for coroutines returned lambda: None, causing TypeError on await; now uses awaitable stub (#14).

### Deprecated
- None.

### Removed
- None, backward compatibility preserved.

### Security
- None.

## [0.2.0] - 2025-07-26

### Added
- Introduced `create_proxy` method for creating non-destructive proxies that preserve the original object's state and type hints, including support for TypeVar generics (#3, #4). This allows users to apply chaos without mutating the source object, enhancing flexibility for parallel usage scenarios.
- Added state copying logic for `__dict__` using copy.deepcopy and manual setattr for `__slots__` in proxy creation, ensuring compatibility with slotted classes and complex objects like dataclasses (#5).
- Implemented overload annotations for the internal `__inject` method to improve type checking with tools like mypy and PyCharm, providing better IDE integration and error prevention (#6).
- Added validation for method_probs dictionary to check if all probabilities are within [0, 1], raising ValueError for invalid values and including detailed error messages (#7).
- Incorporated @wraps decorator in `__handle` to preserve metadata of the original __getattribute__, aiding in debugging and introspection (#8).

### Changed
- Refactored shared logic between `inject` and `create_proxy` into a private `__inject` method with overloads, reducing code duplication and improving maintainability (#2).
- Updated README.md with examples for the new proxy mode, multi-language support, and detailed features, including preservation of isinstance compatibility (#1).
- Minor renaming and reorganization of internal methods (e.g., probability to probability in signatures for consistency) to align with Pythonic standards.

### Fixed
- Ensured isinstance compatibility in proxies by dynamically inheriting from the original class, resolving potential type checking issues in user code (#9).
- Fixed potential deep copy errors for unpickleable attributes in __dict__ by using copy.deepcopy, with fallback for slotted classes (#10).

### Deprecated
- None. All features from 0.1.0 remain fully supported.

### Removed
- None. Backward compatibility preserved.

### Security
- None. No security vulnerabilities addressed in this release, but enhanced validation reduces risks of invalid input leading to unexpected behavior.

## [0.1.0] - 2025-07-25

### Added
- Initial release of ChaosInjector with core functionality: in-place injection of probabilistic behavior via `inject` method.
- Support for probability, decider callables, and method-specific probabilities.
- Basic no-op handling for callable and non-callable attributes.
- Validation for probability ranges.
- Comprehensive unit tests covering key scenarios.

### Changed
- N/A (initial release).

### Fixed
- N/A (initial release).

### Deprecated
- N/A.

### Removed
- N/A.

### Security
- N/A.
# Improvement Plan

The following steps are ordered from simple documentation updates to complex architectural changes. Extensive steps are broken into substeps.

1. Document Python version requirement in `README.md`. **complete**
2. Add installation instructions for optional `Pillow` dependency in `README.md`. **complete**
3. Document the purpose of each example script in `README.md`. **complete**
4. Update `CHANGELOG` to reflect latest version `0.9.21`. **complete**
5. Synchronize `VERSION` file with `CHANGELOG`. **complete**
6. Include `Pillow>=9.0.0` in `setup.py` `install_requires`. **complete**
7. Add `.editorconfig` for consistent code style. **complete**
8. Document virtual environment usage in `README.md`. **complete**
9. Clarify device support matrix in documentation. **complete**
10. Add missing docstrings to all example scripts. **complete**
11. Enable strict linting rules by adjusting `.flake8` ignores. **complete**
12. Add type hints to all functions in `src/example_basic.py`. **complete**
13. Apply type hints to remaining example scripts. **complete**
14. Add `mypy` configuration and initial check in CI. **complete**
15. Create a CONTRIBUTING guide outlining development workflow. **complete**
16. Update `setup.py` classifiers for supported Python versions. **complete**
17. Add `__all__` definitions to modules missing them. **complete**
18. Document available transports in `README.md`. **complete**
19. Create a script to list connected Stream Decks. **complete**
20. Add unit tests for `DeviceManager.enumerate` using dummy transport. **complete**
21. Document testing instructions in `README.md`. **complete**
22. Provide example images in a dedicated `assets` section of docs. **complete**
23. Document environment variables used by the library. **complete**
24. Replace direct path manipulation with `pathlib` in `example_basic.py`. **complete**
25. Add docstrings to all methods in `DeviceMonitor`. **complete**
26. Add type hints to `DeviceMonitor` methods. **complete**
27. Expand test coverage for `DeviceMonitor` start/stop behavior. **complete**
28. Add docstrings to `MacroDeck` private helper methods. **complete**
29. Enforce `black` formatting via CI. **complete**
30. Move CLI logic in tests into separate example script. **complete**
31. Replace `print` statements with `logging` in examples. **complete**
32. Create unit tests for `MacroDeck.get_board_char` error conditions. **complete**
33. Add docstrings to `Transport` abstract methods. **complete**
34. Document return types in `Transport` subclasses. **complete**
35. Add test to confirm `Dummy` transport logs messages. **complete**
36. Incorporate continuous integration using GitHub Actions. **complete**
37. Add badges for build status and coverage to `README.md`. **complete**
38. Implement `ruff` for linting and integrate with CI. **complete**
39. Document how to build and view Sphinx docs locally. **complete**
40. Add code examples for touchscreen APIs in docs. **complete**
41. Split large constants in device classes into separate module.
    - Identify all constant attributes across `StreamDeck` device subclasses.
    - Create new module `StreamDeck/DeviceConstants.py`.
    - Move the constants into the new module without altering values.
    - Update device classes to import from `DeviceConstants`.
    - Add unit tests ensuring constants remain accessible.
42. Replace magic numbers with named constants in device implementations.
    - Audit device modules for numeric literals.
    - Introduce descriptive constant names in `DeviceConstants`.
    - Substitute literals with the new constants.
    - Ensure no behaviour changes via targeted unit tests.
43. Refactor repeated JPEG header bytes into a helper function.
    - Locate all occurrences of raw JPEG header byte sequences.
    - Add `build_jpeg_header()` to new helper module.
    - Replace direct byte arrays with calls to the helper.
    - Verify image payloads remain identical via tests.
44. Add a central configuration class for library settings.
    - Design `Config` dataclass exposing defaults for key parameters.
    - Place the class in `StreamDeck/config.py`.
    - Update modules to read settings from this class.
    - Document configuration usage in the README.
45. Create dedicated exception classes for common error cases.
    - Enumerate frequent error conditions across modules.
    - Add new exceptions in `StreamDeck/exceptions.py`.
    - Replace generic raises with the new exceptions.
    - Extend tests to cover exception handling paths.
46. Introduce logging configuration helper for applications.
    - Provide `setup_logging(level: int)` in `StreamDeck/logging_utils.py`.
    - Allow configuring log format and output destination.
    - Update examples to use this helper.
    - Add unit tests verifying log messages appear with chosen level.
47. Update `MacroDeck.run_loop` to support custom sleep functions.
48. Write tests for `MacroDeck.swap_key_configurations` edge cases.
49. Document concurrency considerations for callbacks.
50. Add asynchronous versions of `DeviceMonitor` methods.
51. Create integration tests covering multiple device types via dummy transport.
52. Convert example scripts into runnable entry points installed via `setup.py`.
53. Add support for reading brightness level from devices if available.
54. Add optional timeout parameter to `DeviceMonitor.start`.
55. Implement context manager for `DeviceManager` to auto-close decks.
56. Add dataclass-based representation for key configurations.
57. Refactor `MacroDeck` board operations into a separate class.
58. Create higher level API for batch image updates.
59. Replace raw thread management with `threading.Thread` subclasses.
60. Add input validation for all public methods.
61. Store configuration data in an SQLite database for persistence.
    - Design schema for decks, keys, dials, and touches.
    - Implement CRUD operations via a small ORM layer.
    - Update existing classes to read/write through the database.
62. Extend unit tests to cover database persistence logic.
63. Add command line tool to export and import configuration data.
64. Implement caching layer to avoid redundant image conversions.
65. Provide plugin interface for additional transport backends.
66. Document plugin development guidelines.
67. Introduce a Streamlit GUI exposing all `MacroDeck` features.
    - Create tabs for key layout, dial controls, and touchscreen.
    - Implement REST endpoints used by GUI actions.
    - Ensure mobile-friendly responsive design.
68. Write end-to-end tests for GUI interactions using `streamlit-testing` guidance.
69. Package GUI as an optional extra in `setup.py`.
70. Implement automatic hot-plug detection using platform hooks.
71. Add event subscription API for applications to receive deck events.
72. Provide asyncio-compatible API variants throughout the library.
73. Add comprehensive error handling for USB transport failures.
74. Create benchmarking suite for image conversion performance.
75. Implement hardware capability discovery for new deck models.
76. Add support for custom key shapes and sizes.
77. Provide configuration templating for common deck layouts.
78. Introduce internationalization support for GUI text.
79. Implement voice control integration as optional feature.
80. Add WebSocket server exposing deck events to remote clients.
81. Write API documentation using `sphinx.ext.autodoc` for all modules.
82. Generate type stub files for third-party usage.
83. Publish coverage reports to Codecov.
84. Add stress tests simulating high-frequency events.
85. Integrate PyInstaller build for a standalone demo app.
86. Create plugin for remote control via networked Stream Decks.
87. Implement secure authentication for remote connections.
88. Add GUI-based macro editor with drag-and-drop support.
89. Provide migration tools for configuration schema changes.
90. Integrate hardware firmware update functionality.
91. Implement cross-platform device permission helpers.
92. Add MQTT integration for home automation workflows.
93. Support dynamic deck discovery over network.
94. Provide containerized development environment via Docker.
95. Optimize memory usage when handling large images.
96. Implement theming support in GUI with customizable styles.
97. Add failover handling between multiple attached devices.
98. Provide extensive user guide with troubleshooting section.
99. Implement plugin marketplace infrastructure.
100. Release version `1.0` with complete documentation and test coverage.

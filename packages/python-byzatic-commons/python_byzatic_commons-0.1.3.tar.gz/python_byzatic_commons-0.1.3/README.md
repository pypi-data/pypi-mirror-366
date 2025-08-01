# PythonByzaticCommons

**PythonByzaticCommons** is a modular utility library for Python that provides a collection of reusable components for file reading, exception handling, logging, in-memory storage, singleton management, and more. Designed for extensibility and clean architecture, it helps accelerate development by offering ready-to-use patterns and interfaces.

Artifact available on pypi:  
https://pypi.org/project/python-byzatic-commons/0.1.0/

```bash
pip install python-byzatic-commons
```

---

## Modules Overview

### `exceptions`
A set of structured exception classes to formalize error handling in complex systems.

- **`BaseErrorException`**: Root base class for domain-specific exceptions.
- **`OperationIncompleteException`**: Indicates partial success or failure in operations.
- **`ExitHandlerException`**: Used to trigger early exit logic in controlled flows.
- **`CriticalErrorException`**: Raised for non-recoverable fatal errors.
- **`NotImplementedException`**: Placeholder for yet-to-be-implemented logic.

---

### `filereaders`
Unified interfaces and concrete implementations for parsing configuration files.

- **Interfaces**:
  - `BaseReaderInterface`: Defines contract for readers returning a dict from a file.

- **Readers**:
  - `JsonFileReader`: Loads `.json` files into Python dictionaries.
  - `YamlFileReader`: Loads `.yaml`/`.yml` files using `PyYAML`.
  - `ConfigParserFileReader`: Loads `.ini`-style config files using `configparser`.

All readers validate input paths and support standard Python error handling.

---

### `in_memory_storages`
In-memory key-value storage layer with interchangeable implementations and management.

- **Interfaces**:
  - `KeyValueDictStorageInterface`, `KeyValueListStorageInterface`, etc.

- **Storages**:
  - `KeyValueDictStorage`: Uses `dict` internally.
  - `KeyValueListStorage`: Uses `list` for indexed access.
  - `KeyValueObjectStorage`: Stores arbitrary Python objects.
  - `KeyValueStringStorage`, `KeyValueModuleTypeStorage`, etc.

- **Manager**:
  - `StoragesManager`: Central registry and access point for storage instances.

Test coverage is included in the `test/` directory.

---

### `logging_manager`
Encapsulates logging configuration and output.

- **`LoggingManagerInterface`**: Describes basic logging interface (`info`, `warn`, `error`, etc.)
- **`LoggingManager`**: Concrete implementation wrapping Python’s built-in `logging` module with a consistent configuration.

Supports colored output, custom formatters, and stream redirection.

---

### `singleton`
Provides a class-based singleton pattern.

- **`Singleton`**: A metaclass-based implementation that ensures a class has only one instance across the application.

Useful for shared services like loggers, configuration managers, etc.

---

## Example Usage

```python
from python_byzatic_commons.filereaders import JsonFileReader
reader = JsonFileReader()
config = reader.read("config.json")
```

```python
import os
import logging
from python_byzatic_commons.logging_manager import LoggingManager

system_script_dir = os.path.abspath(os.path.dirname(__file__))
logger_config_file_path_json = os.path.join(
                system_script_dir,
                'configuration',
                'logger_configuration.json'
            )

logging_manager: LoggingManager = LoggingManager()
logging_manager.init_logging(
    logger_config_file_path_json,
    "JSON"
)
applogger = logging.getLogger("Application-logger")

applogger.debug(f"Creating context")

```

---

## License

This project is licensed under the terms of the **Apache 2.0** license.

# PythonByzaticCommons

**PythonByzaticCommons** is a modular utility library for Python that provides a collection of reusable components for file reading, exception handling, logging, in-memory storage, singleton management, and more. Designed for extensibility and clean architecture, it helps accelerate development by offering ready-to-use patterns and interfaces.

Artifact available on pypi:  
https://pypi.org/project/python-byzatic-commons

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

```python
from python_byzatic_commons.exceptions import OperationIncompleteException
from python_byzatic_commons.exceptions import ExitHandlerException


def main():
    try:
      ...
    except OperationIncompleteException as oie:
        raise ExitHandlerException(oie.args, errno=oie.errno, exception=oie)
    except Exception as e:
        raise ExitHandlerException(e.args, exception=e)
    except KeyboardInterrupt as ki:
        raise ExitHandlerException(ki.args, exception=ki)


if __name__ == '__main__':
    main()
```

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

```python
import os
import sys
from python_byzatic_commons.filereaders import JsonFileReader
from python_byzatic_commons.filereaders.interfaces import BaseReaderInterface


def main():
    runtime_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    logger_config_file_path_json = os.path.join(
        runtime_dir,
        'configuration',
        'configuration.json'
    )
    
    reader: BaseReaderInterface = JsonFileReader()
    config: dict = reader.read(logger_config_file_path_json)
    print(config)


if __name__ == '__main__':
    main()
```

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

```python
from python_byzatic_commons.in_memory_storages.interfaces import KeyValueDictStorageInterface
from python_byzatic_commons.in_memory_storages.key_value_storages.KeyValueDictStorage import KeyValueDictStorage


# create an in-memory dictionary storage
storage: KeyValueDictStorageInterface = KeyValueDictStorage("MyAwsomeStorage")

# create entries
storage.create("foo", {"value": 123})
storage.create("bar", {"value": 456})

# read entry
print(storage.read("foo"))  # → {'value': 123}

# update entry
storage.update("foo", {"value": 999})

# check existence
if storage.contains("foo"):
    print("Entry 'foo' exists!")

# read all
print(storage.read_all())  # → {'foo': {'value': 999}, 'bar': {'value': 456}}

# delete one
storage.delete("bar")

# drop all
storage.drop()
```

---

### `logging_manager`
Encapsulates logging configuration and output.

- **`LoggingManagerInterface`**: Describes basic logging interface (`info`, `warn`, `error`, etc.)
- **`LoggingManager`**: Concrete implementation wrapping Python’s built-in `logging` module with a consistent configuration.

Supports colored output, custom formatters, and stream redirection.

```python
import os
import sys
import logging
from python_byzatic_commons.logging_manager import LoggingManager
from python_byzatic_commons.logging_manager.interfaces import LoggingManagerInterface


def main():
    runtime_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    logger_config_file_path_json = os.path.join(
        runtime_dir,
        'configuration',
        'logger_configuration.json'
    )

    logging_manager: LoggingManagerInterface = LoggingManager()
    logging_manager.init_logging(
        logger_config_file_path_json,
        "JSON"
    )
    
    logger = logging.getLogger("Application-logger")
    
    logger.debug("some debug")


if __name__ == '__main__':
    main()
```

```python
import logging

class SomeClass(object):
    __some_var: list

    def __init__(self, some_var: list):
        self.__logger = logging.getLogger(f"{type(self).__name__}")
        self.__some_var: list = some_var

    def some_method(self, some_other_var: str) -> None:
      self.__logger.debug(f"some_other_var= {some_other_var}")
      self.__logger.debug(f"some_var= {self.__some_var}")
```

---

### `singleton`
Provides a class-based singleton pattern.

- **`Singleton`**: A metaclass-based implementation that ensures a class has only one instance across the application.

Useful for shared services like loggers, configuration managers, etc.

```python
from python_byzatic_commons.singleton import Singleton

class SomeClass(Singleton):
    . . .
```

---

## License

This project is licensed under the terms of the **Apache 2.0** license.

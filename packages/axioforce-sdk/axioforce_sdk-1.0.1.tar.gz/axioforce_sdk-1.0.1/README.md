# Axioforce Python SDK Package

This directory contains the Axioforce Python SDK package and all related files for building and distributing the SDK.

## Contents

- `axioforce_sdk/` - The main Python package
- `setup.py` - Package setup configuration
- `pyproject.toml` - Modern Python packaging configuration
- `MANIFEST.in` - Files to include in the package
- `README_SDK.md` - SDK documentation
- `SDK_MIGRATION_GUIDE.md` - Migration guide from capi_device.py
- `sdk_example.py` - Comprehensive usage examples
- `sdk_csv_example.py` - CSV output example
- `simple_sdk_test.py` - Basic functionality tests

## Building the Package

To build the package distribution files:

```bash
cd python_pkg
python -m build
```

This will create:
- `dist/axioforce_sdk-1.0.0-py3-none-any.whl` (wheel)
- `dist/axioforce_sdk-1.0.0.tar.gz` (source distribution)

## Installing for Development

To install the package in development mode:

```bash
cd python_pkg
python -m pip install -e .
```

## Publishing

To publish to PyPI:

```bash
cd python_pkg
pip install twine
twine upload dist/*
```

## Cross-Platform Support

The package includes native libraries for:
- **macOS**: `libaxioforce_c_api.dylib`
- **Windows**: `axioforce_c_api.dll`
- **Linux**: `libaxioforce_c_api.so` (add when available)

## Usage

After installation, users can:

```python
from axioforce_sdk import AxioforceSDK

with AxioforceSDK() as sdk:
    sdk.initialize_simulator(log_level="info")
    sdk.on_data_received = your_data_handler
    sdk.start_data_collection()
```

Or use command-line tools:
```bash
axioforce-csv --output data.csv --duration 10
axioforce-test --quick
```

## Package Structure

```
python_pkg/
├── axioforce_sdk/
│   ├── __init__.py
│   ├── sdk.py
│   ├── cli.py
│   ├── libaxioforce_c_api.dylib
│   └── axioforce_c_api.dll
├── setup.py
├── pyproject.toml
├── MANIFEST.in
├── README_SDK.md
├── SDK_MIGRATION_GUIDE.md
├── sdk_example.py
├── sdk_csv_example.py
└── simple_sdk_test.py
``` 
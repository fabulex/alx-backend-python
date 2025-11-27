# Python Backend – Unit Testing Project

This project demonstrates effective **unit testing**, **mocking**, **parameterization**, and **integration testing** in Python. It focuses on writing clean, maintainable tests for utility functions and API clients, ensuring correctness and reliability.

## Core Functionality

### utils.py

Contains helper functions commonly used throughout the project:

* **access_nested_map(nested_map, path)**: Retrieves values from deeply nested dictionaries using a tuple path.
* **get_json(url)**: Wrapper around `requests.get().json()` for convenient JSON retrieval.
* **memoize decorator**: Caches method results to avoid repeated computation.

### client.py

Implements API client classes that interact with external web services.

* **GithubOrgClient**: Fetches organization details, repository lists, and public repo metadata from GitHub’s API.

### fixtures.py

Provides static test datasets (mock API responses) used in integration tests.

## Testing Overview

The project uses:

* `unittest` — Python’s built-in testing framework
* `parameterized` — To test multiple inputs efficiently
* `unittest.mock` — For mocking external dependencies
* Integration testing using live-like mocked GitHub API responses

### Included Test Modules

#### test_utils.py

Tests:

* `access_nested_map` (including exception cases)
* `get_json` with mocked requests
* `memoize` behavior with caching verification

#### test_client.py

Tests:

* GithubOrgClient.org property
* _public_repos_url
* public_repos
* has_license
* Integration tests with full GitHub API mock payloads

## Running the Tests

Ensure you are using **Python 3.7** (Ubuntu 18.04 compatible):

```bash
python3 -m unittest discover tests
```

Run a specific file:

```bash
python3 -m unittest tests/test_utils.py
```

Verbose mode:

```bash
python3 -m unittest -v
```

## Requirements & Compliance

* Environment: **Ubuntu 18.04 LTS**
* Python version: **Python 3.7**
* All files:

  * Must start with `#!/usr/bin/env python3`
  * Must be executable
  * Must follow **pycodestyle 2.5**
  * Must have real, complete docstrings
  * Must end with a newline
* Functions and methods must be type-annotated

## Learning Objectives

By completing this project, you will understand:

* How to write unit tests in Python
* How to use `parameterized` for multiple test cases
* How to mock HTTP calls using `unittest.mock`
* How to test decorators and cached properties
* How to conduct integration testing with fixtures
* How to structure a maintainable test suite

## Author

Project designed and implemented by **Fabulex**.

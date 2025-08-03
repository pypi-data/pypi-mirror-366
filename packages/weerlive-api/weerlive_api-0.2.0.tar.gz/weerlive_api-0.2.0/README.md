# Python Weerlive

[![PyPI version][pypi_badge]][pypi_link]
[![License][license_badge]][license_link]
[![Codecov][codecov_badge]][codecov_link]
[![Sonar quality gate][sonar_badge]][sonar_link]
[![GitHub repo stars][stars_badge]][stars_link]
[![Buy me a coffee][buymecoffee_badge]][buymecoffee_link]

Asynchronous Python client for the Weerlive API.

Easily integrate Weerlive's services into your Python application using this client, and enjoy enhanced type safety and autocomplete support.

For more details about the APIs, visit the [Weerlive API page](https://weerlive.nl/delen.php), where you can sign up and get your API key.

## Installation

You can install this package using your preferred package manager. For example, using pip:

```sh
pip install weerlive-api
```

## Usage

To use the Weerlive API, you can import it in your Python scripts and start interacting with the Weerlive API. Here is a simple example:

```python
import asyncio

from weerlive import WeerliveApi


async def main():
    """Show example of fetching weather info from Weerlive API."""
    async with WeerliveApi(api_key="demo") as weerlive:
        weather = await weerlive.city("Amsterdam")
        print(weather)


if __name__ == "__main__":
    asyncio.run(main())

```

## Contributing

Contributions are welcome! Please familiarize yourself with the [contribution guidelines](CONTRIBUTING.md). This document will also help you set up your development environment.

---

Thank you for your interest in the Python Weerlive client! If you have any questions or need further assistance, feel free to open an issue or submit a pull request.

[pypi_link]: https://pypi.org/project/weerlive-api/
[pypi_badge]: https://img.shields.io/pypi/v/weerlive-api?style=for-the-badge
[license_link]: https://github.com/golles/python-weerlive/blob/main/LICENSE
[license_badge]: https://img.shields.io/github/license/golles/python-weerlive.svg?style=for-the-badge
[codecov_link]: https://app.codecov.io/gh/golles/python-weerlive
[codecov_badge]: https://img.shields.io/codecov/c/github/golles/python-weerlive?style=for-the-badge
[sonar_link]: https://sonarcloud.io/project/overview?id=golles_python-weerlive
[sonar_badge]: https://img.shields.io/sonar/quality_gate/golles_python-weerlive?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge
[stars_link]: https://github.com/golles/python-weerlive/stargazers
[stars_badge]: https://img.shields.io/github/stars/golles/python-weerlive?style=for-the-badge
[buymecoffee_link]: https://www.buymeacoffee.com/golles
[buymecoffee_badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge

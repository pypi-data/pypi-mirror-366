# setup-selenium-testing
I get tired of having to rewrite the setup logic for selenium drivers 
in every project.  Time to consolidate.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/bandophahita/setup_selenium/blob/master/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/setup-selenium-testing.svg)](https://pypi.org/project/setup-selenium-testing/)
[![Supported Versions](https://img.shields.io/pypi/pyversions/setup-selenium-testing.svg)](https://pypi.org/project/setup-selenium-testing)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[![Issues](https://img.shields.io/github/issues-raw/bandophahita/setup_selenium.svg)](https://github.com/bandophahita/setup_selenium/issues)

[![Build Status](https://github.com/bandophahita/setup_selenium/actions/workflows/test-linux.yml/badge.svg)](https://github.com/bandophahita/setup_selenium/actions/workflows/test-linux.yml)
[![Build Status](https://github.com/bandophahita/setup_selenium/actions/workflows/test-mac-m1.yml/badge.svg)](https://github.com/bandophahita/setup_selenium/actions/workflows/test-mac-m1.yml)
[![Build Status](https://github.com/bandophahita/setup_selenium/actions/workflows/test-windows.yml/badge.svg)](https://github.com/bandophahita/setup_selenium/actions/workflows/test-windows.yml)
[![Build Status](https://github.com/bandophahita/setup_selenium/actions/workflows/lint.yml/badge.svg)](https://github.com/bandophahita/setup_selenium/actions/workflows/lint.yml)


# Instantiating SetupSelenium

This will automatically handle any downloading of drivers or browsers via `SeleniumManager`

```python
from setup_selenium import SetupSelenium

s = SetupSelenium(headless=True)
assert s.driver.service.is_connectable()
```

Advanced usage:

```python
from setup_selenium import Browser, SetupSelenium

s = SetupSelenium(Browser.FIREFOX, headless=True, driver_version="118.0.5993.70")
s = SetupSelenium(Browser.CHROME, headless=True, driver_version="118.0.5993.70",
                  driver_path="/path/to/webdriver"
                  )
```

> [!NOTE] 
> Version and path arguments follow the logic of 
> [SeleniumManager](https://www.selenium.dev/documentation/selenium_manager/). 
> Caution is advised in cases where version and path do not match. 
> See their documentation.

# Install Driver only
```python
from setup_selenium import Browser, SetupSelenium

driver_path, browser_path = SetupSelenium.install_driver(Browser.CHROME, driver_version="118.0.5993.70")
```

# Create driver only

```python
from setup_selenium import Browser, SetupSelenium

driver = SetupSelenium.create_driver(browser=Browser.CHROME, headless=True)
```

Advanced usage:

```python
from setup_selenium import Browser, SetupSelenium

driver = SetupSelenium.create_driver(
    browser=Browser.CHROME,
    headless=True,
    enable_log_performance=False,
    enable_log_console=False,
    enable_log_driver=False,
    log_dir="./logs",
    binary="/usr/bin/chromium",
    driver_path="/usr/bin/chromedriver",
)
```

> [!NOTE]
> It is possible to enable the performance and console logging
> but only for chrome based browsers. This only enables the browser ability.
> It is up to the tester to handle logging the messages.


# Custom logger
```python
import logging
from setup_selenium import Browser, SetupSelenium, set_logger

set_logger(logging.getLogger("your_custom_logger"))
driver = SetupSelenium.create_driver(browser=Browser.CHROME, headless=True)
```

# Automatic driver and browser installation
This package not only handles setup of the webdriver but also will
automatically install the webdriver and/or browser depending on your
configuration.

If you do not provide a `driver_path` argument to `create_driver` the package
will utilize `selenium-manager` to install the webdriver for the browser type selected.



If the `selenium-manager` cannot find the install path for the browser type
(which is usually in the native install path) it will download a version of the browser
and use that.  

Passing a valid `binary_path` will not trigger any download of the browser.
Passing a valid `driver_path` will not trigger any download of the webdriver.


CHANGELOG
---------
### version 1.0.2

- removed python 3.8 support

### version 1.0.1

- removed `--remote-debugging-pipe` from default chrome options (causes older chrome to crash)

### version 1.0.0

- official release

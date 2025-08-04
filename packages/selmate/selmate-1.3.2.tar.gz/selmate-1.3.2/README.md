# Selmate

Selmate is a Python utility library designed to enhance Selenium WebDriver automation by providing human-like
interactions, robust exception handling, and utilities for common web automation tasks. It simplifies interactions with
web elements, handles popups, normalizes URLs, and simulates natural user behavior like mouse movements and scrolling.

## Features

- **Safe Element Interactions**: Wrappers for Selenium operations (clicks, scrolls, etc.) with built-in exception
  handling for stale elements, timeouts, and more.
- **Human-Like Behavior**: Simulates realistic mouse movements, scrolling, and latency to mimic human interactions.
- **Popup Handling**: Automatically detects and handles popup banners, including those within iframes, with options to
  accept or close them.
- **URL Normalization**: Utilities to normalize URLs relative to a base URL, with configurable handling of query
  strings, fragments, and parameters.
- **JavaScript Integration**: Execute JavaScript for advanced interactions like smooth scrolling, element removal, and
  visibility checks.
- **Text Similarity**: Identify confirmation buttons or close buttons using fuzzy text matching.

## Installation

Install Selmate via pip:

```bash
pip install selmate
```

## Usage

Here are some examples of using Selmate's core functionalities:

### Example 1: Safe Element Click

```python
from selenium import webdriver
from selmate.composites import complex_click
from selmate.selenium_primitives import find_element_safely
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://example.com")

# Safely find and click a button
button = find_element_safely(By.ID, "submit-button", driver)
if button and complex_click(button, driver):
    print("Button clicked successfully")

driver.quit()
```

### Example 2: Handling Popup Banners

```python
from selenium import webdriver
from selmate.composites import bypass_popup_banners

driver = webdriver.Chrome()
driver.get("https://example.com")

# Automatically handle popup banners
bypass_popup_banners(driver, observation_capacity=50, success_capacity=3, try_close=True)
print("Popups handled")

driver.quit()
```

### Example 3: Human-Like Mouse Movement

```python
from selenium import webdriver
from selmate.composites import wander_between_2_elements
from selmate.selenium_primitives import find_element_safely
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://example.com")

# Find two elements and simulate mouse movement between them
element1 = find_element_safely(By.ID, "element1", driver)
element2 = find_element_safely(By.ID, "element2", driver)
if element1 and element2:
    wander_between_2_elements(element1, element2, driver)

driver.quit()
```

## License

Selmate is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, open an issue or contact the maintainer at waxbid@gmail.com.
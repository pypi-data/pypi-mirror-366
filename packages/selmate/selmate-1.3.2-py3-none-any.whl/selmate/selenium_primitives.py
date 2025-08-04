from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selmate.safe_exceptions import safe_out_of_bound, safe_stale, safe_timeout, safe_click_interception, \
    safe_not_interactable


def selenium_tabs_amount(driver: WebDriver):
    """
    Get amount of opened tabs.
    :param driver: The WebDriver instance to interact with the browser.
    :return: Amount of opened tabs.
    """
    return len(driver.window_handles)


def selenium_switch_to_first_tab(driver: WebDriver):
    """
    Switch to the first browser tab/window.
    :param driver: The WebDriver instance to interact with the browser.
    :return: True if the switch was successful, False if no tabs are open.
    """
    if not driver.window_handles:
        return False

    driver.switch_to.window(driver.window_handles[0])

    return True


def selenium_switch_to_last_tab(driver: WebDriver):
    """
    Switch to the last browser tab/window.
    :param driver: The WebDriver instance to interact with the browser.
    :return: True if the switch was successful, False if no tabs are open.
    """
    if not driver.window_handles:
        return False

    driver.switch_to.window(driver.window_handles[-1])

    return True


@safe_timeout(def_val=False)
def wait_selection(element: WebElement, driver, timeout=1.0):
    """Waits for an element to be selected.
    :param element: The web element to check for selection.
    :param driver: The Selenium WebDriver instance.
    :param timeout: Time to wait for the element to be selected.
    :return: True if the element is selected, False otherwise.
    """
    return WebDriverWait(driver, timeout).until(
        expected_conditions.element_to_be_selected(element)
    )


@safe_not_interactable(def_val=None)
@safe_stale(def_val=None)
def selenium_element_center(element: WebElement):
    """Calculates the center coordinates of a web element.
    :param element: The web element to find the center of.
    :return: Tuple of (x, y) coordinates of the element's center.
    """
    rect = element.rect
    return rect['x'] + rect['width'] / 2, rect['y'] + rect['height'] / 2


@safe_not_interactable(def_val=False)
@safe_click_interception(def_val=False)
@safe_out_of_bound(def_val=False)
def selenium_click(element: WebElement):
    """Performs a click on a web element.
    :param element: The web element to click.
    :return: True if the click was successful.
    """
    element.click()
    return True


@safe_timeout(def_val=None)
def find_element_safely(by, value, driver, timeout=0.01):
    """Safely finds an element on the page with a short timeout.
    :param by: The method used to locate the element.
    :param value: The value for the locator.
    :param driver: The Selenium WebDriver instance.
    :param timeout: The maximum time to wait for the element.
    :return: The found web element or None if not found.
    """
    return WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located((by, value))
    )


@safe_not_interactable(def_val=False)
@safe_out_of_bound(def_val=False)
@safe_stale(def_val=False)
def selenium_scroll_to_element(element: WebElement, driver):
    """Scrolls to a web element using ActionChains.
    :param element: The web element to scroll to.
    :param driver: The Selenium WebDriver instance.
    :return: True if the scroll was successful.
    """
    ActionChains(driver).move_to_element(element).perform()
    return True

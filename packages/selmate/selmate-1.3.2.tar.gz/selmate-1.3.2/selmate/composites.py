import logging
import random
import re
from itertools import pairwise
from operator import itemgetter
from typing import List, Any, Generator
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from selenium.webdriver import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selmate.constants import WINDOW_LOCATION_HREF_JS_PATTERN
from selmate.humanity.constants import HUMAN_SCROLL_LATENCY
from selmate.humanity.latency import human_click_latency, human_mouse_move_latency, human_focus_element_latency, \
    human_observe_view_latency, human_scroll_latency, human_key_type_latency
from selmate.js_primitives import js_smooth_scroll, js_remove_element, js_need_scroll_to_element, js_scroll_to_element, \
    js_click, js_choose_elements_above_z_index
from selmate.safe_exceptions import safe_timeout, safe_stale, safe_out_of_bound, safe_not_found, safe_not_interactable
from selmate.selenium_primitives import find_element_safely, selenium_element_center, selenium_scroll_to_element, \
    selenium_click
from selmate.utils import is_confirmation_text, norm_string, latency_time, normalize_url, \
    is_webpage, generate_curved_path

logger = logging.getLogger(__name__)


@safe_not_interactable(def_val=False)
@safe_not_found(def_val=False)
@safe_stale(def_val=False)
def selenium_human_type(text: str, element: WebElement) -> bool:
    """
    Simulate human-like typing into a web element.
    :param text: The text to type.
    :param element: The web element to type into.
    """
    for c in text:
        element.send_keys(c)
        human_key_type_latency()

    return True


def wandering_between_elements(elements, driver, max_moves=0, mouse_step=10.0):
    """Simulates mouse wandering between pairs of elements.
    :param elements: List of elements to wander between.
    :param driver: The Selenium WebDriver instance.
    :param max_moves: Maximum number of moves to perform.
    :param mouse_step: Amount of pixels for one scroll.
    :return: Tuple of the last element and number of moves made.
    """
    move_cnt = 0
    el2 = None
    for el1, el2 in pairwise(elements):
        if el1 is None or not element_displayed_enabled(el1):
            continue

        if el2 is None or not element_displayed_enabled(el2):
            continue

        wander_between_2_elements(el1, el2, driver, mouse_step, 0.01)
        human_observe_view_latency()

        move_cnt += 1
        if max_moves and move_cnt >= max_moves:
            break

    return el2, move_cnt


def get_current_base_url(driver):
    """Retrieves the base URL from the page or driver.
    :param driver: The Selenium WebDriver instance.
    :return: The base URL of the current page.
    """
    base_tag = find_element_safely(By.TAG_NAME, 'base', driver)
    if base_tag:
        base_current_url = base_tag.get_attribute("href")
    else:
        base_current_url = driver.current_url

    parsed_url = urlparse(base_current_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path if parsed_url.path else ''}"


def find_transition_buttons(base_url, driver):
    """Finds navigation elements like links or buttons.
    :param base_url: The base URL for normalizing links.
    :param driver: The Selenium WebDriver instance.
    :return: List of navigation web elements.
    """
    xpath_selector = (
        "//a[@href] | "
        "//button[@onclick or @data-href or contains(@class, 'nav')] | "
        "//*[contains(@class, 'link') or contains(@class, 'menu-item')]"
    )
    elements = driver.find_elements(By.XPATH, xpath_selector)

    navigation_elements = []
    for element in elements:
        if not element_displayed_enabled(element):
            continue

        url = get_element_url(element)
        if not url:
            navigation_elements.append(element)
            continue

        norm_url = normalize_url(url, base_url, True, True, True)
        if not norm_url:
            navigation_elements.append(element)
            continue

        if is_webpage(norm_url):
            navigation_elements.append(element)
            continue

    return navigation_elements


@safe_stale(def_val=None)
@safe_not_found(def_val=None)
@safe_not_interactable(def_val=None)
def get_element_url(element: WebElement):
    """Extracts the URL from an element's attributes.
    :param element: The web element to check.
    :return: The URL if found, None otherwise.
    """
    tag_name = element.tag_name

    if tag_name == "a":
        url = element.get_attribute("href")
        if url:
            return url

    elif tag_name == "button":
        data_href = element.get_attribute("data-href")
        if data_href:
            return data_href

        onclick = element.get_attribute("onclick")
        if onclick:
            match = re.search(WINDOW_LOCATION_HREF_JS_PATTERN, onclick)
            if match:
                return match.group(1)

    data_href = element.get_attribute("data-href")
    if data_href:
        return data_href

    return None


def selenium_random_vertical_scroll(driver, from_ratio=-0.5, to_ratio=0.5, step=30):
    """Performs a random vertical scroll within a ratio range.
    :param driver: The Selenium WebDriver instance.
    :param from_ratio: Minimum scroll ratio.
    :param to_ratio: Maximum scroll ratio.
    :param step: Amount of pixels for one scroll.
    """
    doc_height = driver.execute_script("return document.body.scrollHeight")
    aim_ratio = random.uniform(from_ratio, to_ratio)
    logger.debug(f'Aim ratio for random selenium human scroll: {aim_ratio:.2f}.')
    on_delta = int(aim_ratio * doc_height)

    selenium_human_vertical_scroll(on_delta, driver, step)


def selenium_human_vertical_scroll(y_delta, driver, step=30):
    """Performs a smooth vertical scroll by a specified delta.
    :param y_delta: The vertical distance to scroll.
    :param driver: The Selenium WebDriver instance.
    :param step: Amount of pixels for one scroll.
    """
    steps = abs(int(y_delta / step))
    if y_delta < 0:
        step *= -1

    actions = ActionChains(driver)
    for i in range(steps):
        actions.scroll_by_amount(0, step).pause(latency_time(*HUMAN_SCROLL_LATENCY))

    actions.perform()


def js_random_human_scroll(driver, from_ratio=0.25, to_ratio=1.0, step=30, to_x=0):
    """Performs a random vertical scroll using JavaScript.
    :param driver: The Selenium WebDriver instance.
    :param from_ratio: Minimum scroll ratio.
    :param to_ratio: Maximum scroll ratio.
    :param step: Amount of pixels for one scroll.
    :param to_x: Target x-coordinate for scroll.
    """
    doc_height = driver.execute_script("return document.body.scrollHeight")
    aim_ratio = random.uniform(from_ratio, to_ratio)
    logger.debug(f'Aim ratio for random js human scroll: {aim_ratio:.2f}.')
    to_y = aim_ratio * doc_height

    js_human_vertical_scroll(to_y, driver, step, to_x)


def js_human_vertical_scroll(to_y, driver, step=30, to_x=0):
    """Performs a smooth vertical scroll to a y-coordinate using JavaScript.
    :param to_y: Target y-coordinate.
    :param driver: The Selenium WebDriver instance.
    :param step: Amount of pixels for one scroll.
    :param to_x: Target x-coordinate.
    """
    steps = int(to_y / step)

    for i in range(steps):
        js_smooth_scroll(to_x, i * step, driver)
        human_scroll_latency()


def selenium_find_close_buttons(parent: WebElement | WebDriver, text_similarity_threshold=0.75):
    """Finds close buttons within a parent element or driver.
    :param parent: The parent element or WebDriver to search in.
    :param text_similarity_threshold: Similarity threshold for button text.
    :return: List of close button elements.
    """
    css_selector = "button, [role='button'], [type='button']"
    close_text_variants = {'закрыть', 'close', '×', 'x'}

    close_buttons = []
    for button in parent.find_elements(By.CSS_SELECTOR, css_selector):
        try:
            btn_text = button.text
            norm_btn_text = norm_string(btn_text)
            norm_value = norm_string(button.get_attribute('value')) or ''
            norm_aria_label = norm_string(button.get_attribute('aria-label')) or ''
            norm_title = norm_string(button.get_attribute('title')) or ''
            norm_class_name = norm_string(button.get_attribute('class'))
            data_attrs = button.get_attribute('data-dismiss') or button.get_attribute('data-close') or ''

            if (
                    any(map(
                        lambda close_text_var:
                        fuzz.ratio(norm_btn_text, close_text_var) / 100 > text_similarity_threshold,
                        close_text_variants
                    )) or
                    'close' in norm_class_name or
                    'close' in norm_value or
                    'close' in norm_aria_label or
                    'close' in norm_title or
                    data_attrs.lower() in {'close', 'modal', 'dialog'}
            ):
                close_buttons.append(button)
                logger.debug(f'Button <{btn_text}> was classified as a close button.')
        except Exception as e:
            continue

    return close_buttons


@safe_not_found(def_val=0)
@safe_stale(def_val=0)
def soup_count_children(element: WebElement):
    """Counts the number of child elements using BeautifulSoup.
    :param element: The web element to analyze.
    :return: Number of child elements.
    """
    el_html = element.get_attribute('innerHTML')
    soup = BeautifulSoup(el_html, 'lxml')
    all_elements = soup.find_all()
    return len(all_elements)


def bypass_popup_banners_with_iframes(
        driver, observation_capacity=100, success_capacity=5,
        try_close=True, allow_removing_when_closing=True
):
    """Bypasses popup banners, including those in iframes.
    :param driver: The Selenium WebDriver instance.
    :param observation_capacity: Maximum elements to observe.
    :param success_capacity: Maximum successful actions.
    :param try_close: Whether to attempt closing popups.
    :param allow_removing_when_closing: Whether to allow element removal.
    :return: True if successful, False otherwise.
    """
    body = find_element_safely(By.TAG_NAME, 'body', driver, timeout=1.0)
    if body is None:
        logger.debug('Body element not found for bypassing popup banners.')
        return False

    iframes = find_available_elements_gtr(By.TAG_NAME, 'iframe', body)
    for iframe in iframes:
        if not element_displayed_enabled(iframe):
            continue

        driver.switch_to.frame(iframe)
        logger.debug('Switched to iframe to search for popup banners.')
        bypass_popup_banners_with_iframes(
            driver, observation_capacity, success_capacity,
            try_close, allow_removing_when_closing
        )
        logger.debug('Returned from iframe after searching for popup banners.')
        driver.switch_to.parent_frame()

    bypass_popup_banners(driver, observation_capacity, success_capacity, try_close, allow_removing_when_closing)

    return True


def bypass_popup_banners(
        driver, observation_capacity=100, success_capacity=5,
        try_close=True, allow_removing_when_closing=True
):
    """Bypasses popup banners by accepting or closing them.
    :param driver: The Selenium WebDriver instance.
    :param observation_capacity: Maximum elements to observe.
    :param success_capacity: Maximum successful actions.
    :param try_close: Whether to attempt closing popups.
    :param allow_removing_when_closing: Whether to allow element removal.
    """
    elements = find_top_available_elements(By.CSS_SELECTOR, 'div', driver)
    logger.debug(f'Found {len(elements)} elements as potential popup banners.')
    cnt = 0
    suc_cnt = 0
    for el in elements:
        cnt += 1
        if not element_displayed_enabled(el):
            continue

        if accept_popup_banner(el, driver):
            suc_cnt += 1
        elif try_close:
            logger.debug('Failed to accept popup banner. Attempting to close.')
            close_element(el, driver, allow_removing=allow_removing_when_closing)

        if cnt > observation_capacity:
            logger.debug(f'Observation limit of <{observation_capacity}> elements reached.')
            break

        if suc_cnt > success_capacity:
            logger.debug(f'Confirmation limit of <{success_capacity}> reached.')
            break


@safe_not_found(def_val=True)
@safe_stale(def_val=True)
def close_element(element, driver, allow_removing=True, close_btn_text_threshold=0.75):
    """Closes an element by clicking a close button or removing it.
    :param element: The web element to close.
    :param driver: The Selenium WebDriver instance.
    :param allow_removing: Whether to allow element removal.
    :param close_btn_text_threshold: Similarity threshold for close button text.
    :return: True if the element was closed or removed.
    """
    close_buttons = selenium_find_close_buttons(element, close_btn_text_threshold)
    for close_btn in close_buttons:
        if not element_displayed_enabled(close_btn):
            logger.debug('Close button is no longer available in the element.')
            continue

        rect = element.rect
        move_radius = 2 * max(rect['width'], rect['height'])
        btn_center = selenium_element_center(element)
        x, y = (0, 0) if btn_center is None else btn_center
        logger.debug(f'Close button center coordinates: x={x}, y={y}.')

        if complex_click(close_btn, driver):
            logger.debug('Successfully clicked the close button in the element.')
            human_click_latency()
        else:
            logger.debug('Failed to click the close button.')
            continue

        logger.debug('Starting random mouse movement near the close button.')
        random_mouse_move_in_vicinity(int(move_radius), driver, int(x), int(y))

        if not element_displayed_enabled(element):
            logger.debug('Element successfully disappeared after clicking the close button.')
            return True

    logger.debug('Failed to close the element.')
    if not allow_removing:
        return False

    logger.debug('Attempting to remove the element.')
    return js_remove_element(element, driver)


def accept_popup_banner(banner, driver):
    """Accepts a popup banner by clicking checkboxes or confirmation buttons.
    :param banner: The popup banner element.
    :param driver: The Selenium WebDriver instance.
    :return: True if the banner was accepted.
    """
    avb_checkboxes = find_available_elements_gtr(
        By.CSS_SELECTOR,
        'input[type="checkbox"], [role="input"][type="checkbox"]',
        banner
    )
    for avb_checkbox in avb_checkboxes:
        logger.debug('Found an available checkbox in the popup banner.')
        if complex_click(avb_checkbox, driver, True):
            logger.debug('Successfully clicked the checkbox in the popup banner.')
            human_click_latency()

    button_elements = choose_confirmation_buttons(banner, 0.75, True)
    logger.debug(f'Found <{len(button_elements)}> confirmation buttons in the popup banner.')
    for btn in button_elements:
        if not element_displayed_enabled(btn):
            logger.debug('Confirmation button is no longer available in the popup banner.')
            continue

        rect = btn.rect
        move_radius = 2 * max(rect['width'], rect['height'])
        btn_center = selenium_element_center(btn)
        x, y = (0, 0) if btn_center is None else btn_center
        logger.debug(f'Confirmation button center coordinates: x={x}, y={y}.')

        if selenium_scroll_to_element(btn, driver):
            human_observe_view_latency()
        else:
            logger.debug('Failed to scroll to the confirmation button via Selenium.')

        if complex_click(btn, driver):
            logger.debug('Successfully clicked the confirmation button in the popup banner.')
            human_click_latency()
        else:
            logger.debug('Failed to click the confirmation button.')
            continue

        logger.debug('Starting random mouse movement near the confirmation button.')
        random_mouse_move_in_vicinity(int(move_radius), driver, int(x), int(y))

        if not element_displayed_enabled(btn):
            logger.debug('Confirmation button successfully disappeared after clicking.')
            return True

    return False


def complex_click(element: WebElement, driver, prevent_unselect=True):
    """Performs a complex click operation with scrolling if needed.
    :param element: The web element to click.
    :param driver: The Selenium WebDriver instance.
    :param prevent_unselect: Whether to avoid clicking already selected elements.
    :return: True if the click was successful.
    """
    if not element_displayed_enabled(element):
        logger.debug('Click failed because the element is not available.')
        return False

    if prevent_unselect and element.is_selected():
        logger.debug('No click needed; the element is already selected.')
        return True

    if js_need_scroll_to_element(element, driver):
        logger.debug('Scrolling required for element click. Using JavaScript.')
        js_scroll_to_element(element, driver)
        human_observe_view_latency()

    if not selenium_click(element):
        logger.debug('Selenium click failed. Attempting JavaScript click.')
        human_click_latency()
        return js_click(element, driver)

    return True


def random_mouse_move_in_vicinity(radius, driver, x1=0, y1=0, mouse_step=10.0, eps=0.1):
    """Moves the mouse randomly within a radius of a point.
    :param radius: The radius for random movement.
    :param driver: The Selenium WebDriver instance.
    :param x1: Starting x-coordinate.
    :param y1: Starting y-coordinate.
    :param mouse_step: Amount of pixels for one scroll.
    :param eps: Minimum movement threshold.
    """
    window_size = driver.get_window_size()
    max_x = window_size['width']
    max_y = window_size['height']

    x2, y2 = random.randint(x1 - radius, x1 + radius), random.randint(y1 - radius, y1 + radius)
    x2 = min(max_x, max(0, x2))
    y2 = min(max_y, max(0, y2))

    actions = ActionChains(driver)
    path = generate_curved_path(x1, y1, x2, y2, mouse_step)
    logger.debug(f'Generated mouse path: {path}.')
    suc_step_cnt, total_step_cnt = move_mouse_by_path(path, actions, x1, y1, eps)

    logger.debug(f'Mouse movements in vicinity: {suc_step_cnt}/{total_step_cnt}.')


def find_top_available_elements(by, value, driver, skip_under_one=True, sort_z_children_desc=True) -> List[WebElement]:
    """Finds topmost available elements by z-index and visibility.
    :param by: The method to locate elements.
    :param value: The locator value.
    :param driver: The Selenium WebDriver instance.
    :param skip_under_one: Whether to skip elements with z-index < 1.
    :param sort_z_children_desc: Whether to sort by z-index and children count.
    :return: List of available web elements.
    """
    sort_values = []
    avb_elements = []

    @safe_stale(def_val=None)
    @safe_not_found(def_val=None)
    def _el_score(el):
        if not element_displayed_enabled(el):
            return None
        z_index = el.value_of_css_property("z-index")
        z_index_value = int(z_index) if z_index.isdigit() else -1
        if skip_under_one and z_index_value < 1:
            return None

        els_amount = soup_count_children(el)

        return z_index_value, els_amount

    elements = None
    if by == By.CSS_SELECTOR and skip_under_one:
        try:
            elements = js_choose_elements_above_z_index(1, driver, value)
        except Exception as e:
            logger.debug(f'Failed to find top elements via JavaScript: <{str(e)}>.')
            pass

    if not elements:
        elements = driver.find_elements(by, value)

    for element in elements:
        score = _el_score(element)
        if score is None:
            continue
        sort_values.append(score)
        avb_elements.append(element)

    if sort_z_children_desc:
        return [el for _, el in sorted(zip(sort_values, avb_elements), key=itemgetter(0), reverse=True)]

    return avb_elements

@safe_not_interactable(def_val=False)
@safe_stale(def_val=False)
@safe_out_of_bound(def_val=False)
def wander_between_2_elements(
        from_element: WebElement, to_element: WebElement, driver: WebDriver, mouse_step=10.0, eps=0.01
):
    """Moves the mouse between two elements along a curved path.
    :param from_element: Starting web element.
    :param to_element: Ending web element.
    :param driver: The Selenium WebDriver instance.
    :param mouse_step: Amount of pixels for one scroll.
    :param eps: Minimum movement threshold.
    :return: True if the movement was successful.
    """
    actions = ActionChains(driver)

    actions.move_to_element(from_element).perform()
    human_focus_element_latency()

    first_element_center = selenium_element_center(from_element)
    second_element_center = selenium_element_center(to_element)

    suc_step_cnt, total_step_cnt = 0, 0
    if first_element_center and second_element_center:
        x1, y1 = first_element_center
        x2, y2 = second_element_center
        path = generate_curved_path(x1, y1, x2, y2, mouse_step)
        suc_step_cnt, total_step_cnt = move_mouse_by_path(path, actions, x1, y1, eps)

    actions.move_to_element(to_element).perform()

    logger.debug(f'Mouse movements while wandering between elements: {suc_step_cnt}/{total_step_cnt}.')
    return bool(suc_step_cnt)


def move_mouse_by_path(path, actions, x1=0, y1=0, eps=0.01):
    """Moves the mouse along a specified path.
    :param path: List of (x, y) coordinates.
    :param actions: ActionChains instance.
    :param x1: Starting x-coordinate.
    :param y1: Starting y-coordinate.
    :param eps: Minimum movement threshold.
    :return: Tuple of successful and total steps.
    """

    @safe_out_of_bound(def_val=False)
    def _safely_move(_dx, _dy):
        actions.move_by_offset(_dx, _dy).perform()
        return True

    suc_step_cnt = 0
    total_step_cnt = 0
    prev_x, prev_y = x1, y1
    for x, y in path:
        total_step_cnt += 1

        dx, dy = x - prev_x, y - prev_y
        logger.debug(f'Mouse moving: dx={dx}, dy={dy}.')
        if abs(dx) < eps and abs(dy) < eps:
            continue

        move_suc = _safely_move(dx, dy)
        suc_step_cnt += int(move_suc)

        if not move_suc:
            continue

        human_mouse_move_latency()
        prev_x, prev_y = x, y

    return suc_step_cnt, total_step_cnt


@safe_timeout(def_val=False)
def wait_for_page_load(driver, timeout=30):
    """Waits for the page to fully load.
    :param driver: The Selenium WebDriver instance.
    :param timeout: Maximum time to wait.
    :return: True if the page loaded successfully.
    """
    WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
    )

    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    return True


@safe_not_found(def_val=False)
@safe_stale(def_val=False)
def element_displayed_enabled(element: WebElement):
    """Checks if an element is displayed and enabled.
    :param element: The web element to check.
    :return: True if the element is displayed and enabled.
    """
    return element.is_displayed() and element.is_enabled()


def find_available_elements_gtr(by, value, parent: WebElement) -> Generator[WebElement, Any, None]:
    """Yields available elements from a parent element.
    :param by: The method to locate elements.
    :param value: The locator value.
    :param parent: The parent web element.
    :return: Generator of available web elements.
    """
    skipped_cnt = 0
    for el in parent.find_elements(by, value):
        if element_displayed_enabled(el):
            yield el
        else:
            skipped_cnt += 1
    if skipped_cnt:
        logger.debug(f'Skipped <{skipped_cnt}> elements of <{value}> because they are not available.')


@safe_stale(def_val=[])
@safe_not_found(def_val=[])
def choose_confirmation_buttons(parent: WebElement, threshold=0.75, sort_similarity_desc=False) -> List[WebElement]:
    """Selects confirmation buttons based on text similarity.
    :param parent: The parent web element.
    :param threshold: Similarity threshold for button text.
    :param sort_similarity_desc: Whether to sort by similarity.
    :return: List of confirmation button elements.
    """
    confirmation_buttons = []
    confirmation_probs = []
    for btn in find_available_elements_gtr(By.CSS_SELECTOR, "button, [role='button']", parent):
        btn_text = btn.text
        btn_confirmation_prob = is_confirmation_text(btn_text, threshold)
        if btn_confirmation_prob is None:
            logger.debug(f'Button <{btn_text}> was classified as not a confirmation button.')
            continue

        logger.debug(f'Found confirmation button <{btn.text}> with probability <{btn_confirmation_prob}>.')
        confirmation_buttons.append(btn)
        confirmation_probs.append(btn_confirmation_prob)

    if sort_similarity_desc:
        return [el for _, el in sorted(zip(confirmation_probs, confirmation_buttons), key=itemgetter(0), reverse=True)]

    return confirmation_buttons

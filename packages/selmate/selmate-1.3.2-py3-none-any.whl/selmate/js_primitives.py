from typing import List

from selenium.webdriver.remote.webelement import WebElement

from selmate.safe_exceptions import safe_stale, safe_not_found


def activate_mouse_path_drawing(driver):
    """Adds a canvas to the page to draw mouse movement paths.
    :param driver: The Selenium WebDriver instance.
    """
    driver.execute_script("""
            const canvas = document.createElement('canvas');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            canvas.style.position = 'fixed';
            canvas.style.top = '0';
            canvas.style.left = '0';
            canvas.style.pointerEvents = 'none';
            document.body.appendChild(canvas);
            const ctx = canvas.getContext('2d');
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            let lastX, lastY;

            document.addEventListener('mousemove', (e) => {
                if (lastX && lastY) {
                    ctx.beginPath();
                    ctx.moveTo(lastX, lastY);
                    ctx.lineTo(e.clientX, e.clientY);
                    ctx.stroke();
                }
                lastX = e.clientX;
                lastY = e.clientY;
            });
            """)


def js_choose_elements_above_z_index(min_z_index, driver, query_selector='*') -> List[WebElement]:
    """Finds elements with a z-index above a minimum value.
    :param min_z_index: Minimum z-index value.
    :param driver: The Selenium WebDriver instance.
    :param query_selector: CSS selector for elements.
    :return: List of elements with z-index above the minimum.
    """
    return driver.execute_script(f"""
        let elements = document.querySelectorAll('{query_selector}');
        let result = [];
        for (let el of elements) {{
            let zIndex = window.getComputedStyle(el).zIndex;
            if (zIndex !== 'auto' && parseInt(zIndex) >= {min_z_index}) {{
                result.push(el);
            }}
        }}
        return result;
    """)


def js_find_elements(query_selector, driver):
    """Finds elements matching a CSS selector.
    :param query_selector: CSS selector for elements.
    :param driver: The Selenium WebDriver instance.
    :return: List of matching web elements.
    """
    return driver.execute_script(f"return document.querySelectorAll('{query_selector}');")


def js_smooth_scroll(to_x, to_y, driver):
    """Performs a smooth scroll to specified coordinates.
    :param to_x: Target x-coordinate.
    :param to_y: Target y-coordinate.
    :param driver: The Selenium WebDriver instance.
    """
    driver.execute_script(f"window.scrollTo({to_x}, {to_y}, {{behaviour: 'smooth'}});")


@safe_stale(def_val=False)
def js_click(element: WebElement, driver) -> bool:
    """Performs a JavaScript click on an element.
    :param element: The web element to click.
    :param driver: The Selenium WebDriver instance.
    :return: True if the click was successful.
    """
    driver.execute_script('arguments[0].click();', element)
    return True


@safe_not_found(def_val=False)
@safe_stale(def_val=False)
def js_is_full_in_viewport(element: WebElement, driver):
    """Checks if an element is fully in the viewport.
    :param element: The web element to check.
    :param driver: The Selenium WebDriver instance.
    :return: True if the element is fully visible.
    """
    return driver.execute_script(
        """
        var elem = arguments[0], box = elem.getBoundingClientRect();
        return (
            box.top >= 0 &&
            box.left >= 0 &&
            box.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            box.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
        """,
        element
    )


@safe_not_found(def_val=False)
@safe_stale(def_val=False)
def js_is_partially_in_viewport(element: WebElement, driver):
    """Checks if an element is partially in the viewport.
    :param element: The web element to check.
    :param driver: The Selenium WebDriver instance.
    :return: True if the element is partially visible.
    """
    return driver.execute_script(
        """
        var elem = arguments[0], box = elem.getBoundingClientRect();
        var windowHeight = window.innerHeight || document.documentElement.clientHeight;
        var windowWidth = window.innerWidth || document.documentElement.clientWidth;
        return (
            box.bottom >= 0 && 
            box.top <= windowHeight &&
            box.right >= 0 &&
            box.left <= windowWidth
        );
        """,
        element
    )


@safe_stale(def_val=False)
def js_need_scroll_to_element(element: WebElement, driver):
    """Checks if scrolling is needed to bring an element into view.
    :param element: The web element to check.
    :param driver: The Selenium WebDriver instance.
    :return: True if scrolling is needed.
    """
    return driver.execute_script(
        """
        var elem = arguments[0], box = elem.getBoundingClientRect();
        return box.top < 0 || box.bottom > (window.innerHeight || document.documentElement.clientHeight);
        """,
        element
    )


@safe_stale(def_val=False)
def js_scroll_to_element(element: WebElement, driver):
    """Scrolls to an element using JavaScript.
    :param element: The web element to scroll to.
    :param driver: The Selenium WebDriver instance.
    :return: True if the scroll was successful.
    """
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    return True


@safe_stale(def_val=False)
def js_remove_element(element: WebElement, driver):
    """Removes an element from the DOM using JavaScript.
    :param element: The web element to remove.
    :param driver: The Selenium WebDriver instance.
    :return: True if the removal was successful.
    """
    driver.execute_script("arguments[0].remove();", element)
    return True
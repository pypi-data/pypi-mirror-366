from functools import wraps

from selenium.common import StaleElementReferenceException, TimeoutException, MoveTargetOutOfBoundsException, \
    ElementClickInterceptedException, NoSuchElementException, ElementNotInteractableException


def make_exception_safe_decorator(exception, default_value=None):
    """Creates a decorator to handle specific Selenium exceptions.
    :param exception: The exception type to catch.
    :param default_value: The value to return on exception.
    :return: A decorator function.
    """
    def safe_decorator(def_val=default_value):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exception:
                    return def_val

            return wrapper

        return decorator

    return safe_decorator


safe_stale = make_exception_safe_decorator(StaleElementReferenceException, None)
safe_timeout = make_exception_safe_decorator(TimeoutException, None)
safe_out_of_bound = make_exception_safe_decorator(MoveTargetOutOfBoundsException, None)
safe_click_interception = make_exception_safe_decorator(ElementClickInterceptedException, None)
safe_not_interactable = make_exception_safe_decorator(ElementNotInteractableException, None)
safe_not_found = make_exception_safe_decorator(NoSuchElementException, None)
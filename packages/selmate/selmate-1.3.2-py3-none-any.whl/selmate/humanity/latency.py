import time

from selmate.humanity.constants import HUMAN_CLICK_LATENCY, HUMAN_MOUSE_MOVE_LATENCY, HUMAN_FOCUS_ELEMENT_LATENCY, \
    HUMAN_OBSERVE_VIEW_LATENCY, HUMAN_OBSERVE_PAGE_LATENCY, HUMAN_SCROLL_LATENCY, HUMAN_KEY_TYPE_LATENCY
from selmate.utils import latency_time


def human_key_type_latency():
    """ Introduces a delay simulating human key type latency.
    """
    time.sleep(latency_time(*HUMAN_KEY_TYPE_LATENCY))


def human_click_latency():
    """Introduces a delay simulating human click latency.
    """
    time.sleep(latency_time(*HUMAN_CLICK_LATENCY))


def human_mouse_move_latency():
    """Introduces a delay simulating human mouse movement latency.
    """
    time.sleep(latency_time(*HUMAN_MOUSE_MOVE_LATENCY))


def human_focus_element_latency():
    """Introduces a delay simulating human element focus latency.
    """
    time.sleep(latency_time(*HUMAN_FOCUS_ELEMENT_LATENCY))


def human_observe_view_latency():
    """Introduces a delay simulating human view observation latency.
    """
    time.sleep(latency_time(*HUMAN_OBSERVE_VIEW_LATENCY))


def human_observe_page_latency():
    """Introduces a delay simulating human page observation latency.
    """
    time.sleep(latency_time(*HUMAN_OBSERVE_PAGE_LATENCY))


def human_scroll_latency():
    """Introduces a delay simulating human scroll latency.
    """
    time.sleep(latency_time(*HUMAN_SCROLL_LATENCY))

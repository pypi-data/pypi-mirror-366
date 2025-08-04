import math
import random
import re
from typing import Tuple, List, Optional
from urllib.parse import urlparse, urlunparse, urljoin

from rapidfuzz import fuzz

from selmate.constants import WHITESPACE_PATTERN, CONFIRMATIONS


def normalize_url(href, base_url, save_query=True, save_fragment=False, save_params=False):
    """Normalizes a URL relative to a base URL.
    :param href: The URL to normalize.
    :param base_url: The base URL for relative URLs.
    :param save_query: Whether to keep the query string.
    :param save_fragment: Whether to keep the fragment.
    :param save_params: Whether to keep URL parameters.
    :return: The normalized URL or None if invalid.
    """
    href = href.strip()
    if not href:
        return None

    parsed_base = urlparse(base_url)
    if not parsed_base.scheme:
        base_url = 'https://' + base_url.lstrip('/')
        parsed_base = urlparse(base_url)

    parsed_href = urlparse(href)
    if parsed_href.scheme:
        absolute_url = href
    else:
        if href.startswith('//'):
            href = parsed_base.scheme + ':' + href
        absolute_url = urljoin(base_url, href)

    parsed_url = urlparse(absolute_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return None

    cleaned_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params if save_params else '',
        parsed_url.query if save_query else '',
        parsed_url.fragment if save_fragment else ''
    ))

    return cleaned_url


def is_webpage(url):
    """Checks if a URL points to a webpage.
    :param url: The URL to check.
    :return: True if the URL is a webpage, False otherwise.
    """
    webpage_extensions = (
        '.html', '.htm', '.php', '.asp', '.aspx', '.jsp', '.jspx',
        '.shtml', '.cfm', '.pl', '.py', '.erb', '.rhtml', '.do',
        '.action', '.cshtml', '.vbhtml', '.phtml', '.cfc', '.ghtml'
    )

    parsed_url = urlparse(url)
    path = parsed_url.path.lower()

    if not path or path.endswith('/'):
        return True

    if path.endswith(webpage_extensions):
        return True

    last_segment = path.split('/')[-1]
    if '.' in last_segment:
        return False

    return True


def is_confirmation_text(text, threshold=0.75) -> Optional[float]:
    """Determines if text resembles a confirmation action.
    :param text: The text to check.
    :param threshold: Similarity threshold for confirmation.
    :return: Similarity score if above threshold, None otherwise.
    """
    max_sim = None
    for confirmation in CONFIRMATIONS:
        sim = fuzz.ratio(confirmation, text, processor=norm_string) / 100
        if sim < threshold:
            continue

        if max_sim is None or sim > max_sim:
            max_sim = sim

    return max_sim


def latency_time(min_time, max_time):
    """Generates a random latency time within a range.
    :param min_time: Minimum latency time.
    :param max_time: Maximum latency time.
    :return: Random latency time.
    """
    return random.uniform(min_time, max_time)


def norm_string(s):
    """Normalizes a string by stripping and lowercasing.
    :param s: The string to normalize.
    :return: Normalized string.
    """
    s = s.strip().lower()
    return re.sub(WHITESPACE_PATTERN, ' ', s)


def generate_parabolic_path(x1, y1, x2, y2, step_length=10.0) -> List[Tuple[float, float]]:
    """Generates a parabolic path between two points.
    :param x1: Starting x-coordinate.
    :param y1: Starting y-coordinate.
    :param x2: Ending x-coordinate.
    :param y2: Ending y-coordinate.
    :param step_length: Length of each step.
    :return: List of (x, y) coordinates.
    """
    dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) * math.pi / 1.5
    steps = math.ceil(dist / step_length)
    path = []
    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y_offset = steps * 4 * t * (1 - t)
        y = y1 + (y2 - y1) * t + y_offset
        path.append((x, y))
    return path


def generate_curved_path(x1, y1, x2, y2, step_length=10.0):
    """Generates a curved path between two points.
    :param x1: Starting x-coordinate.
    :param y1: Starting y-coordinate.
    :param x2: Ending x-coordinate.
    :param y2: Ending y-coordinate.
    :param step_length: Length of each step.
    :return: List of (x, y) coordinates.
    """
    points = [(x1, y1)]

    dx = x2 - x1
    total_dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    num_steps = max(1, int(total_dist / step_length))
    height = abs(y2 - y1) * 0.5 + 0.5

    for i in range(1, num_steps):
        t = i / num_steps
        x = x1 + t * dx
        arc = height * (1 - ((2 * t - 1) ** 2))
        y = y1 + t * (y2 - y1) + arc

        points.append((x, y))

    points.append((x2, y2))

    return points

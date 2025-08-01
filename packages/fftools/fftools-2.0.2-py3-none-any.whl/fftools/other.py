import random
import string
from collections.abc import Generator
from time import sleep
from typing import Any

from loguru import logger as log
from whenever import Instant


# current date for TZ=Europe/Zurich
CURRENT_DATE = Instant.now().to_tz("Europe/Zurich")
# timestamp (str) in format: YYYY-MM-DD
TIMESTAMP_YMD = f"{str(CURRENT_DATE.year).zfill(4)}-{str(CURRENT_DATE.month).zfill(2)}-{str(CURRENT_DATE.day).zfill(2)}"
# timestamp (str) in format: hh-mm-ss
TIMESTAMP_HMS = f"{str(CURRENT_DATE.hour).zfill(2)}-{str(CURRENT_DATE.minute).zfill(2)}-{str(CURRENT_DATE.second).zfill(2)}"
# timestamp (str) in format: YYYY-MM-DD_hh-mm-ss
TIMESTAMP_FULL = f"{TIMESTAMP_YMD}T{TIMESTAMP_HMS}"


def progress_bar(progress: float, total: float) -> None:
    """prints a progress bar.

    Args:
        progress: current progress to total. x/total.
        total: the total.
    """
    percent = int(progress / (int(total) / 100))
    bar_length = 50
    bar_progress = int(progress / (int(total) / bar_length))
    bar_texture = "■" * bar_progress
    whitespace_texture = " " * (bar_length - bar_progress)
    if progress == total:
        full_bar = "■" * bar_length
        log.info(f"\r[ PROGRESS ] ❙{full_bar}❙ 100%", end="\n")
    else:
        log.info(
            f"\r[ PROGRESS ] ❙{bar_texture}{whitespace_texture}❙ {percent}%",
            end="\r",
        )


def pop_dict(input_dict: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """remove keys (and value for key) from `dict`.

    does not modify the input dict. does nothing if the keys don't exist in the dict.

    Args:
        input_dict: dict to remove keys from.
        keys: list of keys to remove.

    Returns:
        the new dict without the specified keys.
    """
    log.debug(f"cleaning dict keys={keys}")
    output_dict = input_dict.copy()
    for key in keys:
        output_dict.pop(key, None)

    return output_dict


def chunks(input_list: list[Any], output_length: int) -> Generator[list[Any], None, None]:
    """get chunks of list -> list of lists.

    Args:
        input_list: the list to split into chunks
        output_length: length of the chunks

    Yields:
        the chunked list of lists
    """
    for i in range(0, len(input_list), output_length):
        yield input_list[i : i + output_length]


def get_random_letters(count: int) -> str:
    """get a string of random letters.

    Args:
        count: count of random characters in the returned string.

    Raises:
        ValueError: if count is smaller than 1.

    Returns:
        the string of random letters.
    """
    if count <= 1:
        log.error(f"'{count}' is not a valid integer")
        raise ValueError

    random_letters = random.choices(string.ascii_letters, k=count)  # noqa
    return "".join(random_letters)


def wait_random(max_seconds: int) -> None:
    """wait random amount of seconds.

    Args:
        max_seconds: max seconds to wait
    """
    if max_seconds <= 1:
        log.info("skipping wait")
        return

    wait_time = random.randrange(1, max_seconds + 1)  # noqa: S311
    log.info(f"waiting {wait_time} seconds")
    sleep(wait_time)


def fix_punycode(zone_name: str) -> str:
    """fix punycode characters in domain name.

    Args:
        zone_name: domain/zone name

    Returns:
        fixed domain/zone name
    """
    return zone_name.encode("idna").decode("utf8")

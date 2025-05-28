from typing import Optional

from .table import table_data


def lookup(c: str) -> Optional[str]:
    """
    Look up a Hanja character and return its 훈음 (Hun-eum) information.

    Args:
        c (str): A single Hanja character to look up.

    Returns:
        Optional[str]: The 훈음 (Hun-eum) information as a string if found,
                      typically in the format "훈 음" (meaning pronunciation).
                      Returns None if the character is not found.

    Examples:
        >>> lookup("雪")
        '눈 설'
        >>> lookup("山")
        '메 산'
        >>> lookup("xyz")
        None
    """
    return table_data.get(c, None)


def is_hanja(c: str) -> bool:
    """
    Check if a character is a Hanja (Chinese character used in Korean).

    Args:
        c (str): A single character to check.

    Returns:
        bool: True if the character is a Hanja in the dictionary, False otherwise.

    Examples:
        >>> is_hanja("雪")
        True
        >>> is_hanja("한")
        False
        >>> is_hanja("xyz")
        False
    """
    return c in table_data


def pronunciation(c: str) -> Optional[str]:
    """
    Extract the Sino-Korean pronunciation (음/音) part from the 훈음 information.

    This function handles various formats in the dictionary:
    - Normal format: "눈 설" -> returns "설"
    - Comma-separated: "샘솟을 집, 샘솟을 설" -> returns "집"
    - Slash-separated: "제비 연/잔치 연" -> returns "연"
    - Parentheses: "영양 령(영)" -> returns "령"

    Args:
        c (str): A single Hanja character.

    Returns:
        Optional[str]: The Sino-Korean pronunciation (음/音) if found, None otherwise.

    Examples:
        >>> pronunciation("雪")  # 눈 설
        '설'
        >>> pronunciation("燕")  # 제비 연/잔치 연
        '연'
        >>> pronunciation("xyz")
        None
    """
    hun_eum = lookup(c)
    if hun_eum is None:
        return None

    # First check for entries with commas: "샘솟을 집, 샘솟을 설" -> "집"
    if "," in hun_eum:
        hun_eum = hun_eum.split(",")[0].strip()

    # For entries with slash: "제비 연/잔치 연" -> "연"
    if "/" in hun_eum:
        hun_eum = hun_eum.split("/")[0].strip()

    # For entries with parentheses: "영양 령(영)" -> "령"
    if "(" in hun_eum:
        hun_eum = hun_eum.split("(")[0].strip()

    return hun_eum[-1] if hun_eum else None

"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Various utilities relating to the Mosel language.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""
import re

from .mosel_keywords import MOSEL_KEYWORDS

VALID_IDENT_REGEX_STR = "[_a-zA-Z][_a-zA-Z0-9]*"
VALID_IDENT_REGEX = re.compile(VALID_IDENT_REGEX_STR)
VALID_IDENT_MAX_LENGTH = 1000

VALID_ANNOTATION_STR_REGEX_STR = "[\n\r\0]"
VALID_ANNOTATION_STR_REGEX = re.compile(VALID_ANNOTATION_STR_REGEX_STR)
VALID_ANNOTATION_STR_MAX_LENGTH = 5000


def is_valid_identifier(ident: str, max_length: int = VALID_IDENT_MAX_LENGTH) -> bool:
    """ Checks if a string is a valid identifier for an Xpress Insight entity. """

    if len(ident) > max_length:
        raise ValueError(f"The identifier {repr(ident)} must not be longer than {max_length} characters.")

    return VALID_IDENT_REGEX.fullmatch(ident) is not None


def validate_ident(ident: str, ident_for: str = None, ident_name: str = "identifier") -> str:
    """ Check that given string would be a valid identifier in a Mosel model. """
    if not is_valid_identifier(ident):
        if ident_for is None:
            err_msg = "Invalid {0} {1}. Identifier must satisfy regex {3}."
        else:
            err_msg = "Invalid {0} {1} for {2}. Identifier must satisfy regex {3}."
        raise ValueError(err_msg.format(ident_name, repr(ident), ident_for, repr(VALID_IDENT_REGEX_STR)))

    if ident in MOSEL_KEYWORDS:
        if ident_for is None:
            err_msg = "Invalid {0} {1}. Identifier must not be a reserved keyword."
        else:
            err_msg = "Invalid {0} {1} for {2}. Identifier must not be a reserved keyword."
        raise ValueError(err_msg.format(ident_name, repr(ident), ident_for))

    return ident


def validate_raw_ident(ident: str, ident_name: str = "identifier") -> str:
    """ Check whether a string is a valid identifier in an annotation. """
    if not is_valid_identifier(ident):
        raise ValueError(f'{repr(ident)} is not a valid {ident_name}. '
                         f'Identifier must satisfy regex {VALID_IDENT_REGEX_STR}.')
    return ident


def validate_annotation_str(annot_str: str,
                            str_name: str = 'annotation string',
                            max_length: int = VALID_ANNOTATION_STR_MAX_LENGTH) -> str:
    """ Check whether annotation string contains unsupported characters or is too long. """
    if "!)" in annot_str:
        raise ValueError(f'The {str_name} must not contain the substring "!)": {repr(annot_str)}.')
    if len(annot_str) > max_length:
        raise ValueError(f'The {str_name} must not be longer than {max_length} characters: {repr(annot_str)}.')
    if VALID_ANNOTATION_STR_REGEX.search(annot_str) is not None:
        raise ValueError(f'The {str_name} {repr(annot_str)} contains unsupported characters. '
                         f'It must not match the regular expression {repr(VALID_ANNOTATION_STR_REGEX_STR)}')
    return annot_str

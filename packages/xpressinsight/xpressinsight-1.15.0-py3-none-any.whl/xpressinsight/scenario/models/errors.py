"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines error-related structures returned by the Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional, List, ForwardRef

from .config import InsightApiBaseModel



#
ESCAPED_MESSAGE_CHARS = {
    '\'': '\'',
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    't': '\t',
    'n': '\n',
    'r': '\r',
    'f': '\f'
}


def unescape_error_message(msg: str) -> str:
    """
    FICO REST API specifications require the 'message' fields' escape JavaScript special characters
    (Insight uses StringEscapeUtils.escapeJavaScript from commons-lang to do this), so we need to reverse
    this escaping when using the message field from Python.

    Yes, this means the message is essentially double-escaped (once from escapeJavaScript then again when it's
    encoded in JSON).
    """
    result = ''
    i = 0
    msglen = len(msg)
    while i < msglen:
        c = msg[i]
        if c == '\\' and i < msglen-1:
            #
            esc = msg[i+1]
            if esc in ESCAPED_MESSAGE_CHARS:
                result += ESCAPED_MESSAGE_CHARS[esc]
                i += 2
            else:
                #
                result += f"\\{esc}"
                i += 2

        else:
            #
            result += c
            i += 1

    return result


class ErrorDetail(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Attachments.html?scroll=_components_schemas_ErrorDetail """
    code: Optional[str] = None
    desc: Optional[str] = None
    message: Optional[str] = None
    target: Optional[str] = None
    timestamp: Optional[str] = None


class InnerError(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Attachments.html?scroll=_components_schemas_InnerError """
    code: Optional[str] = None
    desc: Optional[str] = None
    inner_error: Optional[ForwardRef('InnerError')] = None
    message: Optional[str] = None

    def get_error_description(self) -> Optional[str]:
        """ Return an appropriate error description from an InnerError object. """
        #
        #
        #

        #
        if self.message:
            return unescape_error_message(self.message)

        #
        #
        if self.desc:
            return self.desc

        return None


class OuterError(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Attachments.html?scroll=_components_schemas_OuterError """
    code: Optional[str] = None
    desc: Optional[str] = None
    details: Optional[List[ErrorDetail]] = None
    inner_error: Optional[InnerError] = None
    message: Optional[str] = None
    parent_id: Optional[str] = None
    spanId: Optional[str] = None
    timestamp: Optional[str] = None
    traceId: Optional[str] = None

    def get_error_description(self) -> str:
        """ Return an appropriate error description from an OuterError object. """
        #
        #
        #
        if self.inner_error:
            inner_error_description = self.inner_error.get_error_description()
            if inner_error_description:
                return inner_error_description

        #
        #
        if self.message:
            #
            return unescape_error_message(self.message)

        #
        if self.desc:
            return self.desc

        #
        #
        return self.model_dump_json()


class ErrorResponse(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Folders.html?scroll=_components_schemas_ErrorResponse """
    error: OuterError

    def get_error_description(self) -> Optional[str]:
        """ Return an appropriate error description from an ErrorResponse object. """
        if not self.error:
            return None

        return self.error.get_error_description()

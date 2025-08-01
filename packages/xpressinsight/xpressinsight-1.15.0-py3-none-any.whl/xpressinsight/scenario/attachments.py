"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly. Because app and scenario attachment operations follow the
    same design pattern, we can define a common set of private functions
    that can be used for both.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
# pylint: disable=protected-access,too-many-instance-attributes,too-many-arguments,too-few-public-methods
from abc import ABC
import codecs
from dataclasses import dataclass
from datetime import datetime
from io import BufferedIOBase, RawIOBase, TextIOBase
import os
from tempfile import TemporaryDirectory
from typing import List, Sequence, Union, Optional, BinaryIO, TextIO
import sys

from requests_toolbelt import MultipartEncoder

from .common import parse_insight_datetime, Reference
from .errors import make_insight_server_error
from .rest_client_base import InsightRestClientBase, INSIGHT_JSON_CONTENT_TYPE, INSIGHT_BINARY_CONTENT_TYPE
from . import models

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


@dataclass
class Attachment:
    """
    Information about a single scenario or app attachment.

    Attributes
    ----------
    app : Reference
        A Reference to the app to which the attachment belongs.
    description : str
        A description of the attachment.
    filename : str
        Filename of the attachment, e.g. `my-attachment.txt`
    hidden : bool
        Whether the attachment is hidden. This indicates the attachment is not for general user interaction.
    id : str
        The ID of this attachment.
    last_modified : datetime
        When the attachment contents were last modified.
    last_modified_by : Reference
        The user who last modified this attachment.
    name : str
        Name of the attachment.
    parent : Reference
        The parent of this attachment (either an app or a scenario). If the attachment is an app attachment,
        then the parent property will have the same value as the app property.
    size : int
        The size of this attachment in bytes.
    tags : List[str]
        The tags that are present on this attachment.
    """
    id: str
    app: Reference
    description: str
    filename: str
    hidden: bool
    last_modified: datetime
    last_modified_by: Reference
    name: str
    parent: Reference
    size: int
    tags: List[str]

    @classmethod
    def _from_rest_api_model(cls, src: models.Attachment) -> Self:
        # noinspection PyProtectedMember
        return Attachment(
            id=src.id,
            app=Reference._from_rest_api_model(src.app),
            description=src.description,
            filename=src.filename,
            hidden=src.hidden,
            last_modified=parse_insight_datetime(src.last_modified),
            last_modified_by=Reference._from_rest_api_model(src.last_modified_by),
            name=src.name,
            parent=Reference._from_rest_api_model(src.parent),
            size=src.size,
            tags=src.tags
        )


@dataclass
class AttachmentUpdate:
    """
    Information about an update to apply to the metadata of a scenario or app attachment.

    Attributes
    ----------
    description : str, optional
        A description of the attachment.
    filename : str, optional
        Filename of the attachment, e.g. `my-attachment.txt`.
    hidden : bool, optional
        Whether the attachment is hidden. This indicates the attachment is not for general user interaction.
    tags : List[str], optional
        The tags that are present on this attachment.
    """
    description: Optional[str] = None
    filename: Optional[str] = None
    hidden: Optional[bool] = None
    tags: Optional[List[str]] = None


@dataclass
class AttachmentTag:
    """
    Information about a single attachment tag.

    Attributes
    ----------
    name : str
        The unique name for the tag.
    description : str
        A human-readable description for this tag.
    mandatory : bool
        Whether this tag must be present on at least one attachment belonging to the app or scenario.
    multi_file : bool
        Whether this tag can be present on multiple attachments.
    """
    name: str
    description: str
    mandatory: bool
    multi_file: bool

    @classmethod
    def _from_rest_api_model(cls, src: models.AttachmentTag) -> Self:
        # noinspection PyProtectedMember
        return AttachmentTag(
            name=src.name,
            description=src.description,
            mandatory=src.mandatory,
            multi_file=src.multi_file
        )


class InsightAttachOperations(InsightRestClientBase, ABC):
    """
    Implementation of private calls to attachment-related endpoints in the Insight REST API.  Each takes
    as the first parameter the base path of the attachments endpoint, something like `['api', 'scenarios',
    scenario_id, 'attachments']`.
    """

    def _get_attachment_info(self, attachments_endpoint: List[str], attachment_id: str) -> Attachment:
        return Attachment._from_rest_api_model(
            self._make_json_request(
                path=attachments_endpoint + [attachment_id],
                method='GET',
                response_type=models.Attachment
            )
        )

    def _get_all_attachment_info(self, attachments_endpoint: List[str]) -> List[Attachment]:
        all_models = self._make_paged_json_request(
            path=attachments_endpoint,
            method='GET',
            item_type=models.Attachment
        )
        return [Attachment._from_rest_api_model(m) for m in all_models]

    def _get_attachment(self, attachments_endpoint: List[str], attachment_id: str,
                        destination: Union[str, TextIO, BinaryIO],
                        encoding: Optional[str] = 'utf-8') -> None:
        """
        Read given attachment data to given destination.
        Destination may be a filename, TextIO or BinaryIO object.
        """
        #
        if isinstance(destination, str):
            with open(destination, "wb") as f:
                self._get_attachment(attachments_endpoint, attachment_id, f)
                return

        request_url = self._get_request_url(attachments_endpoint + [attachment_id, 'file'])
        with self._slow_tasks_monitor.task(f'InsightRestClient HTTP GET {request_url}'):
            #
            response = self._session.request(
                method='GET',
                url=request_url,
                headers={
                    'Accept': f'{INSIGHT_BINARY_CONTENT_TYPE},{INSIGHT_JSON_CONTENT_TYPE}'
                },
                stream=True
            )

            #
            if response.status_code != 200:
                raise make_insight_server_error(response)

            #
            if isinstance(destination, (RawIOBase, BufferedIOBase)):
                for chunk in response.iter_content(chunk_size=16*1024):
                    destination.write(chunk)

            #
            elif isinstance(destination, TextIOBase):
                decoder = codecs.lookup(encoding).incrementaldecoder()
                for chunk in response.iter_content(chunk_size=16*1024):
                    destination.write(decoder.decode(chunk))
                destination.write(decoder.decode(b'', final=True))

            else:
                raise TypeError(f'Unsupported destination type "{type(destination)}"')

    def _put_attachment(self, attachments_endpoint: List[str], attachment_name: str,
                        source: Union[str, TextIO, BinaryIO],
                        tag_name: Optional[str] = None,
                        overwrite: bool = False,
                        encoding: Optional[str] = 'utf-8') -> Attachment:
        """
        Upload new or update existing attachment with given name.
        Source can be either filename, TextIO or BinaryIO.
        """
        #
        if isinstance(source, str):
            with open(source, "rb") as f:
                return self._put_attachment(attachments_endpoint, attachment_name, f,
                                            tag_name=tag_name,
                                            overwrite=overwrite,
                                            encoding=encoding)

        #
        #
        #
        if isinstance(source, TextIOBase):
            with TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, 'attach.dat')
                with open(temp_file, 'w', encoding=encoding) as f:
                    while True:
                        chunk = source.read(16*1024)
                        if chunk == '':
                            break
                        f.write(chunk)
                return self._put_attachment(attachments_endpoint, attachment_name, temp_file,
                                            tag_name=tag_name,
                                            overwrite=overwrite,
                                            encoding=encoding)

        #
        request_body_fields = {
            'attachment': (attachment_name, source, INSIGHT_BINARY_CONTENT_TYPE),
            'overwrite': 'true' if overwrite else 'false',
            'hidden': 'false'
        }
        if tag_name is not None:
            request_body_fields['tagName'] = tag_name

        #
        request_body_fields = sorted(request_body_fields.items())

        #
        response_body = self._make_json_request(
            method='POST',
            path=attachments_endpoint,
            request_body=MultipartEncoder(request_body_fields),
            response_type=models.Attachment,
            expected_status_code=200
        )

        return Attachment._from_rest_api_model(response_body)

    def _set_attachment_info(self, attachments_endpoint: List[str], attachment_id: str,
                             updated_info: Union[Attachment, AttachmentUpdate]) -> None:
        """ Update the attachment info - only 'filename', 'description', 'tags' and 'hidden' fields can be updated. """
        update_model = models.AttachmentUpdateRequest()
        for field in ('filename', 'description', 'tags', 'hidden'):
            if updated_info.__dict__[field] is not None:
                update_model.__dict__[field] = updated_info.__dict__[field]
        self._make_json_request(
            path=attachments_endpoint + [attachment_id],
            method='PATCH',
            request_body=update_model,
            response_type=None
        )

    def _delete_attachment(self, attachments_endpoint: List[str], attachment_id: str) -> None:
        """ Delete the given attachment """
        self._make_json_request(
            path=attachments_endpoint + [attachment_id],
            method='DELETE',
            response_type=None,
            expected_status_code=204
        )

    def get_attachment_tags(self, app_id) -> Sequence[AttachmentTag]:
        """
        Get information about all the tags defined for the given app.

        Parameters
        ----------
        app_id : str
            The ID of the app to query.

        Returns
        -------
        tags : Sequence[AttachmentTag]
            Information about the available tags.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no app with this ID, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     APP_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     for tag in client.get_attach_tags(APP_ID):
        ...         print(f'Found tag {tag.name}')
        """
        tags = self._make_paged_json_request(
            method='GET',
            path=['api', 'apps', app_id, 'attachments', 'tags'],
            item_type=models.AttachmentTag
        )

        # noinspection PyProtectedMember
        return [AttachmentTag._from_rest_api_model(tag) for tag in tags]

"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly. This defines functions and classes for accessing Insight
    app information through the REST interface.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
# pylint: disable=protected-access
from abc import ABC
from dataclasses import dataclass
import sys
import time
from datetime import datetime
from typing import Sequence, Optional, Union, TextIO, BinaryIO

from requests_toolbelt import MultipartEncoder

from .attachments import InsightAttachOperations, Attachment, AttachmentUpdate
from .common import parse_insight_datetime
from .errors import  InsightServerError, InsightServerResponseError
from .rest_client_base import INSIGHT_BINARY_CONTENT_TYPE, INSIGHT_JSON_CONTENT_TYPE
from . import models

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


@dataclass
class App:
    """
    Information about a single app.

    Attributes
    ----------
    id : str
        The ID of the app.
    name : str
        The name of the app.
    path : str
        The path to the app.
    app_version : str
        The version of the model within the app.
    data_version : int
        The model data version.
    """
    id: str
    name: str
    path: str
    app_version: str
    data_version: int

    @classmethod
    def _from_rest_api_model(cls, src: models.App) -> Self:
        return App(
            id=src.id,
            name=src.name,
            path=src.path,
            app_version=src.model.version,
            data_version=src.model.data_version
        )


@dataclass
class AppMember:
    """
    Information about a user who has access to an app.

    Attributes
    ----------
    id : str
        The ID of the user.
    name : str
        The name of the app member.
    first_name : str
        The first name of the app member.
    last_name : str
        The last name of the app member.
    """
    id: str
    name: str
    first_name: str
    last_name: str

    @classmethod
    def _from_rest_api_model(cls, src: models.AppMember) -> Self:
        return AppMember(
            id=src.id,
            name=src.name,
            first_name=src.first_name,
            last_name=src.last_name
        )


@dataclass
class AppCreationResponse:
    """
    Information about an app creation.

    Attributes
    ----------
    app : App
        Information about the app that was created.
    messages : Sequence[str]
        Informational messages about the app creation which can be displayed to a user,
        e.g. `["An execution service referred to by this app does not exist"]`.
    """
    app: App
    messages: Sequence[str]

    @classmethod
    def _from_rest_api_model(cls, src: models.AppCreationResponse) -> Self:
        return AppCreationResponse(
            app=App._from_rest_api_model(src.app),
            messages=src.messages
        )


@dataclass
class AppUpgradeResponse:
    """
    Information about an app upgrade.

    Attributes
    ----------
    start_time : datetime
        The time the upgrade started.
    finish_time : datetime
        The time the upgrade finished.
    messages : Sequence[str]
        Informational messages about the app creation which can be displayed to a user,
        e.g. `["An execution service referred to by this app does not exist"]`.
    """
    start_time: datetime
    finish_time: datetime
    messages: Sequence[str]

    @classmethod
    def _from_rest_api_model(cls, src: models.Upgrade) -> Self:
        return AppUpgradeResponse(
            start_time=parse_insight_datetime(src.started),
            finish_time=parse_insight_datetime(src.finished),
            messages=(src.error_messages or []) + (src.info_messages or [])
        )


class InsightAppOperations(InsightAttachOperations, ABC):
    """
    Implementation of calls to app-related endpoints in the Insight REST API.
    """

    def get_app(self, app_id: str) -> App:
        """
        Get the app record for the app with the given ID.

        Parameters
        ----------
        app_id : str
            The ID of the app to query.

        Returns
        -------
        app : App
            Information about the app with the requested ID.

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
        ...     app = client.get_app('570b9100-46e3-4643-baee-2e24aa538f25')
        ...     print(f'Found app {app.name} with path {app.path}')
        """
        app = self._make_json_request(
            method='GET',
            path=['api', 'apps', app_id],
            response_type=models.App
        )

        # noinspection PyProtectedMember
        return App._from_rest_api_model(app)

    def get_all_apps(self) -> Sequence[App]:
        """
        Get the app records for all apps that the REST API client credentials have permission to access.

        Returns
        -------
        apps : Sequence[App]
            Information about all the apps the REST API credentials have permission to access.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     for app in client.get_apps():
        ...         print(f'Found app {app.name} with path {app.path}')
        """
        apps = self._make_paged_json_request(
            method='GET',
            path=['api', 'apps'],
            item_type=models.App
        )

        # noinspection PyProtectedMember
        return [App._from_rest_api_model(app) for app in apps]

    def get_app_members(self, app_id: str) -> Sequence[AppMember]:
        """
        Get information about the users who can access the given app.

        Parameters
        ----------
        app_id : str
            The ID of the app to query.

        Returns
        -------
        members : Sequence[AppMember]
            Both direct app members and users who have authority to access all apps.

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
        ...     for member in client.get_app_members(APP_ID):
        ...         print(f'Found app member {member.name}')
        """
        members = self._make_paged_json_request(
            method='GET',
            path=['api', 'apps', app_id, 'members'],
            item_type=models.AppMember
        )

        # noinspection PyProtectedMember
        return [AppMember._from_rest_api_model(member) for member in members]

    def get_app_attachment_info(self, app_id: str, attachment_id: str) -> Attachment:
        """
        Get information about a given app attachment.

        Parameters
        ----------
        app_id : str
            The ID of the app to query on which the attachment resides.
        attachment_id : str
            The ID of the attachment.

        Returns
        -------
        attachment : Attachment
            Information about the app attachment with the requested ID.

        Raises
        ------
        scenario.ItemNotFoundError
            If the app or attachment cannot be found, or the REST API client credentials do not have permission
            to access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     info = client.get_app_attachment_info(
        ...         app_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4')
        ...     print(f'Attachment name is {info.name}')
        """
        return self._get_attachment_info(['api', 'apps', app_id, 'attachments'], attachment_id)

    def get_all_app_attachment_info(self, app_id: str) -> Sequence[Attachment]:
        """
        Get information about all the attachments on the given app.

        Parameters
        ----------
        app_id : str
            The ID of the app for which to query attachments.

        Returns
        -------
        attachments : Sequence[Attachment]
            Information about the app attachments on the given app.

        Raises
        ------
        scenario.ItemNotFoundError
            If the app does not exist, or the REST API client credentials do not have permission to access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     infos = client.get_all_app_attachment_info(
        ...         app_id='570b9100-46e3-4643-baee-2e24aa538f25')
        ...     for info in infos:
        ...         print(f'Found attachment named {info.name}')
        """
        return self._get_all_attachment_info(['api', 'apps', app_id, 'attachments'])

    def get_app_attachment(self, app_id: str, attachment_id: str,
                                destination: Union[str, TextIO, BinaryIO],
                                encoding: Optional[str] = 'utf-8') -> None:
        """
        Download the indicated app attachment.

        Parameters
        ----------
        app_id : str
            The ID of the app on which the attachment resides.
        attachment_id : str
            The ID of the attachment.
        destination : Union[str, TextIO, BinaryIO]
            Where to save the attachment content. This may be the name of a local file, or any file-like object.
        encoding : str, default 'utf-8'
            The character encoding to use when `destination` is of type `TextIO`. Defaults to `utf-8`.

        Raises
        ------
        scenario.ItemNotFoundError
            If the app or attachment does not exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.get_app_attachment(
        ...         app_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4',
        ...         destination='my_local_file.json')
        """
        return self._get_attachment(['api', 'apps', app_id, 'attachments'], attachment_id,
                                    destination,
                                    encoding=encoding)

    def put_app_attachment(self, app_id: str, attachment_name: str,
                                 source: Union[str, TextIO, BinaryIO],
                                 tag_name: Optional[str] = None,
                                 overwrite: bool = False,
                                 encoding: Optional[str] = 'utf-8') -> Attachment:
        """
        Upload an app attachment, either creating a new attachment or overwriting an existing one of the
        same name.

        Parameters
        ----------
        app_id : str
            The ID of the app on which to save the attachment.
        attachment_name : str
            The name to give the attachment (for example, `"factories.csv"`).
        source : Union[str, TextIO, BinaryIO]
            Where to read the attachment content. This may be the name of a local file, or any file-like object.
        tag_name : str, optional
            The name of a tag to give the attachment, if any.
        overwrite : bool, default False
            If set to `True`, the new attachment overwrites any existing app attachment that has the same name.
            If `False`, the new attachment is given a different name if there is an existing attachment
            with the same name.
        encoding : str, default 'utf-8'
            The character encoding to use when `source` is of type `TextIO`. Defaults to `utf-8`.

        Returns
        -------
        attachment : Attachment
            Information about the new or updated app attachment record.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario does not exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.put_app_attachment(
        ...         app_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_name='factories.csv',
        ...         source='factories.csv')
        """
        return self._put_attachment(['api', 'apps', app_id, 'attachments'], attachment_name,
                                    source,
                                    tag_name=tag_name,
                                    overwrite=overwrite,
                                    encoding=encoding)

    def set_app_attachment_info(self, app_id: str, attachment_id: str, updated_info: Union[Attachment, AttachmentUpdate]) -> None:
        """
        Update the filename, description, tags or 'hidden' flag for the given app attachment.

        Parameters
        ----------
        app_id : str
            The ID of the app on which the attachment resides.
        attachment_id : str
            The ID of the attachment.
        updated_info : Union[Attachment, AttachmentUpdate]
            The attachment info to update. Only the fields you want to change need be populated.

        Raises
        ------
        scenario.ItemNotFoundError
            If the app or attachment does not exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.put_app_attachment(
        ...         app_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4',
        ...         updated_info=ins.AttachmentUpdate(tags=['monthly', 'approved']))
        """
        return self._set_attachment_info(['api', 'apps', app_id, 'attachments'], attachment_id, updated_info)

    def delete_app_attachment(self, app_id: str, attachment_id: str) -> None:
        """
        Delete the specified app attachment.

        Parameters
        ----------
        app_id : str
            The ID of the app on which the attachment resides.
        attachment_id : str
            The ID of the attachment.

        Raises
        ------
        scenario.ItemNotFoundError
            If the app or attachment does not exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.delete_app_attachment(
        ...         app_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4')
        """
        return self._delete_attachment(['api', 'apps', app_id, 'attachments'], attachment_id)

    def delete_app(self, app_id: str) -> None:
        """
        Delete an existing app and all scenarios within it.

        Parameters
        ----------
        app_id : str
            The ID of the app to delete.

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
        ...     client.delete_app('570b9100-46e3-4643-baee-2e24aa538f25')
        """
        self._make_json_request(
            method='DELETE',
            path=['api', 'apps', app_id],
            response_type=None,
            expected_status_code=204
        )

    def create_app(self, app_file: Union[str, BinaryIO], app_name: Optional[str] = None,
                   override_app_name: bool = False) -> AppCreationResponse:
        """
        Create a new app.

        Parameters
        ----------
        app_file : Union[str, BinaryIO]
            Either the filename of the application .zip file, or a BinaryIO from which the application .zip
            data will be read.
        app_name : str, optional
            The app name to use. By default, this name is used only if no name is present in the app configuration.
        override_app_name : bool, default False
            Whether to use the supplied app name instead of any name found in the app configuration.

        Returns
        -------
        creation_response : AppCreationResponse
            Information about the newly-created app and any informational messages generated during creation.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     creation_response = client.create_app('new_app.zip')
        ...     print(f'Created new app {creation_response.app.id}')
        ...     for msg in creation_response.messages:
        ...         print(f'  {msg}')
        """

        #
        if isinstance(app_file, str):
            with open(app_file, "rb") as f:
                return self.create_app(f, app_name=app_name, override_app_name=override_app_name)

        #
        if app_name is None:
            app_name = 'app uploaded by xpressinsight.scenario'

        #
        request_body_fields = {
            'appFile': ('app.zip', app_file, INSIGHT_BINARY_CONTENT_TYPE),
            'appName': app_name
        }
        if override_app_name:
            request_body_fields['overrideAppName'] = app_name

        creation_response = self._make_json_request(
            method='POST',
            path=['api', 'apps'],
            request_body=MultipartEncoder(request_body_fields),
            response_type=models.AppCreationResponse,
            expected_status_code=201
        )

        return AppCreationResponse._from_rest_api_model(creation_response)

    def upgrade_app(self, app_id: str, app_file: Union[str, BinaryIO],
                    partial_upgrade: bool = False,
                    validate_model_name: bool = False,
                    wait_for_completion: bool = True) -> Optional[AppUpgradeResponse]:
        """
        Upgrade an existing app.

        Parameters
        ----------
        app_id : str
            The ID of the app to be upgraded.
        app_file : Union[str, BinaryIO]
            Either the filename of the application .zip file, or a BinaryIO from which the application .zip
            data will be read.  This should be a complete replacement for the existing app unless partial_upgrade=True.
        partial_upgrade : bool, default False
            If True, the supplied .zip file need only contain the files that have modified. Files from the original
            app not included in this zipfile are retained unchanged. If False, the .zip file is a complete
            replacement for the existing app, and any files not included in the new .zip file are removed from the
            Insight server.
        validate_model_name : bool, default False
            If True, validate that the model name in the supplied .zip file matches the model name of the existing
            app in the Insight server.
        wait_for_completion : bool, default True
            If True, the function does not return until the upgrade has completed. If False, the function returns
            immediately after upgrade is accepted by the Insight server (which might be before the app upgrade
            has completed).

        Returns
        -------
        upgrade_response : AppUpgradeResponse, optional
            Information about the app upgrade; this is not available if `wait_for_completion=False`.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     upgrade_response = client.upgrade_app(
        ...        '570b9100-46e3-4643-baee-2e24aa538f25', 'new_app.zip')
        ...     print(f'App upgrade completed')
        ...     for msg in upgrade_response.messages:
        ...         print(f'  {msg}')
        """

        #
        if isinstance(app_file, str):
            with open(app_file, "rb") as f:
                return self.upgrade_app(app_id, f,
                                        partial_upgrade=partial_upgrade,
                                        validate_model_name=validate_model_name,
                                        wait_for_completion=wait_for_completion)

        #
        upgrade_request = models.UpgradeRequest(
            reference=models.Reference(id=app_id, object_type='APP'),
            upgrade_type='PARTIAL' if partial_upgrade else 'FULL',
            validate_model_name=validate_model_name
        )
        request_body_fields = {
            'app': ('app.zip', app_file, INSIGHT_BINARY_CONTENT_TYPE),
            'upgradeRequest': ('', upgrade_request.model_dump_json(by_alias=True).encode('utf-8'),
                               INSIGHT_JSON_CONTENT_TYPE)
        }

        upgrade_response = self._make_json_request(
            method='POST',
            path=['api', 'portations', 'upgrades'],
            request_body=MultipartEncoder(request_body_fields),
            response_type=models.Upgrade,
            expected_status_code=201
        )

        #
        if wait_for_completion:
            upgrade_id = upgrade_response.id
            next_delay = 0.001
            while upgrade_response.status in ('QUEUED', 'MIGRATING', 'PORTING'):
                #
                time.sleep(next_delay)
                if next_delay < 0.250:
                    next_delay += 0.025

                #
                upgrade_response = self._make_json_request(
                    method='GET',
                    path=['api', 'portations', 'upgrades', upgrade_id],
                    response_type=models.Upgrade
                )

        #
        if upgrade_response.status == 'ERROR':
            if upgrade_response.error_messages is None or len(upgrade_response.error_messages) == 0:
                raise InsightServerError(f'Failed to upgrade app {app_id}')
            raise InsightServerError(f'Failed to upgrade app {app_id} due to: ' +
                                     "\n".join(upgrade_response.error_messages))

        if wait_for_completion:
            if upgrade_response.status != 'SUCCESS':
                raise InsightServerResponseError(f'Unrecognized upgrade response status "{upgrade_response.status}"')

            return AppUpgradeResponse._from_rest_api_model(upgrade_response)

        #
        return None

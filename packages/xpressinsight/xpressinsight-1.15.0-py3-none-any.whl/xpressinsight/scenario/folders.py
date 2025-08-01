"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly. This defines functions and classes for accessing Insight
    folder information through the REST interface.

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
from typing import Annotated, Union, Sequence, Optional
import sys

from pydantic import Field, RootModel

from .apps import App
from .common import Reference, ShareStatus, parse_insight_enum_value, ObjectType, get_rest_resource_name
from .scenarios import Scenario
from .rest_client_base import InsightRestClientBase
from . import models

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


@dataclass
class Folder:
    """
    Information about a single folder.

    Attributes
    ----------
    id : str
        The ID of the folder.
    app : Reference
        Information about the app that owns the folder.
    name : str
        Name of the folder.
    owner : Reference
        Information about the user that owns the folder.
    parent : Reference
        Information about the parent of the folder. This will be a reference of either type `FOLDER` or type `APP`.
    path : str
        Absolute path of the folder.
    share_status : ShareStatus
        The share status of the folder.
    """
    id: str
    app: Reference
    name: str
    owner: Reference
    parent: Reference
    path: str
    share_status: ShareStatus

    @classmethod
    def _from_rest_api_model(cls, src: models.Folder) -> Self:
        return Folder(
            id=src.id,
            app=Reference._from_rest_api_model(src.app),
            name=src.name,
            owner=Reference._from_rest_api_model(src.owner),
            parent=Reference._from_rest_api_model(src.parent),
            path=src.path,
            share_status=parse_insight_enum_value(ShareStatus, src.share_status)
        )


class InsightFolderOperations(InsightRestClientBase, ABC):
    """
    Implementation of calls to folder-related endpoints in the Insight REST API.
    """

    def get_item_by_path(self, path: str) -> Union[App, Folder, Scenario]:
        """
        Get the scenario, folder, or app record for the given repository path.

        Parameters
        ----------
        path : str
            The repository path to query

        Returns
        -------
        item : Union[App, Folder, Scenario]
            Information about the app, folder, or scenario.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is nothing at this path, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     scenario = client.get_item_by_path('/MyApp/MyFolder/MyPath')
        ...     if not isinstance(scenario, ins.Scenario):
        ...         raise RuntimeError(f'Expected Scenario, found {type(scenario)}')
        ...     print(f'Found scenario {scenario.id} at path {scenario.path}')
        """
        item = self._make_json_request(
            path="/api/repository",
            method="GET",
            query_params={
                "path": path
            },
            #
            response_type=RootModel[Annotated[Union[models.App, models.Folder, models.Scenario],
                                              Field(discriminator='object_type')]]
        )

        #
        if isinstance(item.root, models.Scenario):
            return Scenario._from_rest_api_model(item.root)

        if isinstance(item.root, models.Folder):
            return Folder._from_rest_api_model(item.root)

        if isinstance(item.root, models.App):
            return App._from_rest_api_model(item.root)

        raise TypeError(f"Unexpected response type {type(item)}")

    def get_folder(self, folder_id: str) -> Folder:
        """
        Get the scenario record for the folder with the given ID.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to query.

        Returns
        -------
        folder : Folder
            Information about the folder with the requested ID.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no folder with this ID, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     folder = client.get_folder('570b9100-46e3-4643-baee-2e24aa538f25')
        ...     print(f'Found folder {folder.name} with path {folder.path}')
        """
        folder = self._make_json_request(
            method='GET',
            path=['api', 'folders', folder_id],
            response_type=models.Folder
        )

        # noinspection PyProtectedMember
        return Folder._from_rest_api_model(folder)

    def create_folder(self,
                      name: str,
                      parent: Reference) -> Folder:
        """
        Create a new folder within an app.

        Parameters
        ----------
        name : str
            The desired name for the folder. A suffix is applied to ensure the name is unique among
            its siblings.
        parent : Reference
            A Reference of type `FOLDER` containing the ID of the folder in which to create the folder, or a
            reference of type `APP` containing the app ID if the folder is to be created in the app root.

        Returns
        -------
        folder : Folder
            Information about the newly-created folder.

        Raises
        ------
        scenario.InsightServerError
            If the folder could not be created in the requested location, the REST client credentials do not have
            permission to perform this operation, or there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     PARENT_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     folder = client.create_folder(name='My New Folder',
        ...         parent=Reference.to_folder(PARENT_ID))
        ...     print(f'Created folder with ID {folder.id}')
        """
        if parent.type not in (ObjectType.FOLDER, ObjectType.APP):
            raise ValueError(f'Unexpected parent type "{parent.type.name}"')

        creation_request = models.FolderCreationRequest(
            name=name,
            parent=parent._to_rest_api_model()
        )

        folder = self._make_json_request(
            method='POST',
            path=['api', 'folders'],
            request_body=creation_request,
            response_type=models.Folder,
            expected_status_code=201
        )

        # noinspection PyProtectedMember
        return Folder._from_rest_api_model(folder)

    def delete_folder(self, folder_id: str) -> None:
        """
        Delete an existing folder, including any subfolders and scenarios within it.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to delete.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no folder with this ID, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.delete_folder('570b9100-46e3-4643-baee-2e24aa538f25')
        """
        self._make_json_request(
            method='DELETE',
            path=['api', 'folders', folder_id],
            response_type=None,
            expected_status_code=204
        )

    def get_children(self, parent: Reference) -> Sequence[Union[Scenario, Folder]]:
        """
        Get the folders and scenarios that are the immediate children of the given folder or app.

        Parameters
        ----------
        parent : Reference
            A Reference of type FOLDER or APP.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no folder with this ID, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     APP_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     children = client.get_children(Reference.to_app(APP_ID)
        ...     for child in children:
        ...         if isinstance(child, ins.Folder):
        ...             print(f'Found folder {child.name}')
        ...         else:
        ...             print(f'Found scenario {child.name}')

        Notes
        -----
        Pass a reference to a Folder to return the scenarios and immediate subfolders of that folder.  Pass a reference
        to an App to return the scenarios and folders in the application root.
        """
        if parent.type not in (ObjectType.FOLDER, ObjectType.APP):
            raise ValueError(f'Unexpected parent type "{parent.type.name}"')

        all_models = self._make_paged_json_request(
            path=['api', get_rest_resource_name(parent.type), parent.id, 'children'],
            method='GET',
            item_type=RootModel[Annotated[Union[models.Scenario, models.Folder], Field(discriminator='object_type')]]
        )

        # noinspection PyProtectedMember
        return [Scenario._from_rest_api_model(mdl.root)
                if isinstance(mdl.root, models.Scenario)
                else Folder._from_rest_api_model(mdl.root)
                for mdl in all_models]

    def move_folder(self, folder_id: str, new_parent: Reference) -> None:
        """
        Move a folder to a different parent folder or to the app root.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to move.
        new_parent : Reference
            A Reference to either a folder in the same app as the folder, or the app ID in which the folder
            resides if moving to the app root.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.

        Examples
        --------
        To move a folder to a different folder:

        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     DESTINATION_ID = 'f3336733-5cf9-49fc-84f0-3e7ee80df98e'
        ...     client.move_folder('570b9100-46e3-4643-baee-2e24aa538f25',
        ...                          new_parent=Reference.to_folder(DESTINATION_ID))
        """
        if new_parent.type not in (ObjectType.FOLDER, ObjectType.APP):
            raise ValueError(f'Unexpected parent type "{new_parent.type.name}"')

        self._make_json_request(
            path=['api', get_rest_resource_name(new_parent.type), new_parent.id, 'children'],
            method='POST',
            request_body=models.Reference(
                id=folder_id,
                object_type='FOLDER'
            ),
            response_type=None
        )

    def rename_folder(self, folder_id: str, new_name: str) -> None:
        """
        Rename an existing folder.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to rename.
        new_name : str
            The new name for the folder.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.

        Examples
        --------
        Example of updating the name of a folder.

        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.rename_folder('570b9100-46e3-4643-baee-2e24aa538f25', 'March')
        """
        self._make_json_request(
            path=['api', 'folders', folder_id],
            method='PATCH',
            request_body=models.FolderUpdateRequest(name=new_name),
            response_type=None
        )

    def set_folder_owner(self, folder_id: str, new_owner_id: str, new_share_status: Optional[ShareStatus] = None
                         ) -> None:
        """
        Update folder owner and (optionally) share status.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to update.
        new_owner_id : str
            The ID of the user who should become the folder owner.
        new_share_status : ShareStatus, optional
            The new share status of the folder, if this is also being updated.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.
        """
        self._make_json_request(
            path=['api', 'folders', folder_id],
            method='PATCH',
            request_body=models.FolderUpdateRequest(owner=models.Reference(id=new_owner_id, object_type='USER'),
                                                    share_status=(None if new_share_status is None
                                                                  else new_share_status.name)),
            response_type=None
        )

    def set_folder_share_status(self, folder_id: str, new_share_status: ShareStatus) -> None:
        """
        Update folder share status.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to update.
        new_share_status : ShareStatus
            The new share status of the folder.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.
        """
        self._make_json_request(
            path=['api', 'folders', folder_id],
            method='PATCH',
            request_body=models.FolderUpdateRequest(share_status=new_share_status.name),
            response_type=None
        )

"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

import os
import shutil
import sys
import inspect
from contextlib import nullcontext
from tempfile import TemporaryDirectory
from typing import Type, TypeVar

from .app_base import AppBase
from .interface import AttachType, AppInterface, XpriAttachmentsCache

AppBaseChild = TypeVar('AppBaseChild', bound=AppBase)


def copy_flat_dir(src: str, dst: str):
    """ Throws OSError or shutil.SameFileError on failure. """
    if src != dst:
        try:
            for file_name in os.listdir(src):
                file_path = os.path.join(src, file_name)

                if os.path.isfile(file_path):
                    shutil.copy(file_path, dst)

        except (OSError, shutil.SameFileError) as e:
            print(f'Could not copy files from {repr(src)} to {repr(dst)}.', file=sys.stderr)
            raise e


def copy_flat_dir_if_exists(src: str, dst: str, dir_name: str, quiet: bool = False):
    """ Copy src directory if it exists, do nothing otherwise. """
    if os.path.exists(src):
        copy_flat_dir(src, dst)
    elif not quiet:
        print(f'Test mode: {dir_name} directory does not exist. Skipping: "{src}".')


def _prepare_test_validate_input(insight: AppInterface, base_dir: str, app_work_dir: str):
    #
    if not os.path.exists(os.path.join(base_dir, 'python_source')):
        raise ValueError(f"Invalid 'base_dir' directory: {base_dir!r}. 'python_source' folder is missing.")

    #
    if not os.path.isfile(insight.test_cfile_path):
        raise ValueError(f"Invalid 'companion_file': {insight.test_cfile_path!r} is not a file.")

    #
    if not os.path.isabs(app_work_dir):
        raise ValueError(f"Invalid 'app_work_dir': {app_work_dir!r} must be an absolute path.")

    #
    if base_dir.startswith(app_work_dir):
        raise ValueError(f"Invalid 'app_work_dir': {app_work_dir!r}. "
                         "Directory must differ from 'base_dir' and must not be a parent of 'base_dir'.")

    if base_dir.startswith(insight.work_dir):
        raise ValueError(f"Invalid Insight working directory: {insight.work_dir!r}. "
                         "Directory must differ from 'base_dir' and must not be a parent of 'base_dir'.")

    #
    protected_dirs = [os.path.join(base_dir, dir_name) for dir_name in
                      ['attachments', 'client_resources', 'model_resources', 'python_source', 'source', 'out', '.c9']]

    if app_work_dir in protected_dirs:
        raise ValueError(f"Invalid 'app_work_dir': {app_work_dir!r} is a protected directory.")

    if insight.work_dir in protected_dirs:
        raise ValueError(f"Invalid Insight working directory: {insight.work_dir!r} is a protected directory.")


def prepare_test(app: AppBase, base_dir: str, companion_file: str, app_work_dir: str = None,
                 preserve_insight_work_dir: bool = False):
    """
    Prepare environment for the test mode.

    Parameters
    ----------
    app : AppBase
        xpressinsight.AppBase instance.
    base_dir : str
        Path to application base directory (absolute or relative to current working directory).
    companion_file : str
        Path to application companion XML file (absolute or relative to `base_dir`).
    app_work_dir : str = None
        Absolute path to temporary application working directory.
    preserve_insight_work_dir : bool, default False
        Whether to retain any existing content in the temporary Insight working directory. If False
        (the default), this directory will be emptied by create_app.

    Notes
    -----

    The function first deletes the application working directory, if it exists, and then initializes a new one,
    by copying the model resources to the new directory.
    Afterwards it deletes the application working directory, if it exists, and then initializes a new one, by copying
    the attachments to the newly created folder structure.

    The function also sets the working directory of the Python process to `app_work_dir`, and the internal
    work directory to `app_work_dir/xpressinsight` unless an alternative path is specified.

    Throws an exception on failure: `OSError` or `shutil.SameFileError` if a file operation fails;
    `ValueError` if input values are invalid.
    """
    base_dir = os.path.abspath(base_dir)

    app.insight.test_cfile_path = companion_file if os.path.isabs(companion_file) \
        else os.path.join(base_dir, companion_file)

    _prepare_test_validate_input(app.insight, base_dir, app_work_dir)

    #
    preserve_insight_work_dir = preserve_insight_work_dir and os.path.exists(app.insight.work_dir)

    #
    with (TemporaryDirectory() if preserve_insight_work_dir else nullcontext()) as preserved_insight_work_dir:
        if preserve_insight_work_dir:
            shutil.copytree(app.insight.work_dir, preserved_insight_work_dir, dirs_exist_ok=True)

        #
        if os.path.isdir(app_work_dir):
            print(f'Test mode: Deleting existing application working directory: "{app_work_dir}".')
            shutil.rmtree(app_work_dir)

        print(f'Test mode: Initializing new application working directory: "{app_work_dir}".')
        os.makedirs(app_work_dir, exist_ok=True)

        #
        if preserve_insight_work_dir:
            print(f'Test mode: Restoring existing Insight working directory: "{app.insight.work_dir}".')
            shutil.copytree(preserved_insight_work_dir, app.insight.work_dir)

    #
    model_resources = os.path.join(base_dir, 'model_resources')
    copy_flat_dir_if_exists(model_resources, app_work_dir, 'Model resources')

    #
    os.chdir(app_work_dir)

    #
    if not preserve_insight_work_dir:
        app.insight.delete_work_dir()
        print(f'Test mode: Initializing new Insight working directory: "{app.insight.work_dir}".')

        #
        #
        # noinspection PyProtectedMember,PyUnresolvedReferences
        test_attach_dir = app.insight._xpri_get_test_mode_dir(attach_cache=XpriAttachmentsCache(type=AttachType.APP))
        app_attach_dir = os.path.join(base_dir, 'attachments')
        copy_flat_dir_if_exists(app_attach_dir, test_attach_dir, 'Attachments')


def get_app_base_dir(app_type: Type[AppBaseChild]) -> str:
    """
    Try to determine the application base directory with the help of the location of the source file
    that defines the application type.

    Parameters
    ----------
    app_type : Type[AppBase]
        Insight application type.

    Returns
    -------
    app_base_dir : str
        Path to the application base directory.
    """
    app_source_file = os.path.abspath(inspect.getfile(app_type))
    base_dir = os.path.dirname(os.path.dirname(app_source_file))

    if base_dir != '':
        return base_dir
    raise IOError('Could not determine the location of the application base directory. '
                  'Please specify the application base directory.')


def get_companion_file(base_dir: str) -> str:
    """
    Try to find companion file in application base directory. The function searches for all XML files in the base
    directory. If there is a unique XML file then its filename will be returned. Otherwise the function raises
    an `IOError`.

    Parameters
    ----------
    base_dir : str
        Application base directory.

    Returns
    -------
    companion_file : str
        Relative filename of companion file in base directory.
    """
    xml_files = [f for f in os.listdir(base_dir) if f.lower().endswith(".xml")]
    num_files = len(xml_files)

    if num_files == 1:
        return xml_files[0]

    msg = '\nPlease specify the location of the XML companion file.'
    if num_files == 0:
        raise IOError(f'Could not find XML companion file in application base directory: "{base_dir}".{msg}')

    raise IOError(f'Found multiple XML files in application base directory: "{base_dir}".{msg}')


def _create_app_validate_types(app_type: Type[AppBaseChild], base_dir: str = None, companion_file: str = None,
                               app_work_dir: str = None, insight_work_dir: str = None):
    if not isinstance(app_type, type) or not issubclass(app_type, AppBase) or app_type == AppBase:
        raise TypeError("Parameter 'app_type' must be a subclass of xpressinsight.AppBase.")

    optional_str = (str, type(None))

    if not isinstance(base_dir, optional_str):
        raise TypeError(f"Parameter 'base_dir' must be a string, but is a {type(base_dir)}.")

    if not isinstance(companion_file, optional_str):
        raise TypeError(f"Parameter 'companion_file' must be a string, but is a {type(companion_file)}.")

    if not isinstance(app_work_dir, optional_str):
        raise TypeError(f"Parameter 'app_work_dir' must be a string, but is a {type(app_work_dir)}.")

    if not isinstance(insight_work_dir, optional_str):
        raise TypeError(f"Parameter 'insight_work_dir' must be a string, but is a {type(insight_work_dir)}.")


def create_app(app_type: Type[AppBaseChild], base_dir: str = None, companion_file: str = None,
               app_work_dir: str = None, insight_work_dir: str = None,
               preserve_insight_work_dir: bool = False) -> AppBaseChild:
    """
    Prepare the environment for the test mode and return a new Insight app instance.

    Parameters
    ----------
    app_type : Type[AppBase]
        A subclass of xpressinsight.AppBase.
    base_dir : str, optional
        Path to application base directory (absolute or relative to current working directory).
        By default, it will be set to the parent directory of the source file that defines the `app_type` class.
    companion_file : str, optional
        Path to application companion XML file (absolute or relative to `base_dir`). By default,
        it will be set to the unique XML file that is located in the application base directory.
    app_work_dir : str, optional
        Absolute path to temporary application working directory.
        By default, it will be set to the subfolder "work_dir" in the application base directory.
    insight_work_dir : str, optional
        Absolute path to temporary Insight working directory.
        By default, it will be set to the subfolder "work_dir/xpressinsight" in the application base directory.
    preserve_insight_work_dir : bool, default False
        Whether to retain any existing content in the temporary Insight working directory. If False
        (the default), this directory will be emptied by create_app.

    Returns
    -------
    app : AppBase
        An instance of the Insight app, i.e., an instance of `app_type`.

    Notes
    -----

    *WARNING*:
    The function first deletes the temporary application working directory `app_work_dir`, if it exists,
    and then initializes a new one, by copying the model resources to the new directory. Then it deletes
    the temporary Insight working directory `insight_work_dir`, if it exists, and initializes a new one,
    by copying the attachments to the newly created folder structure.

    The function also sets the working directory of the Python process to `app_work_dir`.

    Throws an exception on failure: `OSError` or `shutil.SameFileError` if a file operation fails;
    `ValueError` or `TypeError` if input values are invalid.

    Examples
    --------
    A typical use case for this function is the `__main__` section of the application source file.
    At first we initialize the test mode environment for the app, then we call the load and run modes.

    >>> import xpressinsight as xi
    ...
    ... @xi.AppConfig(name="Insight Python App")
    ... class MyApp(xi.AppBase):
    ...     @xi.ExecModeLoad()
    ...     def load(self):
    ...         print(self.insight.exec_mode, "mode ...")
    ...
    ...     @xi.ExecModeRun()
    ...     def run(self):
    ...         print(self.insight.exec_mode, "mode ...")
    ...
    ... if __name__ == "__main__":
    ...     app = xi.create_app(MyApp)
    ...     sys.exit(app.call_exec_modes(["LOAD", "RUN"]))

    """
    _create_app_validate_types(app_type, base_dir, companion_file, app_work_dir, insight_work_dir)

    #
    if insight_work_dir is not None and not os.path.isabs(insight_work_dir):
        raise ValueError(f"Invalid 'insight_work_dir': {insight_work_dir!r} must be an absolute path.")

    #
    base_dir = get_app_base_dir(app_type) if base_dir is None else os.path.abspath(base_dir)
    companion_file = get_companion_file(base_dir) if companion_file is None else companion_file
    app_work_dir = os.path.join(base_dir, 'work_dir') if app_work_dir is None else app_work_dir
    insight_work_dir = insight_work_dir if insight_work_dir is not None else os.path.join(app_work_dir, "xpressinsight")

    #
    #
    #
    # noinspection PyProtectedMember
    app_type.get_app_cfg()._next_app_attrs.work_dir = insight_work_dir
    # noinspection PyProtectedMember
    app_type.get_app_cfg()._next_app_attrs.test_mode = True
    try:
        app = app_type()
    finally:
        # noinspection PyProtectedMember
        app_type.get_app_cfg()._next_app_attrs.reset()

    prepare_test(app, base_dir, companion_file, app_work_dir,
                 preserve_insight_work_dir=preserve_insight_work_dir)
    return app

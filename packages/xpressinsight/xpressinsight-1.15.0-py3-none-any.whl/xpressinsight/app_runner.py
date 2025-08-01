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
import sys
import importlib
from typing import Type, TypeVar, Iterable, List
import warnings

from packaging import version

from . import __version__
from .app_base import AppBase
from .exec_mode import ExecMode

#
T = TypeVar("T")
MSG_PREFIX = "xpressinsight: "


def exit_msg(code: int, msg: str):
    """ Print message to stderr then exit Python with given status code. """
    print(MSG_PREFIX + msg, file=sys.stderr)
    sys.exit(code)


def __filter_out_superclasses(classes: Iterable[Type[T]]) -> List[Type[T]]:
    """ Given a list of classes, filter out any classes that are superclasses of other classes in the list
        (i.e. return leaf classes of an inheritance hierarchy). """
    #
    filtered_classes: List[Type[T]] = []

    for cls in classes:
        is_superclass = False

        for cls2 in classes:
            if cls2 != cls and issubclass(cls2, cls):
                is_superclass = True
                break

        if not is_superclass:
            filtered_classes.append(cls)

    return filtered_classes


def import_app(app_source_dir: str, app_package_name: str = 'application') -> Type[AppBase]:
    """
    Import an Insight application class from an Insight application package. The function
    returns the first class in the imported package that extends the AppBase class.

    Side effects:
    Adds application source directory to sys.path. The imported application package can be
    imported again even after reverting sys.path to it's original value.

    @param app_source_dir: Source directory of the application package.
    @param app_package_name: Name of the application package or main file.
    @return: Imported Insight app class, i.e., a subclass of xpressinsight.AppBase.
    """
    if not os.path.isdir(app_source_dir):
        exit_msg(-1, f'import_app: Parameter app_source_dir="{app_source_dir}" is not a directory.')

    if app_package_name != 'application':
        exit_msg(-1, f'import_app: Parameter app_package_name must be set to "application", but it '
                     f'is "{app_package_name}".')

    app_source_dir = os.path.abspath(app_source_dir)

    #
    sys.path.append(app_source_dir)

    #
    old_pythonpath = os.environ.get('PYTHONPATH')
    os.environ['PYTHONPATH'] = f"{app_source_dir}{os.pathsep}{old_pythonpath}" if old_pythonpath else app_source_dir

    try:
        app_pkg = importlib.import_module(app_package_name)
    except (ImportError, ModuleNotFoundError):
        print(f'{MSG_PREFIX}import_app: Could not import "{app_package_name}" package from directory: {app_source_dir}',
              file=sys.stderr)
        raise

    app_pkg_dir = os.path.dirname(app_pkg.__file__)

    if app_pkg_dir != app_source_dir:
        print(f"{MSG_PREFIX}Imported application from non-standard location: {app_pkg_dir}", file=sys.stderr)

    #
    #
    app_classes = list(filter(lambda pkg_attr: isinstance(pkg_attr, type) and issubclass(pkg_attr, AppBase),
                              app_pkg.__dict__.values()))

    #
    #
    app_classes = __filter_out_superclasses(app_classes)

    if len(app_classes) == 1:
        return app_classes[0]

    if len(app_classes) > 1:
        exit_msg(-1, f'import_app: The "{app_package_name}" package defines multiple application classes.')

    exit_msg(-1, f'import_app: The "{app_package_name}" package does not define a subclass of xpressinsight.AppBase.')

    #
    #
    raise RuntimeError("exit_msg should have exited Python")


#
#
# pylint: disable-next=too-many-arguments
def run(app_source_dir: str, work_dir: str, exec_mode: str, apprunner_version: str = None,
        test_mode: bool = None, app_package_name: str = 'application'):
    """ Run the specified app. """
    print("xpressinsight package v" + __version__)

    if sys.version_info < (3, 9):
        exit_msg(-1, f'Unsupported Python version {sys.version_info} detected.')
    if sys.version_info >= (3, 14):
        warnings.warn(f'Unsupported Python version {sys.version_info} detected; v{__version__} of the xpressinsight '
                      f'package has not been proven on this version.', RuntimeWarning)

    if not os.path.isdir(work_dir):
        exit_msg(-1, f'app_runner.run: Parameter work_dir="{work_dir}" is not a directory.')

    if not isinstance(exec_mode, str):
        exit_msg(-1, f'app_runner.run: Parameter exec_mode="{exec_mode}" must be a string.')

    if test_mode is None:
        test_mode = bool(exec_mode == ExecMode.NONE)
    elif not isinstance(test_mode, bool):
        exit_msg(-1, f'app_runner.run: Parameter test_mode="{test_mode}" must be a bool.')

    #
    app_type = import_app(app_source_dir, app_package_name)
    app_type.get_app_cfg()._next_app_attrs.work_dir = work_dir
    app_type.get_app_cfg()._next_app_attrs.test_mode = test_mode

    #
    #
    #
    #
    if apprunner_version is None or version.parse(apprunner_version) < version.parse('1.8.0'):
        print("ERROR: Old version of Xpress Insight server detected. Please upgrade to a more recent version, "
              "or downgrade 'xpressinsight' Python package.", file=sys.stderr)
        sys.exit(1)

    if exec_mode == ExecMode.NONE:
        exit_code = app_type().load_and_run(delete_work_dir=False)
    else:
        exit_code = app_type().call_exec_mode(exec_mode)

    sys.exit(exit_code)

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

from math import floor
import os
import shutil
import sys
from typing import Dict, List, TextIO, Tuple, Type, ValuesView

from . import __version__
from .app_runner import exit_msg, import_app
from .app_base import AppBase, AppConfig
from .exec_mode import ExecMode
from .exec_resource_group import ExecResourceGroup
from .entities import (BASIC_TYPE, BasicType, boolean, integer, string, real,
                       Entity, EntityBase, Param, Scalar, IndexBase,
                       Series, DataFrameBase, Hidden, UnexpectedEntityTypeError, Indexed)
from .mosel import validate_ident, validate_raw_ident, validate_annotation_str


def quote_mos(value: str, max_length: int = 5000) -> str:
    """ Get Mosel source code representation of a string, without type or bound checking. """
    #
    #
    #
    #
    #
    #
    #
    if '\0' in value:
        raise ValueError(f"Null character '\0' not allowed in string: {repr(value)}")
    if len(value) > max_length:
        raise ValueError(f"The string must not be longer than {max_length} characters: {repr(value)}.")

    result = (value.
              replace('\\', r'\\').
              replace('"', r'\"').
              replace('\n', r'\n').
              replace('\r', r'\r').
              replace('\t', r'\t'))
    return '"' + result + '"'


mos_repr_str = quote_mos


def mos_repr_bool(value: bool) -> str:
    """ Get the Mosel source code representation of an bool, without type or bound checking. """
    return 'true' if value else 'false'


def mos_repr_int(value: int) -> str:
    """ Get the Mosel source code representation of an int, without type or bound checking. """
    return repr(value)


def mos_repr_real(value: float) -> str:
    """ Get the Mosel source code representation of a float, without type or bound checking. """
    #
    #
    return repr(value)


class CodeGenerator:
    """ Class to generate the Mosel part of the Python app. """
    BASIC_TYPE_NAME_MAP: Dict[Type[BasicType], str] = {
        boolean: 'boolean',
        integer: 'integer',
        string: 'string',
        real: 'real',
    }

    BASIC_SQL_TYPE_NAME_MAP: Dict[Type[BasicType], str] = {
        boolean: 'SQL_TYPE_BOOL',
        integer: 'SQL_TYPE_INT',
        string: 'SQL_TYPE_STR',
        real: 'SQL_TYPE_REAL',
    }

    @classmethod
    def __declaration_safe_sorted(cls, entities: List[EntityBase]) -> List[EntityBase]:
        """ Given list of entities, sort into an order that can be safely declared in Mosel. """
        #
        #
        #
        #
        #
        entities_with_indexes = [e for e in entities if isinstance(e, Indexed)]
        entities_without_indexes = [e for e in entities if not isinstance(e, Indexed)]
        return entities_without_indexes + entities_with_indexes

    def __init__(self, app_cls: Type[AppBase], file: TextIO):
        self.file: TextIO = file
        self.app_cls: Type[AppBase] = app_cls
        self.app_cfg: AppConfig = app_cls.get_app_cfg()
        self.exec_modes = self.app_cfg.exec_modes
        self.exec_resource_groups = self.app_cfg.exec_resource_groups
        self.entities: ValuesView[EntityBase] = self.app_cfg.entities
        self.params: List[Param] = [e for e in self.entities if isinstance(e, Param)]
        self.declared_entities: List[EntityBase] = CodeGenerator.__declaration_safe_sorted(
            [e for e in self.entities if not isinstance(e, Param)])

    def write_header(self):
        """ Write header at the top of the Mosel source file. """
        self.file.write(f"""! This is a generated file. Do not modify it.
model {quote_mos(self.app_cfg.name)}
    version {validate_annotation_str(str(self.app_cfg.version))}\n
    uses "mminsight"
    uses "apprunner"\n
    namespace AppRunner
    nssearch AppRunner\n\n""")

    def write_app_config_annotations(self):
        """ Write app global annotations to the Mosel source file. """
        for scen_type in self.app_cfg.scen_types:
            scenario_type_identifier = validate_raw_ident(scen_type, 'scenario type identifier')
            self.file.write(f"        @insight.scentypes.{scenario_type_identifier}\n")

        annotation_str = validate_annotation_str(self.app_cfg.result_data.delete.value)
        self.file.write(f"\n        @insight.resultdata.delete {annotation_str}\n")

        if self.app_cfg.partial_populate:
            self.file.write("\n        @apprunner.populate.skip true\n")

    def write_exec_mode(self, mode: ExecMode):
        """ Write execution mode annotations to the Mosel source file. """
        self.file.write(f"""
        @insight.execmodes.{validate_raw_ident(mode.name, 'execution mode name')}.
            @descr {validate_annotation_str(mode.descr)}
            @clearinput {mos_repr_bool(mode.clear_input)}\n""")

        if mode.preferred_service != '':
            self.file.write(f"            @preferredservice {mode.preferred_service}\n")

        if mode.threads != 0:
            self.file.write(f"            @threads {mode.threads}\n")

        if mode.exec_resource_group_name:
            self.file.write(f"            @execresourcegroup {mode.exec_resource_group_name}\n")

        if mode.send_progress:
            self.file.write("            @sendprogress true\n")

    def write_exec_resource_group(self, exec_resource_group: ExecResourceGroup):
        """ Write execution mode annotations to the Mosel source file. """
        self.file.write(f"""
        @insight.execresourcegroups.{validate_raw_ident(exec_resource_group.name, 'execution resource group name')}.
            @descr {validate_annotation_str(exec_resource_group.descr)}\n""")

        if exec_resource_group.min_threads != 0:
            self.file.write(f"            @minthreads {exec_resource_group.min_threads}\n")

        if exec_resource_group.default_threads != 0:
            self.file.write(f"            @defaultthreads {exec_resource_group.default_threads}\n")

        if exec_resource_group.min_memory:
            self.file.write(f"            @minmemory {exec_resource_group.min_memory}\n")

        if exec_resource_group.default_memory:
            self.file.write(f"            @defaultmemory {exec_resource_group.default_memory}\n")

    def write_global_annotations(self):
        """ Write global annotations to the Mosel source file. """
        self.file.write("""    (!@.\n""")
        self.write_app_config_annotations()

        for resource_group in self.exec_resource_groups:
            self.write_exec_resource_group(resource_group)

        for mode in self.exec_modes:
            self.write_exec_mode(mode)

        self.file.write("""
        @.              Unselect current category.
        @mc.flush       Define previous annotations as global.
    !)\n\n""")

    def write_one_line_xi_annotation(self, name: str, value: str):
        """ Write a single line Insight annotation with a value. Indentation 8."""
        self.file.write(f'        !@insight.{name} {validate_annotation_str(value)}\n')

    def write_entity_annotations(self, entity: Entity):
        """ Write all annotations of an entity. Each annotation is written as a single line comment. Indentation 8. """

        #
        #

        if entity.alias != "":
            self.write_one_line_xi_annotation('alias', entity.alias)

        if entity.format != "":
            self.write_one_line_xi_annotation('format', entity.format)

        if entity.hidden != Hidden.FALSE:
            self.write_one_line_xi_annotation('hidden', entity.hidden.value)

        #
        if not isinstance(entity, Param):
            self.write_one_line_xi_annotation('manage', entity.manage.value)

        if entity.read_only:
            self.write_one_line_xi_annotation('readonly', mos_repr_bool(entity.read_only))

        if entity.transform_labels_entity != "":
            self.write_one_line_xi_annotation('transform.labels.entity', entity.transform_labels_entity)

        if not isinstance(entity, Param):
            if entity.update_after_execution:
                self.write_one_line_xi_annotation('update.afterexecution', mos_repr_bool(True))

            if entity.update_keep_result_data:
                self.write_one_line_xi_annotation('update.keepresultdata', mos_repr_bool(True))

            if entity.update_progress:
                self.write_one_line_xi_annotation('update.progress', mos_repr_bool(True))

    def declare_param(self, param: Param):
        """ Write a parameter declaration to the Mosel source file. """
        self.write_entity_annotations(param)

        #
        param.check_value(param.default)

        if param.dtype == string:
            value_str = mos_repr_str(param.default)
        elif param.dtype == integer:
            value_str = mos_repr_int(param.default)
        elif param.dtype == real:
            value_str = param.default.hex() + "  ! " + mos_repr_real(param.default)
        elif param.dtype == boolean:
            value_str = mos_repr_bool(param.default)
        else:
            raise ValueError(f"Unexpected value of dtype={param.dtype} in parameter {param.name}.")

        self.file.write(f'        {validate_ident(param.name)} = {value_str}\n')

    def declare_parameters(self):
        """ Write the parameter declarations to the Mosel source file. """
        if len(self.params) > 0:
            self.file.write('    parameters\n')

            for i, param in enumerate(self.params):
                if i > 0:
                    self.file.write('\n')

                self.declare_param(param)

            self.file.write('    end-parameters\n\n')

    def declare_scalar(self, scalar: Scalar):
        """" Write a scalar declaration to the Mosel source file. """
        self.write_entity_annotations(scalar)
        mosel_type = CodeGenerator.BASIC_TYPE_NAME_MAP[scalar.dtype]
        self.file.write(f'        {validate_ident(scalar.name)}: {mosel_type}\n')

    def declare_index(self, index: IndexBase):
        """ Write an index (set) declaration to the Mosel source file. """
        self.write_entity_annotations(index)
        mosel_value_type = CodeGenerator.BASIC_TYPE_NAME_MAP[index.dtype]
        self.file.write(f'        {validate_ident(index.name)}: dynamic set of {mosel_value_type}\n')

    @staticmethod
    def get_index_set_str(index_list: Tuple[IndexBase, ...]) -> str:
        """ Generate comma-separated list of index names. """
        result = ''

        for i, index in enumerate(index_list):
            if i > 0:
                result += ', '

            result += index.name

        return result

    def declare_array(self, name: str, index: Tuple[IndexBase, ...], dtype: BASIC_TYPE):
        """ Write an array declaration to the Mosel source file. """
        array_ident = validate_ident(name)
        index_set_names_list = self.get_index_set_str(index)
        array_value_type = CodeGenerator.BASIC_TYPE_NAME_MAP[dtype]
        self.file.write(f'        {array_ident}: dynamic array({index_set_names_list}) of {array_value_type}\n')

    def declare_series(self, series: Series):
        """ Write a series (array) declaration to the Mosel source file. """
        self.write_entity_annotations(series)
        self.declare_array(series.name, series.index, series.dtype)

    def declare_data_frame(self, data_frame: DataFrameBase):
        """ Write a DataFrame (group of arrays) declaration to the Mosel source file. """
        for i, column in enumerate(data_frame.columns):
            if i > 0:
                self.file.write('\n')

            self.write_entity_annotations(column)
            self.declare_array(column.entity_name, data_frame.index, column.dtype)

    def write_declarations(self):
        """ Write the entity declarations to the Mosel source file. """
        if len(self.declared_entities) > 0:
            self.file.write('    public declarations\n')

            for i, entity in enumerate(self.declared_entities):
                if i > 0:
                    self.file.write('\n')

                if isinstance(entity, Scalar):
                    self.declare_scalar(entity)
                elif isinstance(entity, IndexBase):
                    self.declare_index(entity)
                elif isinstance(entity, Series):
                    self.declare_series(entity)
                elif isinstance(entity, DataFrameBase):
                    self.declare_data_frame(entity)
                else:
                    raise UnexpectedEntityTypeError(entity)

            self.file.write('    end-declarations\n\n')

    def write_footer(self):
        """ Write the footer to the Mosel source file. """
        slow_task_threshold_in_seconds = floor(self.app_cfg.slow_task_threshold.total_seconds())
        self.file.write(f"    setparam('slow_task_threshold', {slow_task_threshold_in_seconds})\n")
        self.file.write('\n')
        self.file.write('    runapp\n')
        self.file.write('end-model\n')

    def generate_mos(self):
        """ Write the Mosel model to the source file. """
        self.write_header()
        self.write_global_annotations()
        self.declare_parameters()
        self.write_declarations()
        self.write_footer()


def generate(app_source_dir: str, target_file: str, app_package_name: str = 'application'):
    """ Generate the Mosel model from the specified Insight app. """
    print("Python", sys.version)
    print("xpressinsight package v" + __version__)

    #
    if not os.path.isdir(os.path.dirname(target_file)):
        try:
            os.makedirs(os.path.dirname(target_file))
        except (FileExistsError, OSError):
            exit_msg(-1, f'Could not create the directory for target_file="{target_file}"')

    #
    app_cls = import_app(app_source_dir, app_package_name)
    print("Application class:", app_cls.__name__)
    print("Application name:", app_cls.get_app_cfg().name)

    #
    if os.path.isfile(os.path.join(app_source_dir, app_package_name + '._mos')):
        #
        hard_coded_template = os.path.join(app_source_dir, app_package_name + '._mos')
        print('Using hard coded template:', hard_coded_template, file=sys.stderr)
        shutil.copyfile(hard_coded_template, target_file)
    else:
        #
        with open(target_file, 'w', encoding='utf8') as file:
            CodeGenerator(app_cls, file).generate_mos()

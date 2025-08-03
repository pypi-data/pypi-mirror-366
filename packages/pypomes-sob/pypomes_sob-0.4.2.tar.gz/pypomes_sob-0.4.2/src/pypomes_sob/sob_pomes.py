from __future__ import annotations  # allow forward references
import sys
from importlib import import_module
from inspect import FrameInfo, stack
from enum import Enum
from logging import Logger
from pathlib import Path
from pypomes_core import dict_get_key, dict_stringify, exc_format
from pypomes_db import (
    DbEngine, db_exists, db_count,
    db_select, db_insert, db_update, db_delete
)
from types import ModuleType
from typing import Any, Type, TypeVar

from .sob_config import (
    SOB_BASE_FOLDER,
    sob_db_specs, sob_attrs_map,
    sob_attrs_unique, sob_cls_references
)

# 'Sob' stands for all subclasses of 'PySob'
Sob = TypeVar("Sob",
              bound="PySob")


class PySob:
    """
    Root entity.
    """

    def __init__(self,
                 errors: list[str] = None,
                 load_references: bool = False,
                 where_data: dict[str, Any] = None,
                 db_engine: DbEngine = None,
                 db_conn: Any = None,
                 logger: Logger = None) -> None:

        self._logger: Logger = logger
        # maps to the entity's PK in its DB table (returned on INSERT operations)
        self.id: int | str | None = None

        # determine whether this instance exists in the database
        self._is_new: bool = True

        if where_data:
            self.set(data=where_data)
            self.load(errors=errors,
                      omit_nulls=True,
                      db_engine=db_engine,
                      db_conn=db_conn)
        if not errors and load_references:
            self.load_references(errors=errors,
                                 db_engine=db_engine,
                                 db_conn=db_conn)

    def insert(self,
               errors: list[str] = None,
               db_engine: DbEngine = None,
               db_conn: Any = None) -> bool:

        # prepara data for INSERT
        return_col: dict[str, type] | None = None
        insert_data: dict[str, Any] = self.to_columns(omit_nulls=True)
        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        if sob_db_specs[class_name][3]:
            # PK is an identity column
            insert_data.pop(sob_db_specs[class_name][1], None)
            return_col = {sob_db_specs[class_name][1]: sob_db_specs[class_name][2]}

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # execute the INSERT statement
        rec: tuple[Any] = db_insert(errors=errors,
                                    insert_stmt=f"INSERT INTO {sob_db_specs[class_name][0]}",
                                    insert_data=insert_data,
                                    return_cols=return_col,
                                    engine=db_engine,
                                    connection=db_conn,
                                    logger=self._logger)
        if not errors:
            self._is_new = False
            if sob_db_specs[class_name][3]:
                # PK is an identity column
                self.id = rec[0]
        elif self._logger:
            self._logger.error(msg="Error INSERTing into table "
                                   f"{sob_db_specs[class_name][0]}: {'; '.join(errors)}")
        return not errors

    def update(self,
               errors: list[str] = None,
               db_engine: DbEngine = None,
               db_conn: Any = None) -> bool:

        # prepare data for UPDATE
        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        update_data: dict[str, Any] = self.to_columns(omit_nulls=False)
        key: int = update_data.pop(sob_db_specs[class_name][1])

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # execute the UPDATE statement
        db_update(errors=errors,
                  update_stmt=f"UPDATE {sob_db_specs[class_name][0]}",
                  update_data=update_data,
                  where_data={sob_db_specs[class_name][1]: key},
                  min_count=1,
                  max_count=1,
                  engine=db_engine,
                  connection=db_conn,
                  logger=self._logger)

        if errors and self._logger:
            self._logger.error(msg="Error UPDATEing table "
                                   f"{sob_db_specs[class_name][0]}: {'; '.join(errors)}")
        return not errors

    def persist(self,
                errors: list[str] = None,
                db_engine: DbEngine = None,
                db_conn: Any = None) -> bool:

        # declare the return variable
        result: bool

        if self._is_new:
            result = self.insert(errors=errors,
                                 db_engine=db_engine,
                                 db_conn=db_conn)
        else:
            result = self.update(errors=errors,
                                 db_engine=db_engine,
                                 db_conn=db_conn)
        return result

    def delete(self,
               errors: list[str] = None,
               db_engine: DbEngine = None,
               db_conn: Any = None) -> int | None:

        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        where_data: dict[str, Any]
        if self.id:
            where_data = {sob_db_specs[class_name][1]: self.id}
        else:
            where_data = self.to_columns(omit_nulls=True)
            where_data.pop(sob_db_specs[class_name][1], None)

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # execute the DELETE statement
        result: int = db_delete(errors=errors,
                                delete_stmt=f"DELETE FROM {sob_db_specs[class_name][0]}",
                                where_data=where_data,
                                max_count=1,
                                engine=db_engine,
                                connection=db_conn,
                                logger=self._logger)
        if not errors:
            self.clear()
        elif self._logger:
            self._logger.error(msg="Error DELETEing from table "
                                   f"{sob_db_specs[class_name][0]}: {'; '.join(errors)}")
        return result

    def clear(self) -> None:

        for key in self.__dict__:
            self.__dict__[key] = None

    def set(self,
            data: dict[str, Any]) -> None:

        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        for key, value in data.items():
            attr: str = (sob_attrs_map.get(class_name) or {}).get(key) or key

            # use enum names assigned as values in 'data'
            if isinstance(value, Enum) and "use_names" in value.__class__:
                value = value.name  # noqa: PLW2901

            if attr in self.__dict__:
                self.__dict__[attr] = value
            elif self._logger:
                self._logger.warning(msg=f"'{attr}'is not an attribute of "
                                         f"{sob_db_specs[class_name][0]}")

    def is_new(self) -> bool:

        return self._is_new

    def is_in_db(self,
                 errors: list[str] = None,
                 db_engine: DbEngine = None,
                 db_conn: Any = None) -> bool | None:

        # initialize the return variable
        result: bool = False

        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        where_data: dict[str, Any] | None = None
        if self.id:
            # use object's ID
            where_data = {sob_db_specs[class_name][1]: self.id}
        elif sob_attrs_unique[class_name]:
            # use first set of unique attributes with non-null values found
            for attr_set in sob_attrs_unique[class_name]:
                attrs_unique: dict[str, Any] = {}
                for attr in attr_set:
                    val: Any = self.__dict__.get(attr)
                    if val is not None:
                        attrs_unique[attr] = val
                if len(attrs_unique) == len(sob_attrs_unique[class_name]):
                    where_data = attrs_unique
                    break

        if not where_data:
            # use object's available data
            where_data = self.to_columns(omit_nulls=True)
            where_data.pop(sob_db_specs[class_name][1], None)

        if not where_data:
            result = db_exists(errors=errors,
                               table=sob_db_specs[class_name][0],
                               where_data=where_data,
                               engine=db_engine,
                               connection=db_conn,
                               logger=self._logger)
        return result

    def load(self,
             errors: list[str] = None,
             omit_nulls: bool = True,
             db_engine: DbEngine = None,
             db_conn: Any = None) -> bool:

        # initialize the return variable
        result: bool = False

        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        where_data: dict[str, Any]
        if self.id:
            where_data = {sob_db_specs[class_name][1]: self.id}
        else:
            where_data = self.to_columns(omit_nulls=omit_nulls)
            where_data.pop(sob_db_specs[class_name][1], None)

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # loading the object from the database might fail
        attrs: list[str] = self.get_columns()
        recs: list[tuple] = db_select(errors=errors,
                                      sel_stmt=f"SELECT {', '.join(attrs)} "
                                               f"FROM {sob_db_specs[class_name][0]}",
                                      where_data=where_data,
                                      limit_count=2,
                                      engine=db_engine,
                                      connection=db_conn,
                                      logger=self._logger)
        msg: str | None = None
        if errors:
            msg = ("Error SELECTing from table "
                   f"{sob_db_specs[class_name][0]}: {'; '.join(errors)}")
        elif not recs:
            msg = (f"No record found on table "
                   f"{sob_db_specs[class_name][0]} for {dict_stringify(where_data)}")
        elif len(recs) > 1:
            msg = (f"More than on record found on table "
                   f"{sob_db_specs[class_name][0]} for {dict_stringify(where_data)}")

        if msg:
            errors.append(msg)
            if self._logger:
                self._logger.error(msg=msg)
        else:
            rec: tuple = recs[0]
            for inx, attr in enumerate(attrs):
                # PK attribute in DB table might have a different name
                if attr == sob_db_specs[class_name][0]:
                    self.__dict__["id"] = rec[inx]
                else:
                    self.__dict__[attr] = rec[inx]
            self._is_new = False
            result = True

        return result

    def get_columns(self) -> list[str]:

        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        # PK attribute in DB table might have a different name
        result: list[str] = [sob_db_specs[class_name][1]]
        result.extend([k for k in self.__dict__
                      if k.islower() and not k.startswith("_") and not k == "id"])
        return result

    def to_columns(self,
                   omit_nulls: bool) -> dict[str, Any]:

        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        # PK attribute in DB table might have a different name
        result: dict[str, Any] = {sob_db_specs[class_name][1]: self.__dict__.get("id")}
        result.update({k: v for k, v in self.__dict__.items()
                      if k.islower() and not (k.startswith("_") or k == "id" or (omit_nulls and v is None))})
        return result

    def to_params(self,
                  omit_nulls: bool) -> dict[str, Any]:

        return self.data_to_params(data=self.__dict__,
                                   omit_nulls=omit_nulls)

    def data_to_params(self,
                       data: dict[str, Any],
                       omit_nulls: bool) -> dict[str, Any]:

        # initialize the return variable
        result: dict[str, Any] = {}
        
        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        for k, v in data.items():
            if not omit_nulls or v is not None:
                attr: str = dict_get_key(source=sob_attrs_map.get(class_name) or {},
                                         value=k) or k
                result[attr] = v

        return result

    # noinspection PyUnusedLocal
    def load_reference(self,
                       __cls: type[Sob],
                       /,
                       errors: list[str] = None,
                       db_engine: DbEngine = None,
                       db_conn: Any = None) -> None:

        # must be implemented by subclasses containing references
        msg: str = f"Subclass {__cls.__module__}.{__cls.__qualname__} failed to implement 'load_reference()'"
        if isinstance(errors, list):
            errors.append(msg)
        if self._logger:
            self._logger.error(msg=msg)

    def load_references(self,
                        errors: list[str] = None,
                        db_engine: DbEngine = None,
                        db_conn: Any = None) -> None:

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # traverse the references
        class_name: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        for name in (sob_cls_references.get(class_name) or []):
            # identify the reference
            pos: int = name.rfind(".")
            module_name: str = name[:pos]
            module: ModuleType = import_module(name=module_name)
            cls: type[Sob] = getattr(module,
                                     name[pos+1:])
            # load it
            self.load_reference(cls,
                                errors=errors,
                                db_engine=db_engine,
                                db_conn=db_conn)

            if errors and self._logger:
                self._logger.error(msg=f"Error SELECTing from table "
                                       f"{sob_db_specs[name][0]}: {'; '.join(errors)}")
                break

    @staticmethod
    # HAZARD:
    #   1. because 'typings.Type' has been deprecated, 'type' should be used here
    #   2. 'Sob' stands for all subclasses of 'PySob', and thus 'type[Sob]' should suffice
    #   3. PyCharm's code inspector, however, takes 'type[Sob]' to mean strict 'PySob' class
    #   4. thus, a fallback to 'Type[PySub]' was necessary
    def initialize(db_specs: tuple[str, str, int | str] |
                             tuple[str,  str, int, bool],  # noqa
                   attrs_map: dict[str, str] = None,
                   attrs_unique: list[tuple[str]] = None,
                   sob_references: list[Type[PySob]] = None,
                   logger: Logger = None) -> None:

        # obtain the invoking class
        errors: list[str] = []
        cls: type[Sob] = PySob.__get_invoking_class(errors=errors,
                                                    logger=logger)
        # initialize its data
        if cls:
            name: str = f"{cls.__module__}.{cls.__qualname__}"
            if len(db_specs) == 3:
                # 'id' defaults to being an identity attribute in the DB for type 'int'
                db_specs += (db_specs[2] is int,)
            sob_db_specs.update({name: db_specs})
            if attrs_map:
                sob_attrs_map.update({name: attrs_map})
            if attrs_unique:
                sob_attrs_unique.update({name: attrs_unique})
            if sob_references:
                ref_names: list[str] = [f"{c.__module__}.{c.__qualname__}" for c in sob_references]
                sob_cls_references.update({name: ref_names})
            if logger:
                logger.debug(msg=f"Inicialized access data for class '{name}'")

    @staticmethod
    def count(errors: list[str] = None,
              where_data: dict[str, Any] = None,
              db_engine: DbEngine = None,
              db_conn: Any = None,
              logger: Logger = None) -> int | None:

        # inicialize the return variable
        result: int | None = None

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # obtain the invoking class
        cls: type[Sob] = PySob.__get_invoking_class(errors=errors,
                                                    logger=logger)
        if not errors:
            name: str = f"{cls.__module__}.{cls.__qualname__}"
            result = db_count(errors=errors,
                              table=sob_db_specs[name][0],
                              where_data=where_data,
                              engine=db_engine,
                              connection=db_conn,
                              logger=logger)
        if errors and logger:
            logger.error(msg="; ".join(errors))

        return result

    @staticmethod
    def exists(errors: list[str] = None,
               where_data: dict[str, Any] = None,
               db_engine: DbEngine = None,
               db_conn: Any = None,
               logger: Logger = None) -> int | None:

        # inicialize the return variable
        result: bool | None = None

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # obtain the invoking class
        cls: type[Sob] = PySob.__get_invoking_class(errors=errors,
                                                    logger=logger)
        if not errors:
            name: str = f"{cls.__module__}.{cls.__qualname__}"
            result = db_exists(errors=errors,
                               table=sob_db_specs[name][0],
                               where_data=where_data,
                               engine=db_engine,
                               connection=db_conn,
                               logger=logger)
        if errors and logger:
            logger.error(msg="; ".join(errors))

        return result

    @staticmethod
    def retrieve(errors: list[str] = None,
                 load_references: bool = False,
                 table_alias: str = None,
                 table_joins: str = None,
                 where_clause: str = None,
                 where_vals: tuple = None,
                 where_data: dict[str, Any] = None,
                 orderby_clause: str = None,
                 min_count: int = None,
                 max_count: int = None,
                 offset_count: int = None,
                 limit_count: int = None,
                 db_engine: DbEngine = None,
                 db_conn: Any = None,
                 logger: Logger = None) -> list[Sob] | None:

        # inicialize the return variable
        result: list[Sob] | None = None

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # obtain the invoking class
        cls: type[Sob] = PySob.__get_invoking_class(errors=errors,
                                                    logger=logger)
        if not errors:
            name: str = f"{cls.__module__}.{cls.__qualname__}"
            sel_stmt: str = (f"SELECT {sob_db_specs[name][1]} "
                             f"FROM {sob_db_specs[name][0]}")
            if table_alias:
                sel_stmt = sel_stmt.replace("SELECT", f"SELECT {table_alias}.") + f" {table_alias}"
            if table_joins:
                sel_stmt += f" {table_joins}"
            recs: list[tuple[int | str]] = db_select(errors=errors,
                                                     sel_stmt=sel_stmt,
                                                     where_clause=where_clause,
                                                     where_vals=where_vals,
                                                     where_data=where_data,
                                                     orderby_clause=orderby_clause,
                                                     min_count=min_count,
                                                     max_count=max_count,
                                                     offset_count=offset_count,
                                                     limit_count=limit_count,
                                                     engine=db_engine,
                                                     connection=db_conn,
                                                     logger=logger)
            if not errors:
                # build the objects list
                objs: list[Sob] = []
                for rec in recs:
                    # constructor of 'cls', a subclass of 'PySob'
                    objs.append(cls(rec[0],
                                    errors=errors,
                                    load_references=load_references,
                                    db_engine=db_engine,
                                    db_conn=db_conn,
                                    logger=logger))
                    if errors:
                        break

                if not errors:
                    result = objs

        if errors and logger:
            logger.error(msg="; ".join(errors))

        return result

    @staticmethod
    def erase(errors: list[str] = None,
              where_data: dict[str, Any] = None,
              db_engine: DbEngine = None,
              db_conn: Any = None,
              logger: Logger = None) -> int | None:

        # initialize the return variable
        result: int | None = None

        # make sure to have an errors list
        if not isinstance(errors, list):
            errors = []

        # obtain the invoking class
        cls: type[Sob] = PySob.__get_invoking_class(errors=errors,
                                                    logger=logger)
        # delete specified tuples
        if not errors:
            name: str = f"{cls.__module__}.{cls.__qualname__}"
            result: int = db_delete(errors=errors,
                                    delete_stmt=f"DELETE FROM {sob_db_specs[name][0]}",
                                    where_data=where_data,
                                    engine=db_engine,
                                    connection=db_conn,
                                    logger=logger)
        if errors and logger:
            logger.error(msg="; ".join(errors))

        return result

    @staticmethod
    def __get_invoking_class(errors: list[str] | None,
                             logger: Logger | None) -> type[Sob] | None:

        # initialize the return variable
        result: type[Sob] | None = None

        # obtain the invoking function
        caller_frame: FrameInfo = stack()[1]
        invoking_function: str = caller_frame.function
        mark: str = f".{invoking_function}("

        # obtain the invoking class and its filepath
        caller_frame = stack()[2]
        context: str = caller_frame.code_context[0]
        pos_to: int = context.find(mark)
        pos_from: int = context.rfind(" ", 0, pos_to) + 1
        classname: str = context[pos_from:pos_to]
        filepath: Path = Path(caller_frame.filename)
        mark = "." + classname

        for name in sob_db_specs:
            if name.endswith(mark):
                try:
                    pos: int = name.rfind(".")
                    module_name: str = name[:pos]
                    module: ModuleType = import_module(name=module_name)
                    result = getattr(module,
                                     classname)
                except Exception as e:
                    if logger:
                        msg: str = exc_format(exc=e,
                                              exc_info=sys.exc_info())
                        logger.warning(msg=msg)
                break

        if not result and SOB_BASE_FOLDER:
            try:
                pos: int = filepath.parts.index(SOB_BASE_FOLDER)
                module_name: str = Path(*filepath.parts[pos:]).as_posix()[:-3].replace("/", ".")
                module: ModuleType = import_module(name=module_name)
                result = getattr(module,
                                 classname)
            except Exception as e:
                if logger:
                    msg: str = exc_format(exc=e,
                                          exc_info=sys.exc_info())
                    logger.warning(msg=msg)

        if not result:
            msg: str = (f"Unable to obtain class '{classname}', "
                        f"filepath '{filepath}', "f"from invoking function '{invoking_function}'")
            if logger:
                logger.error(msg=f"{msg} - invocation frame {caller_frame}")
            if isinstance(errors, list):
                errors.append(msg)

        return result

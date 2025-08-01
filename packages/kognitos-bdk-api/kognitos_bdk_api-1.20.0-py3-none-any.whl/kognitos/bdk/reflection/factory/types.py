import importlib
import inspect
import sys
import uuid
from dataclasses import MISSING, fields, is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum, EnumMeta
from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from types import NoneType, UnionType
from typing import (IO, Any, ForwardRef, List, Optional, Tuple, Union,
                    get_origin)

from ...api.noun_phrase import NounPhrase
from ...docstring import DocstringParser
from ...typing import Sensitive
from ..types import ConceptTableType
from ..types.any import ConceptAnyType
from ..types.base import ConceptType
from ..types.dict import ConceptDictionaryType, ConceptDictionaryTypeField
from ..types.enum import ConceptEnumType, ConceptEnumTypeMember
from ..types.list import ConceptListType
from ..types.opaque import ConceptOpaqueType
from ..types.optional import ConceptOptionalType
from ..types.scalar import ConceptScalarType
from ..types.self import ConceptSelfType
from ..types.sensitive import ConceptSensitiveType
from ..types.union import ConceptUnionType


@lru_cache
def is_attrs_installed():
    try:
        importlib.metadata.distribution("attrs")
        return True
    except PackageNotFoundError:
        return False


@lru_cache
def is_pyarrow_installed():
    try:
        importlib.metadata.distribution("pyarrow")
        return True
    except PackageNotFoundError:
        return False


@lru_cache
def is_arro3_installed():
    try:
        importlib.metadata.distribution("arro3.core")
        return True
    except PackageNotFoundError:
        return False


@lru_cache
def is_nanoarrow_installed():
    try:
        importlib.metadata.distribution("nanoarrow")
        return True
    except PackageNotFoundError:
        return False


if is_attrs_installed():
    from .attrs_utils import from_attrs, is_attrs


if is_pyarrow_installed():
    from pyarrow import Table as PyArrowTable
else:
    PyArrowTable = None

if is_arro3_installed():
    from arro3.core import \
        Table as Arro3Table  # pylint: disable=no-name-in-module
else:
    Arro3Table = None

if is_nanoarrow_installed():
    from nanoarrow import ArrayStream as NanoArrowArrayStream
else:
    NanoArrowArrayStream = None


def should_translate_to_optional(annotation: type, unset: Optional[Any] = None):
    if not get_origin(annotation) in (Union, UnionType):
        return False
    unset_types = [NoneType] if unset is None else [NoneType, unset.__class__]
    unset_types_present = list(map(lambda t: t in unset_types, annotation.__args__)).count(True)
    return unset_types_present >= 1


def get_truthy_types(annotation: type, unset: Optional[Any]) -> List[Any]:
    unset_types = [NoneType] if unset is None else [NoneType, unset.__class__]
    return [t for t in annotation.__args__ if t not in unset_types]


class ConceptTypeFactory:

    @classmethod
    def from_type(cls, annotation: type, backward: Optional[List[str]] = None, unset: Optional[Any] = None) -> ConceptType:
        from ...api.questions import Question  # pylint: disable=cyclic-import

        if getattr(getattr(annotation, "__origin__", None), "__name__", None) == "Question":
            raise ValueError(
                "Questions cannot be used as a concept type. If you are type-hinting a procedure to indicate that it can return a question, use a union type at the top level of the return type-hint. If the procedure can return a question, but has no results, use 'None | Question' as the return type-hint."
            )

        if annotation is Question:
            raise ValueError("Question typehints must be parameterized: Question[Literal['noun phrase'], type]")

        if backward is None:
            backward = []

        if isinstance(annotation, EnumMeta):
            is_a = set(getattr(annotation, "__is_a__", []))

            docstring = DocstringParser.parse(annotation.__doc__ or "")

            keys = sorted(list(annotation.__members__.keys()))
            resolved_members = [docstring.enum_member_by_name(key) for key in keys]

            members = [ConceptEnumTypeMember(member.name, member.description, member.noun_phrase) for member in resolved_members]

            return ConceptEnumType(is_a=is_a, members=members, description=docstring.short_description or docstring.long_description, concrete=annotation)

        if annotation == str:
            return ConceptScalarType.TEXT
        if annotation in (int, float, Decimal):
            return ConceptScalarType.NUMBER
        if annotation == bool:
            return ConceptScalarType.BOOLEAN
        if annotation == datetime:
            return ConceptScalarType.DATETIME
        if annotation == date:
            return ConceptScalarType.DATE
        if annotation == time:
            return ConceptScalarType.TIME
        if annotation == uuid.UUID:
            return ConceptScalarType.UUID
        if should_translate_to_optional(annotation, unset):
            truthy_types = get_truthy_types(annotation, unset)
            if len(truthy_types) == 1:
                return ConceptOptionalType(ConceptTypeFactory.from_type(truthy_types[0], backward, unset)).simplify()

            inner_types = [ConceptTypeFactory.from_type(t, backward, unset) for t in truthy_types]
            return ConceptOptionalType(ConceptUnionType(inner_types)).simplify()
        if get_origin(annotation) == Sensitive:
            return ConceptSensitiveType(ConceptTypeFactory.from_type(annotation.__args__[0], backward, unset)).simplify()
        if get_origin(annotation) == list:
            return ConceptListType(ConceptTypeFactory.from_type(annotation.__args__[0], backward, unset)).simplify()
        if get_origin(annotation) in (Union, UnionType):
            inner_types = [ConceptTypeFactory.from_type(arg, backward, unset) for arg in annotation.__args__]
            return ConceptUnionType(inner_types).simplify()
        if get_origin(annotation) == IO or (inspect.isclass(annotation) and issubclass(annotation, IO)):
            return ConceptScalarType.FILE
        if annotation == NounPhrase:
            return ConceptScalarType.CONCEPTUAL
        if annotation == Any:
            return ConceptAnyType()
        if inspect.isclass(annotation) and issubclass(annotation, Enum):
            return ConceptTypeFactory.from_type(type(next(iter(annotation)).value), unset=unset)
        if isinstance(annotation, ForwardRef):
            if annotation.__forward_arg__ in backward:
                return ConceptSelfType()

            globalns, localns = collect_namespaces()
            resolved = annotation._evaluate(globalns, localns, recursive_guard=set())

            return ConceptTypeFactory.from_type(resolved, backward + [annotation.__forward_arg__], unset=unset).simplify()

        if is_dataclass(annotation):
            return from_dataclass(annotation, unset)

        if is_attrs_installed():
            if is_attrs(annotation):  # pyright: ignore [reportPossiblyUnboundVariable]
                return from_attrs(annotation, cls, unset)  # pyright: ignore [reportPossiblyUnboundVariable]

        if is_pyarrow_installed():
            if PyArrowTable and annotation == PyArrowTable:
                return ConceptTableType(None, [], PyArrowTable)

        if is_arro3_installed():
            if Arro3Table and annotation == Arro3Table:
                return ConceptTableType(None, [], Arro3Table)

        if is_nanoarrow_installed():
            if NanoArrowArrayStream and annotation == NanoArrowArrayStream:
                return ConceptTableType(None, [], NanoArrowArrayStream)

        if hasattr(annotation, "__is_a__"):
            return from_serializable(annotation)

        if get_origin(annotation) == dict:
            return ConceptDictionaryType(set(), None, None, [])

        return ConceptOpaqueType({NounPhrase.from_head("thing")}, None, annotation)


def compute_default_value(field: Any) -> Tuple[bool, Any]:
    if field.default is not MISSING:
        return True, field.default

    if field.default_factory is not MISSING:
        return True, field.default_factory()

    return False, None


def from_dataclass(annotation, unset: Optional[Any] = None):
    docstring = DocstringParser.parse(annotation.__doc__)
    unset = getattr(annotation, "__unset__", unset)
    dict_fields = []

    for field in fields(annotation):
        description: Optional[str] = next((attribute.description for attribute in docstring.attributes if attribute.name == field.name), None)

        has_default_value, default_value = compute_default_value(field)

        if field.init is False:
            concept_type = ConceptTypeFactory.from_type(Optional[field.type], unset=unset)  # type: ignore
        else:
            concept_type = ConceptTypeFactory.from_type(field.type, unset=unset)  # type: ignore

        dict_fields.append(ConceptDictionaryTypeField(field.name, description, concept_type, default_value=default_value, has_default_value=has_default_value, init=field.init))

    return ConceptDictionaryType(
        set(getattr(annotation, "__is_a__", [])),
        annotation,
        (
            (docstring.short_description or "") + (docstring.long_description or "")
            if docstring.short_description and docstring.long_description
            else docstring.short_description or docstring.long_description or ""
        ),
        dict_fields,
        unset=unset,
    )


def from_serializable(annotation):
    docstring = DocstringParser.parse(annotation.__doc__)

    return ConceptOpaqueType(
        set(getattr(annotation, "__is_a__")),
        (
            (docstring.short_description or "") + (docstring.long_description or "")
            if docstring.short_description and docstring.long_description
            else docstring.short_description or docstring.long_description or ""
        ),
        annotation,
    )


def collect_namespaces():
    globalns = {}
    localns = {}

    frame = sys._getframe()
    while frame:
        globalns.update(frame.f_globals)
        localns.update(frame.f_locals)
        frame = frame.f_back

    return globalns, localns

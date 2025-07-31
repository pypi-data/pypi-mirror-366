from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, List, Literal, Optional, Sequence, TypeVar, Union

import scale_sensor_fusion_io as sfio
from typing_extensions import TypeAlias

PathField: TypeAlias = Union[int, str]
PathInput: TypeAlias = Union[PathField, List[PathField]]

T = TypeVar("T")


@dataclass
class ParseSuccess(Generic[T]):
    data: T
    success: Literal[True] = True


@dataclass
class ErrorDetails:
    path: List[PathField]
    errors: List[str]

    def __repr__(self) -> str:
        return f"{{ path: '{'.'.join([str(p) for p in self.path])}', errors: {self.errors} }}"

    @staticmethod
    def from_msg(msg: str, path: Optional[PathInput] = None) -> ErrorDetails:
        """
        Helper function to initiate a ErrorDetails from a single error message to reduce boilerplate
        """
        return ErrorDetails(
            path=(path if type(path) is list else [path]) if path else [], errors=[msg]  # type: ignore
        )

    @staticmethod
    def missing_field(field: str, path: Optional[PathInput] = None) -> ErrorDetails:
        """
        Helper function to template out details for missing field
        """
        return ErrorDetails(
            path=(path if type(path) is list else [path]) if path else [],  # type: ignore
            errors=[f"Missing field: {field}"],
        )


@dataclass
class DataValidationError(Exception):
    details: List[ErrorDetails]

    @staticmethod
    def from_msg(msg: str, path: Optional[PathInput] = None) -> DataValidationError:
        """
        Helper function to initiate a DataValidationError from a single error message to reduce boilerplate
        """
        return DataValidationError(details=[ErrorDetails.from_msg(msg, path)])

    def prepend_path(self, path: List[PathField]) -> DataValidationError:
        """Prepend path of error with additional prefix"""
        for err in self.details:
            err.path = path + err.path
        return self


@dataclass
class ParseError(DataValidationError):
    details: List[ErrorDetails]
    success: Literal[False] = False

    @staticmethod
    def from_msg(msg: str, path: Optional[PathInput] = None) -> ParseError:
        """
        Helper function to initiate a ParseError from a single error message to reduce boilerplate
        """
        return ParseError(details=[ErrorDetails.from_msg(msg, path)])

    @staticmethod
    def missing_field(field: str, path: Optional[PathInput] = None) -> ParseError:
        """
        Helper function to template out details for missing field
        """
        return ParseError(details=[ErrorDetails.missing_field(field, path)])


ParseResult: TypeAlias = Union[ParseSuccess[T], ParseError]

ValidationResult: TypeAlias = Optional[DataValidationError]

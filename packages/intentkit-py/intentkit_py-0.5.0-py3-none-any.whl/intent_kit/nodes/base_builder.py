"""
Base builder class for creating intent graph nodes.

This module provides a base class that all specific builders inherit from,
ensuring consistent patterns and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic
from intent_kit.utils.logger import Logger

T = TypeVar("T")


class BaseBuilder(ABC, Generic[T]):
    """Base class for all node builders.

    This class provides common functionality and enforces consistent patterns
    across all builder implementations.
    """

    logger: Logger

    def __init__(self, name: str):
        """Initialize the base builder.

        Args:
            name: Name of the node to be created
        """
        self.name = name
        self.description = ""
        self.logger = Logger(name or self.__class__.__name__.lower())

    def with_description(self, description: str) -> "BaseBuilder[T]":
        """Set the description for the node.

        Args:
            description: Description of what this node does

        Returns:
            Self for method chaining
        """
        self.description = description
        return self

    @abstractmethod
    def build(self) -> T:
        """Build and return the node instance.

        Returns:
            Configured node instance

        Raises:
            ValueError: If required fields are missing
        """
        pass

    def _validate_required_field(
        self, field_name: str, field_value: Any, method_name: str
    ) -> None:
        """Validate that a required field is set.

        Args:
            field_name: Name of the field being validated
            field_value: Value of the field
            method_name: Name of the method that should be called to set the field

        Raises:
            ValueError: If the field is not set
        """
        if field_value is None:
            raise ValueError(
                f"{field_name} must be set. Call .{method_name}() before .build()"
            )

    def _validate_required_fields(self, validations: list) -> None:
        """Validate multiple required fields.

        Args:
            validations: List of tuples (field_name, field_value, method_name)

        Raises:
            ValueError: If any required field is not set
        """
        for field_name, field_value, method_name in validations:
            self._validate_required_field(field_name, field_value, method_name)

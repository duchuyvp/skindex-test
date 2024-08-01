from __future__ import annotations

from typing import Any, override


class UnitTestState:
    """TestState."""

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        responses: dict[str, Any] | None = None,
        messages: dict[str, Any] | None = None,
    ):
        super().__init__()

        self.data = data if data is not None else {}
        self.responses = responses if responses is not None else {}
        self.messages = messages if messages is not None else {}

    def __add__(self, other: UnitTestState) -> UnitTestState:
        """__add__.

        Args:
            other (TestState): other

        Returns:
            TestState:
        """
        state = UnitTestState(
            data=self.data | other.data,
            responses=self.responses | other.responses,
            messages=self.messages | other.messages,
        )
        return state

    def __iadd__(self, other: UnitTestState) -> UnitTestState:
        """__iadd__.

        Args:
            other (TestState): other

        Returns:
            TestState:
        """
        self.data = self.data | other.data
        self.responses = self.responses | other.responses
        self.messages = self.messages | other.messages
        return self

    @override
    def __eq__(self, other: object) -> bool:
        """__eq__.

        Args:
            other (TestState): other

        Returns:
            bool:
        """
        assert isinstance(other, UnitTestState)

        return (
            self.data == other.data
            and self.responses == other.responses
            and self.messages == other.messages
        )

    @override
    def __str__(self) -> str:
        """__str__.

        Args:

        Returns:
            str:
        """
        return f"TestState(\n\tdata={self.data},\n\tresponses={self.responses},\n\tmessages={self.messages}\n)"

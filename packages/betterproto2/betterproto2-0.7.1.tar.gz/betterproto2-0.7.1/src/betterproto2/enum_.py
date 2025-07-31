import sys
from enum import EnumMeta, IntEnum

from typing_extensions import Self


class _EnumMeta(EnumMeta):
    def __new__(metacls, cls, bases, classdict):
        # Find the proto names if defined
        if sys.version_info >= (3, 11):
            proto_names = classdict.pop("betterproto_proto_names", {})
            classdict._member_names.pop("betterproto_proto_names", None)
        else:
            proto_names = {}
            if "betterproto_proto_names" in classdict:
                proto_names = classdict.pop("betterproto_proto_names")
                classdict._member_names.remove("betterproto_proto_names")

        enum_class = super().__new__(metacls, cls, bases, classdict)

        # Attach extra info to each enum member
        for member in enum_class:
            value = member.value  # type: ignore[reportAttributeAccessIssue]
            extra = proto_names.get(value)
            member._proto_name = extra  # type: ignore[reportAttributeAccessIssue]

        return enum_class


class Enum(IntEnum, metaclass=_EnumMeta):
    @property
    def proto_name(self) -> str | None:
        return self._proto_name  # type: ignore[reportAttributeAccessIssue]

    @classmethod
    def _missing_(cls, value):
        # If the given value is not an integer, let the standard enum implementation raise an error
        if not isinstance(value, int):
            return

        # Create a new "unknown" instance with the given value.
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._name_ = ""
        return obj

    def __str__(self):
        if not self.name:
            return f"UNKNOWN({self.value})"
        return self.name

    def __repr__(self):
        if not self.name:
            return f"<{self.__class__.__name__}.~UNKNOWN: {self.value}>"
        return super().__repr__()

    @classmethod
    def from_string(cls, name: str) -> Self:
        """Return the value which corresponds to the string name.

        Parameters:
            name: The name of the enum member to get.

        Raises:
            ValueError: The member was not found in the Enum.

        Returns:
            The corresponding value
        """
        try:
            return cls[name]
        except KeyError as e:
            raise ValueError(f"Unknown value {name} for enum {cls.__name__}") from e

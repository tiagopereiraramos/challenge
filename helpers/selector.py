import dataclasses
from dataclasses import dataclass, field


@dataclass
class Selector:
    # Helper to make it easier to pass around selectors and reduce number of args in each function
    css: str = ""
    xpath: str = ""
    text: str = ""
    attr: tuple = field(default_factory=tuple)

    def __str__(self):
        """Returns a string containing only the non-default field values."""
        s = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in dataclasses.fields(self)
            if getattr(self, field.name)
        )
        return f"{type(self).__name__}({s})"


@dataclass
class TagAttVl:
    # Helper to make it easier to pass around selectors and reduce number of args in each function
    tag: str = ""
    attr: str = ""
    vlr: str = ""

    def __str__(self):
        """Returns a string containing only the non-default field values."""
        s = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in dataclasses.fields(self)
            if getattr(self, field.name)
        )
        return f"{type(self).__name__}({s})"

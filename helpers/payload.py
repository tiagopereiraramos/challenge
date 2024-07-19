import dataclasses
from dataclasses import dataclass, field


@dataclass
class Payload:
    phrase_test: str
    section: str
    data_range: int
    sort_by: int
    results:int

    def __str__(self):
        """Returns a string containing only the non-default field values."""
        s = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in dataclasses.fields(self)
            if getattr(self, field.name)
        )
        return f"{type(self).__name__}({s})"

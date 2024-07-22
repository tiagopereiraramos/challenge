import dataclasses
from dataclasses import dataclass, field
from Log.logs import Logs

@dataclass
class Payload:
    phrase_test: str = ''
    section: str = ''
    sort_by: int = ''
    results: int = 0


    def to_dict(self):
        return {
            "phrase_test": self.phrase_test,
            "section": self.section,
            "sort_by": self.sort_by,
            "results": self.results
        }
    
    def __str__(self):
        """Returns a string containing only the non-default field values."""
        s = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in dataclasses.fields(self)
            if getattr(self, field.name)
        )
        return f"{type(self).__name__}({s})"

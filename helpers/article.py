import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    title: str = ""
    date: datetime = ""
    description: str = ""
    picture_filename: str = ""
    picture_local_path: str = ""
    title_count_phrase: int = 0
    description_count_phrase: int = 0
    find_money_title_description: bool = False

    def to_dict(self):
        formatted_date = self.date.isoformat() if self.date else ""

        return {
            "title": self.title,
            "date": formatted_date,
            "description": self.description,
            "picture_filename": self.picture_filename,
            "picture_local_path": self.picture_local_path,
            "title_count_phrase": self.title_count_phrase,
            "description_count_phrase": self.description_count_phrase,
            "find_money_title_description": self.find_money_title_description,
        }

    @staticmethod
    def articles_to_json(articles):
        return json.dumps([article.to_dict() for article in articles], indent=4)

    def __str__(self):
        """Returns a string containing only the non-default field values."""
        s = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in dataclasses.fields(self)
            if getattr(self, field.name)
        )
        return f"{type(self).__name__}({s})"

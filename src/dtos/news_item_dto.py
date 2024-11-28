import re
from dataclasses import dataclass
from datetime import date


@dataclass
class NewsItemDto:
    title: str
    description: str
    date: date
    image_name: str

    def phrase_count_in_title_and_description(self, phrase: str) -> int:
        return self.title.lower().count(
            phrase.lower()
        ) + self.description.lower().count(phrase.lower())

    def title_or_description_contains_money(self) -> bool:
        regex = (
            r"\$\d{1,3}(,\d{3})*(\.\d{1,2})?|\d{1,3}(,\d{3})*(\.\d{1,2})?"
            r"\s*dollars|\d{1,3}(,\d{3})*(\.\d{1,2})?\s*usd"
        )
        pattern = re.compile(regex)
        return bool(pattern.search(self.title)) or bool(
            pattern.search(self.description)
        )

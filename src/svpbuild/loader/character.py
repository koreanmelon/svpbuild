import logging
from collections.abc import Iterable
from pathlib import Path

from svpbuild.loader.types import CharacterAsset, PortraitAsset

RESERVED_VALUES = {
    "Monday": ("DayOfWeek", "Monday"),
    "Tuesday": ("DayOfWeek", "Tuesday"),
    "Wednesday": ("DayOfWeek", "Wednesday"),
    "Thursday": ("DayOfWeek", "Thursday"),
    "Friday": ("DayOfWeek", "Friday"),
    "Saturday": ("DayOfWeek", "Saturday"),
    "Sunday": ("DayOfWeek", "Sunday"),
    "Spring": ("Season", "Spring"),
    "Summer": ("Season", "Summer"),
    "Fall": ("Season", "Fall"),
    "Winter": ("Season", "Winter"),
    "Sun": ("Weather", "Sun"),
    "Rain": ("Weather", "Rain"),
    "Storm": ("Weather", "Storm"),
    "GreenRain": ("Weather", "GreenRain"),
    "Snow": ("Weather", "Snow"),
    "Wind": ("Weather", "Wind"),
    "Indoor": ("IsOutdoors", False),
    "Outdoor": ("IsOutdoors", True),
}

KNOWN_TOKENS = {
    "Day",
    "DayEvent",
    "DayOfWeek",
    "Season",
    "Weather",
    "IsOutdoors",
    "LocationContext",
    "LocationName",
}


class CharacterLoader:
    def __init__(self, root: Path) -> None:
        self.root: Path = root
        self.characters: dict[str, CharacterAsset] = {}

        self._load_all(root)

    def _parse_filename(self, filename: str) -> tuple[str, str, dict[str, str | int | bool]]:
        """
        Parses a portrait asset filename based on the required naming convention.
        """
        name = Path(filename).stem
        parts = name.split("-")

        char_name = parts[0]
        variant_parts = []
        conditions = {}

        i = 1
        while i < len(parts):
            part = parts[i]
            if part in RESERVED_VALUES:
                k, v = RESERVED_VALUES[part]
                conditions[k] = v
            elif part in KNOWN_TOKENS:
                if i + 1 < len(parts):
                    val = parts[i + 1]
                    if val.lower() == "true":
                        conditions[part] = True
                    elif val.lower() == "false":
                        conditions[part] = False
                    elif val.isdigit():
                        if val.startswith("0") and len(val) > 1:
                            conditions[part] = val
                        else:
                            conditions[part] = int(val)
                    else:
                        conditions[part] = val
                    i += 1
                else:
                    variant_parts.append(part)
            else:
                variant_parts.append(part)
            i += 1

        variant = " ".join(variant_parts).replace("_", " ") if variant_parts else "Standard"
        return char_name, variant, conditions

    def _load_all(self, directory: Path):
        for file in sorted(
            directory.rglob("*.png"), key=lambda item: item.relative_to(directory).as_posix()
        ):
            if file.is_file():
                self._load_one(file)

    def _load_one(self, file: Path):
        if not file.is_file():
            return

        name, variant, conditions = self._parse_filename(file.name)

        rel_path = file.relative_to(self.root).as_posix()
        self.characters.setdefault(name, CharacterAsset(name=name))
        self.characters[name].portraits.append(
            PortraitAsset(variant=variant, conditions=conditions, path=rel_path)
        )
        logging.debug(
            "Parsed '%s' -> Character: %s | Variant: %s | Conditions: %s",
            file.name,
            name,
            variant,
            conditions,
        )

    def get_names(self) -> Iterable[str]:
        return sorted(self.characters.keys())

    def get_characters(self) -> Iterable[CharacterAsset]:
        return [self.characters[name] for name in self.get_names()]

    def get_character(self, name: str) -> CharacterAsset:
        return self.characters[name]

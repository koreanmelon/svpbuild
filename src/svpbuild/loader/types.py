from dataclasses import dataclass, field


@dataclass
class PortraitAsset:
    """
    Represents an individual portrait file.

    Attributes:
        variant: The variant name (e.g., 'Standard', 'Beach').
        conditions: Content Patcher condition keys and values.
        path: The relative path to the image file.
    """

    path: str
    variant: str
    conditions: dict[str, str | int | bool] = field(default_factory=dict)


@dataclass
class CharacterAsset:
    """
    Represents a character's portrait assets discovered on disk.

    Attributes:
        name: The name of the character (e.g., 'Harvey').
        portraits: A list of PortraitAsset objects.
    """

    name: str
    portraits: list[PortraitAsset] = field(default_factory=list)

    @property
    def variants(self) -> list[str]:
        """Returns sorted unique variants associated with this character."""
        return sorted({portrait.variant for portrait in self.portraits})

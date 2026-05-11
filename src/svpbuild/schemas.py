"""
Defines the JSON schema structures used by SMAPI and Content Patcher.

These TypedDicts ensure type safety when generating the final manifest.json
and content.json files for Stardew Valley mods.

References:
- SMAPI Manifest: https://smapi.io/schemas/manifest.json
- Content Patcher: https://smapi.io/schemas/content-patcher.json
"""

from typing import TypedDict

try:
    from typing import NotRequired
except ImportError:  # Python 3.10
    from typing_extensions import NotRequired

CP_FORMAT_VERSION = "2.9.0"


class SMAPIDependency(TypedDict):
    """Represents a single mod dependency in a SMAPI manifest.json."""

    UniqueID: str
    MinimumVersion: NotRequired[str]
    IsRequired: NotRequired[bool]


class SMAPIContentPackFor(TypedDict):
    """Specifies the mod which can read this content pack."""

    UniqueID: str
    MinimumVersion: NotRequired[str]


class SMAPIManifestBase(TypedDict):
    pass


SMAPIManifestSchema = TypedDict("SMAPIManifestSchema", {"$schema": NotRequired[str]})


class SMAPIManifest(SMAPIManifestSchema):
    """Represents the complete structure of a SMAPI manifest.json file."""

    Name: str
    Author: str
    Version: str
    Description: str
    UniqueID: str
    EntryDll: NotRequired[str]
    ContentPackFor: NotRequired[SMAPIContentPackFor]
    MinimumApiVersion: NotRequired[str]
    MinimumGameVersion: NotRequired[str]
    Dependencies: NotRequired[list[SMAPIDependency]]
    UpdateKeys: NotRequired[list[str]]


class CPContentConfigSchemaEntry(TypedDict):
    """Represents a single configuration option in a Content Patcher content.json ConfigSchema."""

    AllowValues: NotRequired[str]
    AllowBlank: NotRequired[bool]
    AllowMultiple: NotRequired[bool]
    Default: NotRequired[str | bool | int | float]
    Description: NotRequired[str]
    Section: NotRequired[str]


class CPContentRectangle(TypedDict):
    """Represents a spatial area definition for image or map patching."""

    X: int | str
    Y: int | str
    Width: int | str
    Height: int | str


class CPContentChange(TypedDict):
    """Represents a single dynamic action/patch in a Content Patcher content.json Changes list."""

    Action: str
    Target: NotRequired[str]
    TargetLocale: NotRequired[str]
    LogName: NotRequired[str]
    Update: NotRequired[str]
    LocalTokens: NotRequired[dict[str, str | int | bool | float]]
    FromFile: NotRequired[str]
    FromArea: NotRequired[CPContentRectangle]
    ToArea: NotRequired[CPContentRectangle]
    PatchMode: NotRequired[str]
    Priority: NotRequired[str]
    TargetField: NotRequired[list[str]]
    Fields: NotRequired[dict[str, dict]]
    Entries: NotRequired[dict[str, str | int | bool | float | None] | None]
    MoveEntries: NotRequired[list[dict]]
    AddWarps: NotRequired[list[str]]
    AddNpcWarps: NotRequired[list[str]]
    MapProperties: NotRequired[dict[str, str | None]]
    MapTiles: NotRequired[list[dict]]
    TextOperations: NotRequired[list[dict]]
    When: NotRequired[dict[str, str | int | bool]]


CPContentSpecSchema = TypedDict("CPContentSpecSchema", {"$schema": NotRequired[str]})


class CPContentSpec(CPContentSpecSchema):
    """Represents the complete structure of a Content Patcher content.json file."""

    Format: str
    Changes: list[CPContentChange]
    ConfigSchema: NotRequired[dict[str, CPContentConfigSchemaEntry]]
    CustomLocations: NotRequired[list[dict]]
    DynamicTokens: NotRequired[list[dict]]
    AliasTokenNames: NotRequired[dict[str, str]]

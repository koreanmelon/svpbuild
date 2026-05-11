from svpbuild.loader.loader import Loader


def test_loader_discovery(sample_pack_dir):
    loader = Loader(sample_pack_dir)

    # Verify manifest loaded
    assert loader.manifest["UniqueID"] == "Test.SamplePortraits"

    # Verify character loaded
    assert "Abigail" in loader.characters.get_names()
    assert "Sebastian" in loader.characters.get_names()

    # Check Abigail's variants
    abigail = loader.characters.get_character("Abigail")
    assert "Standard" in abigail.variants
    assert abigail.variants == ["Beach Party Outfit", "Standard"]

    # Find specific portraits to verify parsing
    beach_summer = next(
        (
            p
            for p in abigail.portraits
            if p.variant == "Beach Party Outfit" and p.conditions.get("Season") == "Summer"
        ),
        None,
    )
    assert beach_summer is not None
    assert beach_summer.path == "Abigail/Abigail-Beach_Party-Outfit-Summer.png"

    spring_standard = next(
        (
            p
            for p in abigail.portraits
            if p.variant == "Standard" and p.conditions.get("Season") == "Spring"
        ),
        None,
    )
    assert spring_standard is not None
    assert spring_standard.path == "Abigail/Abigail-Spring.png"

    outdoors_standard = next(
        (
            p
            for p in abigail.portraits
            if p.variant == "Standard" and p.conditions.get("IsOutdoors") is True
        ),
        None,
    )
    assert outdoors_standard is not None
    assert outdoors_standard.path == "Abigail/Abigail-Outdoor.png"

    indoors_standard = next(
        (
            p
            for p in abigail.portraits
            if p.variant == "Standard" and p.conditions.get("IsOutdoors") is False
        ),
        None,
    )
    assert indoors_standard is not None
    assert indoors_standard.path == "Abigail/Abigail-Indoor.png"

    # Check Sebastian's complex parsing fallback
    sebastian = loader.characters.get_character("Sebastian")
    assert "Goth" in sebastian.variants

    goth_saloon = next((p for p in sebastian.portraits if p.variant == "Goth"), None)
    assert goth_saloon is not None
    assert goth_saloon.conditions.get("LocationName") == "Saloon"
    assert goth_saloon.path == "Sebastian/Sebastian-Goth-LocationName-Saloon.png"


def test_loader_orders_characters_and_variants(sample_pack_dir):
    loader = Loader(sample_pack_dir)

    assert list(loader.characters.get_names()) == ["Abigail", "Sebastian"]
    assert [character.name for character in loader.characters.get_characters()] == [
        "Abigail",
        "Sebastian",
    ]

    content = loader.build_content()
    assert list(content["ConfigSchema"]) == ["Abigail", "Sebastian"]
    assert content["ConfigSchema"]["Abigail"]["AllowValues"] == "Beach Party Outfit, Standard"


def test_loader_build_content(sample_pack_dir):
    loader = Loader(sample_pack_dir)
    content = loader.build_content()

    # Verify changes array exists
    changes = content["Changes"]
    assert len(changes) > 0

    # Check that Abigail's Beach Party Outfit variant with Summer condition generated correctly
    abigail_beach_summer_patch = next(
        (
            c
            for c in changes
            if c.get("Target") == "Portraits/Abigail"
            and c.get("When", {}).get("Season") == "Summer"
        ),
        None,
    )

    assert abigail_beach_summer_patch is not None
    assert abigail_beach_summer_patch["Action"] == "EditImage"
    assert (
        abigail_beach_summer_patch.get("FromFile")
        == "assets/Abigail/Abigail-Beach_Party-Outfit-Summer.png"
    )
    # Ensure BOTH conditions are present in the 'When' block
    assert abigail_beach_summer_patch.get("When", {}).get("Abigail") == "Beach Party Outfit"
    assert abigail_beach_summer_patch.get("When", {}).get("Season") == "Summer"

    # Check that Abigail's IsOutdoors variant generated correctly
    abigail_outdoors_patch = next(
        (
            c
            for c in changes
            if c.get("Target") == "Portraits/Abigail"
            and c.get("When", {}).get("IsOutdoors") is True
        ),
        None,
    )

    assert abigail_outdoors_patch is not None
    assert abigail_outdoors_patch["Action"] == "EditImage"
    assert abigail_outdoors_patch.get("FromFile") == "assets/Abigail/Abigail-Outdoor.png"
    assert abigail_outdoors_patch.get("When", {}).get("Abigail") == "Standard"
    assert abigail_outdoors_patch.get("When", {}).get("IsOutdoors") is True

# test_template_resolving.py
import os
import pytest
from template_loader import TemplateLoader
from resolver import PathResolver

# This is a test file for the PathResolver class
# It tests the path resolution functionality using various templates and contexts.

# This is the base directory for the test files
# It is used to load the YAML templates for testing.
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture
def loader():

    return TemplateLoader([
        os.path.join(base_dir, "templates/base.yaml"),
        os.path.join(base_dir, "templates/assets.yaml"),
        os.path.join(base_dir, "templates/shots.yaml")
    ])

@pytest.fixture
def resolver(loader):
    resolver = PathResolver(loader=loader)
    return resolver

@pytest.fixture
def common_context():
    return {
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ001",
        "shot": "SH010",
        "task": "comp",
        "version": "004",
        "ext": "nk"
    }

@pytest.mark.parametrize("template_name,context,expected", [
    ("shot_workfile", {
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ001",
        "shot": "SH010",
        "task": "comp",
        "version": "004",
        "ext": "nk"
    }, "Z:/projects/dragonfire/sequences/SQ001/SH010/work/comp/SH010_comp_v004.nk"),
    ("asset_publish", {
        "root": "Z:/projects",
        "project": "dragonfire",
        "asset_type": "char",
        "asset_name": "orc",
        "task": "model",
        "version": "002"
    }, "Z:/projects/dragonfire/assets/char/orc/publish/model/orc_model_v002.abc"),
    ("render_frames", {
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ002",
        "shot": "SH020",
        "task": "lighting",
        "version": "001",
        "frame": "1001",
        "ext": "exr"
    }, "Z:/projects/dragonfire/sequences/SQ002/SH020/render/lighting/SH020_lighting_v001/SH020_lighting_v001.1001.exr"),
    ("render_frames", {
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ001",
        "shot": "SH010",
        "task": "comp",
        "version": "004",
        "ext": "exr"
    }, "Z:/projects/dragonfire/sequences/SQ001/SH010/render/comp/SH010_comp_v004.####.exr")

])

def test_path_resolver(resolver, template_name, context, expected):
    """
    Test the path resolution functionality of the PathResolver class.
    """
    resolved_path = resolver.resolve(template_name, context)
    assert resolved_path == expected, f"Expected {expected}, but got {resolved_path}"

def test_invalid_template_name(resolver):
    with pytest.raises(KeyError):
        resolver.resolve("non_existent_template", {})

def test_invalid_context(resolver):
    with pytest.raises(KeyError):
        resolver.resolve("shot_workfile", {"root": "Z:/projects"})

def test_shot_workfile_resolves(resolver, common_context):
    path = resolver.resolve(template_name="shot_workfile", context=common_context)
    assert "SH010_comp_v004.nk" in path

def test_full_path_resolves(resolver):
    path = resolver.resolve(template_name="shot_workfile", context={
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ001",
        "shot": "SH010",
        "task": "comp",
        "version": "004",
        "ext": "nk"
    })
    expected_path = "Z:/projects/dragonfire/sequences/SQ001/SH010/work/comp/SH010_comp_v004.nk"
    assert path == expected_path

def test_image_sequence_resolves(resolver):
    path = resolver.resolve(template_name="render_frames", context={
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ001",
        "shot": "SH010",
        "task": "comp",
        "version": "004",
        "ext": "exr"
    })
    expected_path = "Z:/projects/dragonfire/sequences/SQ001/SH010/render/comp/SH010_comp_v004/SH010_comp_v004.####.exr"
    assert path == expected_path
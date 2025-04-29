# test_template_resolving.py

import pytest
from template_loader import TemplateLoader
from resolver import PathResolver

# This is a test file for the PathResolver class
# It tests the path resolution functionality using various templates and contexts.

@pytest.fixture
def loader():
    return TemplateLoader(["Z:\\Repositories\\PycharmProjects\\ConfluxPathResolver\\templates\pipeline_template.yaml"])

@pytest.fixture
def resolver(loader):
    resolver = PathResolver(loader=loader)
    return resolver

def test_shot_workfile_resolves(resolver):
    path = resolver.resolve(template_name="shot_workfile",context={
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ001",
        "shot": "SH010",
        "task": "comp",
        "version": "004",
        "ext": "nk"
    })
    assert "SH010_comp_v004.nk" in path

def test_asset_publish_resolves(resolver):
    path = resolver.resolve(template_name="asset_publish", context={
        "root": "Z:/projects",
        "project": "dragonfire",
        "asset_type": "char",
        "asset_name": "orc",
        "task": "model",
        "version": "002"
    })
    assert "orc_model_v002.abc" in path

def test_render_frame_path(resolver):
    path = resolver.resolve(template_name="render_frames", context={
        "root": "Z:/projects",
        "project": "dragonfire",
        "sequence": "SQ002",
        "shot": "SH020",
        "task": "lighting",
        "version": "001",
        "frame": "1001",
        "ext": "exr"
    })
    assert path.endswith("SH020.1001.exr")

def test_missing_field_raises(resolver):
    with pytest.raises(KeyError):
        resolver.resolve("shot_workfile", {
            "project": "dragonfire",
            "sequence": "SQ001",
            # missing shot
        })

def test_template_inheritance_defaults(resolver):
    tmpl = resolver.loader.get("shot_publish")
    assert tmpl.pattern.startswith("{root}")
    assert tmpl.parent == "shot_publish"

def test_template_inheritance_overrides(resolver):
    tmpl = resolver.loader.get("review_mov")
    assert tmpl.pattern == "{root}/{project}/publish/{task}/{shot}.{ext}"
    assert tmpl.parent == "shot_publish"

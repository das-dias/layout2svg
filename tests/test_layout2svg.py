import pytest
from pathlib import Path

from layout2svg import __version__

from layout2svg.layout2svg import load_layout, load_layerstack, render_to_svg
from layout2svg.data import LayerStack, Layer, LayerProperties, Material

import gdstk

def test_version():
    assert __version__ == '0.1.0'


def test_load_layout():
    layout = load_layout("./tests/data/crossed_metal.gds")
    assert layout is not None
    assert len(layout.cells) > 0
    assert layout.top_level() is not None
    assert len(layout.top_level()) == 1
    assert layout.top_level()[0].name == "crossed_metal"


def test_load_layerstack():
    layerstack = load_layerstack("./tests/data/mock_layers.ymls")
    assert layerstack is not None
    assert type(layerstack) == LayerStack
    assert len(layerstack.layers) > 0
    assert len(layerstack.layers) == 3
    assert layerstack.layers[(2, 0)] is not None
    assert layerstack.layers[(2, 0)].name == "metal1"
    assert layerstack.layers[(1, 0)] is None
    assert layerstack.layers[(2, 0)].metadata is not None
    assert layerstack.layers[(2, 0)].metadata.type == "routing"
    assert layerstack.layers[(2, 0)].metadata.keys == ["metal1", "m1"]
    
def test_render_to_svg():
    #TODO: implement test
    pass
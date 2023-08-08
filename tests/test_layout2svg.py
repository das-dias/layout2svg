import pytest
from pathlib import Path

from lxml import etree
import gdstk

from layout2svg import __version__

from layout2svg.layout2svg import load_layout, load_layerstack, render_to_svg
from layout2svg.data import LayerStack

def test_version():
    assert __version__ == '0.1.6'


def test_load_layout():
    layout = load_layout("./tests/data/crossed_metal.gds")
    assert layout is not None
    assert len(layout.cells) > 0
    assert layout.top_level() is not None
    assert len(layout.top_level()) == 1
    assert layout.top_level()[0].name == "crossed_metal"
    # TODO: expand tests

def test_load_layerstack():
    layerstack = load_layerstack("./tests/data/mock_layers.ymls")
    assert layerstack is not None
    assert type(layerstack) == LayerStack
    assert len(layerstack.layers) > 0
    assert len(layerstack.layers) == 3
    assert layerstack[(2, 0)] is not None
    assert layerstack[(2, 0)].name == "met1"
    assert layerstack[(1, 0)] is None
    assert layerstack.layers[(2, 0)].metadata is not None
    assert layerstack.layers[(2, 0)].metadata.type == "routing"
    assert layerstack.layers[(2, 0)].metadata.keys == ["Metal1", "M1"]
    # TODO: expand tests
    
    
def test_render_to_svg():
    layout = load_layout("./tests/data/crossed_metal.gds")
    layerstack = load_layerstack("./tests/data/mock_layers.ymls")
    
    svg = render_to_svg(layout, layerstack, topcell="crossed_metal", out="./tests/data/crossed_metal.svg")
    
    svg2 = render_to_svg(layout, layerstack, topcell="crossed_metal", out="./tests/data/crossed_metal_labeled.svg", render_labels=True)
    
    assert svg is not None
    assert svg2 is not None
    assert type(svg) == etree._Element
    assert type(svg2) == etree._Element
    assert Path("./tests/data/crossed_metal.svg").exists()
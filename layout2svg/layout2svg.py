import os
import sys
import tempfile
from pathlib import Path
from typing import Optional


import yaml
import gdstk
from lxml import etree

from .data import *

_LAYOUT_FILE_EXTENSIONS = [".oas", ".oasis", ".gds", ".gdsii"]

_LAYERSTACK_FILE_EXTENSIONS = [".yaml", ".yml", ".ymls"]


def load_layout(fp: str) -> Optional[gdstk.Library]:
    """Load a layout from a GDSII file.
    Args:
        fp: Path to the GDSII file.
    Returns:
        The top cell of the layout.
    """
    # check if file extension is .oas, .oasis, .gds, or .gdsii
    fp = str(Path(fp).resolve())
    ext = Path(fp).suffix

    assert Path(fp).exists(), f"File {fp} does not exist."
    
    lib = None
    if ext in _LAYOUT_FILE_EXTENSIONS[:2]:
        # load OASIS file
        lib = gdstk.read_oas(fp)

    elif ext in _LAYOUT_FILE_EXTENSIONS[2:]:
        # load GDSII file
        lib = gdstk.read_gds(fp)
    else:
        raise ValueError(
            f"Unsupported file extension: {ext}, Supported extensions: {_LAYOUT_FILE_EXTENSIONS}"
        )
    return lib


def load_layerstack(fp: str) -> LayerStack:
    """Load a layerstack from a YAML file
        and return a LayerStack Object
        mapping {(ly,dt) : LayerNode}
    Args:
        fp: Path to the YAML file.
    Returns:
        The layerstack.
    """
    fp = str(Path(fp).resolve())
    
    assert Path(fp).exists(), f"File {fp} does not exist."
    
    ext = Path(fp).suffix
    if ext not in _LAYERSTACK_FILE_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension: {ext}, Supported extensions: {_LAYERSTACK_FILE_EXTENSIONS}"
        )

    layerstack = {}
    layerstack_yaml = None
    try:
        with open(fp, "r") as f:
            layerstack_yaml = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Could not load layerstack from {fp}.") from e
    
    # convert layerstack to LayerStack object
    if not layerstack_yaml.get("layers"):
        raise ValueError("Layerstack is missing layers.")

    for layerkey, layer in layerstack_yaml["layers"].items():
        material = None
        properties = None
        metadata = None
        print(layer)
        if layer.get("metadata"):
            material = Material(
                rgba=layer["metadata"].get("rgba"), text=layer["metadata"].get("text")
            )
            metadata = LayerMetadata(
                type=layer["metadata"].get("type"),
                keys=layer["metadata"].get("keys"),
                material=material,
            )
        if not layer.get("properties"):
            raise ValueError(f"Layer {layerkey} is missing properties.")
        # check if layer has all required properties
        obligatory_pars = ["ly", "dt"]
        fields = list(map(lambda x: layer["properties"].get(x), obligatory_pars))
        if None in fields:
            raise ValueError(
                f"Layer {layerkey} is missing properties: {[field for field in fields if field is None]}"
            )
        properties = LayerProperties(
            ly=layer["properties"].get("ly"),
            dt=layer["properties"].get("dy"),
        )
        lydt = (properties.ly, properties.dt)
        layerstack[lydt] = Layer(
            name=layerkey, lydt=lydt, metadata=metadata, properties=properties
        )
    
    return LayerStack(layerstack)


def render_to_svg(
    layout: gdstk.Library,
    layerstack: LayerStack,
    topcell: Optional[str] = None,
    out: Optional[str] = None,
    cmap: Optional[Dict[Tuple[int, int], Dict[int, Tuple[str, float]]]] = None,
    render_labels: bool = False,
) -> etree.ElementTree:
    """Render a layout to an SVG file.

    Args:
        layout (gdstk.Library): IC Layout.
        layerstack (LayerStack): Layerstack.
        topcell (Optional[str]): Name of the layout's top cell to render.
        out (Optional[str]): Path to the output SVG file.
        cmap (Optional[Dict[Tuple[int, int], Dict[int, Tuple[str,float]]]]): Color map for each polygon of each layer.
        render_labels (bool): Render labels to SVG surface.
    Returns:
        etree.ElementTree: SVG XML file rendered from the layout.
    """

    # check if topcell exists
    tcell = max(layout.cells, key=lambda cell: cell.area())
    if topcell not in [cell.name for cell in layout.cells]:
        Warning(f"Topcell {topcell} not found in layout. Rendering largest cell.")
    else:
        tcell = layout[topcell]
    # create SVG surface
    pbot, ptop = tcell.bounding_box()
    width_points, length_points = (
        abs(val) for val in (v2 - v1 for v1, v2 in zip(pbot, ptop))
    )
    # create SVG xml tree
    kwargs = {
        "width": width_points,
        "height": length_points,
        "version": 1.0,
        "xmlns": "http://www.w3.org/2000/svg",
        "xmlns:dc": "http://purl.org/dc/elements/1.1/",
        "xmlns:cc": "http://creativecommons.org/ns#",
        "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xmlns:svg": "http://www.w3.org/2000/svg",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "id": f"{tcell.name}",
        "renderedby": "layout2svg",
    }
    tree = etree.Element("svg", **kwargs)
    tree_child = etree.SubElement(tree, "g", id=f"{tcell.name}")

    # setup colour mappings for each poly of each layer
    if cmap is None:
        cmap = {}
        for layer, datatype in layerstack.layers.keys():
            layer_cmap = {}
            layer_polys = tcell.get_polygons(layer=layer, datatype=datatype)
            for id, poly in enumerate(layer_polys):
                # must be in 6 digit hexadecimal format + opacity as alpha channel
                mat = layerstack[(layer, datatype)].metadata.material
                layer_cmap[id] = (
                    mat.hex,  # fill as 6-digit hex
                    mat.rgba[-1] / 255,  # opacity as alpha channel between 0 and 1
                )

    # render polygons to SVG surface
    for layer, datatype in layerstack.layers.keys():
        layer_polys = tcell.get_polygons(layer=layer, datatype=datatype)
        # set the layer, datatype attributes of the polygon
        layer_group = etree.SubElement(tree_child, "g", id=f"{layer},{datatype}")
        for id, poly in enumerate(layer_polys):
            # build an SVG polygon at the corresponding layer
            # add the polygon to the SVG surface
            vertices = poly.points
            str_vertices = "m "
            str_vertices += [
                f"{vertex[0]},{vertex[1]}" for vertex in vertices[1:]
            ].join(" ")
            str_vertices += " z"
            fill = cmap[(layer, datatype)][id][0]
            opacity = cmap[(layer, datatype)][id][1]
            style = f"fill:{fill};fill-opacity:{opacity}"
            etree.SubElement(
                layer_group,
                "path",
                id=f"{layer},{datatype},{id}",
                d=str_vertices,
                style=style,
            )
    # render labels to SVG surface
    if render_labels:
        for label in tcell.labels:
            # initialize a new group to hold the label
            text_group = etree.SubElement(
                tree_child,
                "text",
                {
                    "id": f"{label.text}:{label.layer},{label.texttype}",
                    "x": f"{label.origin[0]}",
                    "y": f"{label.origin[1]}",
                    "fill": "black",
                    "font-family": "ariel",
                    "font-size": f"{10/max([width_points,length_points])}",
                },
            )

    if out:
        svg_canvas = etree.ElementTree(tree)
        svg_canvas.write(
            Path(out).resolve(), pretty_print=True, version=1.0, standalone="no", encoding="UTF-8"
        )
    return tree

<h1 align=center> layout2svg </h1>

<div align=justify>
<p> This is a simple tool to convert an integrated circuit layout saved in OASIS / GDSII file format to a .SVG image file. The tool supports direct export of the SVG file into the Inkscape desktop app. This tool was written with the goal of rendering any layout in a desktop or web application. </p>
</div>

<h2 align=center> Installation </h2>

<h3 align=center> MacOS, Linux, Windows </h3>

```bash
pip install layout2svg
```

<h2 align=center> Usage - Command Line Interface </h2>

```bash
layout2svg -i <input_file_path [.gds/.oas]> -o <output_file_path [.svg]>
```

<h2 align=center> Examples </h2>

<p>
Running the example with the mock layerstack file and layout provided in the <a href="./examples">examples</a> directory, by running the following command:
</p>

```bash
layout2svg -i examples/crossed_metal.gds -t examples/mock_layers.lys.yml -o examples/crossed_metal.svg
```

<p>
can generate the following SVG image:
</p>

<p align=center>
<img src="./examples/crossed_metal.svg" width="400" height="400">
</p>

#!/usr/bin/env python3

"""layout2svg command line tool.

Usage:
    layout2svg -i <input> -t <layerstack> [-c <top_cell>] -o --output <output> [--verbose] [--inkscape] [--log <log>]
    layout2svg -i <input> -t <layerstack> [-c <top_cell>] [--verbose] --inkscape [--log <log>]
    layout2svg -h | --help
    layout2svg --version

Options:
    -h --help     Show this help message and exit.
    --version     Show version information.
    --verbose     Enable verbose debug output.
    --inkscape    Use inkscape to render SVG.
    -i --input    Input [.gds] | [.oas] layout file.
    -t            Layerstack [.lys.yml] file.
    -c --top-cell Top cell name. If not specified, the largest area cell is used.
    -o --output   Output [.svg] file.
    --log         Log file.
Description:
    layout2svg is a tool to convert GDS or OAS layout files to SVG. 
    Optional direct rendering to Inkscape is supported.
"""


from layout2svg.layout2svg import load_layerstack, load_layout, render_to_svg
import platform
import sys
import tempfile
import subprocess
try:
    from loguru import logger
except ImportError as e:
    print("Error: loguru not found.", e)
    print("Please install loguru with: pip install loguru")
    exit(1)

try:
    from docopt import docopt
except ImportError as e:
    print("Error: docopt not found.", e)
    print("Please install docopt with: pip install docopt")
    exit(1)

# get inkscape binary path
INKSCAPE_BIN = ""
try:
    if platform.system() == "Windows":
        INKSCAPE_BIN = subprocess.check_output(["where", "inkscape"]).decode("utf-8").strip()
    elif platform.system() == "Darwin":
        INKSCAPE_BIN = subprocess.check_output(["which", "inkscape"]).decode("utf-8").strip()
    elif platform.system() == "Linux":
        INKSCAPE_BIN = subprocess.check_output(["command", "-v", "inkscape"]).decode("utf-8").strip()
    else:
        print("Error: Unsupported platform.")
        exit(1)
except subprocess.CalledProcessError as e:
    print("Error: Could not find inkscape binary.", e)
    exit(1)

def main():
    # Configure the logger to write to a file
    logger.add("layout2svg.log", rotation="1 week")  # Change the log file name and rotation settings as needed
    args = docopt(__doc__, version="layout2svg 1.0")
    verbose = args["--verbose"]
    render_to_inkscape = args["--inkscape"] and (INKSCAPE_BIN != "")
    render_to_svg = args.get("-o") or args.get("--output")
    
    try: 
        # import layout
        layerstack = load_layerstack(args["-t"])
        # import layerstack to generate svg layer info
        layout = load_layout(args["-i"])
    except Exception as e:
        if verbose:
            logger.error("Could not load layout or layerstack: ")
            logger.exception(e)
        sys.exit("Failed: Could not load input files.")
    
    topcell_name = args.get("-c") or args.get("--top-cell")
    if render_to_svg:
        try:
            render_to_svg(layout, layerstack, topcell=topcell_name, o=args["-o"])
        except Exception as e:
            if verbose:
                logger.error("Could not render to SVG: ", e)
            sys.exit("Failed: Could not render to output file.")
        if verbose:
            logger.success("Rendered to SVG: ", args["-o"])
    if render_to_inkscape:
        print("Inkscape binary found at: ", INKSCAPE_BIN)
        cmd = [INKSCAPE_BIN, "--pipe"]
        try:
            with tempfile.NamedTemporaryFile(suffix=".svg") as f:
                try:
                    render_to_svg(layout, layerstack, topcell=topcell_name, out=f.name)
                except Exception as e:
                    if verbose:
                        logger.error("Could not render to temporary file: ")
                        logger.exception(e)
                    sys.exit("Failed: Could not render to Inkscape.")
                try:
                    cmd.append(f.name)
                    subprocess.run(cmd)
                except subprocess.CalledProcessError as e:
                    if verbose:
                        logger.error("Subprocess system call failed: ")
                        logger.exception(e)
                    sys.exit("Failed: Could not render to Inkscape.")
        except OSError as e:
            if verbose:
                logger.error("Could not create temporary file: ")
                logger.exception(e)
            sys.exit("Failed: Could not render to Inkscape.")
        if verbose:
            logger.success("Inkscape run: ", cmd.join(" "))
    logger.success("Done.")
    
if __name__ == "__main__":
    main()
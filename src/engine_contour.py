#!/usr/bin/env python3

#-----------------------------------------------------------------------------------------------------------------------
# Program: Filleted Injector-Chamber-Interface Rocket Engine Contour Model
# Version: 1.0
# Date:    2019
# Author:  Rohin Gosling
#
# Description:
#
#   Python / Matplotlib port of the legacy MATLAB model in src/legacy/engineContour.m (and its helper circle.m).
#   Since I no longer have access to Matlab, I created this Python tool to reproduce the exact same 2D axial-contour
#   rendering of the filleted combustion chamber, throat, and nozzle adaptor, and save it as a PNG screenshot.
#
#   Geometry note:
# 
#   - The MATLAB engineContour() accepts s1..s5 as arguments but then immediately overrides them with hard-coded 
#     section boundaries.
#
#   - This port mirrors that behavior faithfully. The meaningful inputs are the three radii (chamber RC, throat RT, 
#     and exhaust RE).
#
#   - The axial section boundaries are fixed exactly as in the original.
#
# Usage:
#
#   python3 engine_contour.py                       # defaults: RC=4.0, RT=1.5, RE=3.0 (matches the MATLAB example)
#   python3 engine_contour.py --rc 4 --rt 1 --re 2  # the values testFig.m's button used
#   python3 engine_contour.py --out path/to.png     # choose output file
#
#-----------------------------------------------------------------------------------------------------------------------

import argparse
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# NOTE: The headless "Agg" backend is selected inside main() (just before rendering) rather than at import time, so
#       that other tools (e.g. the interactive 3D viewer) can import the profile geometry below without being forced
#       onto a non-interactive backend.


#-----------------------------------------------------------------------------------------------------------------------
# Function: circle
#
# Description:
#
#   Port of circle.m: plot a circle of radius r centred at (x, y) using the given Matplotlib line style. The original
#   had an optional axis-drawing branch gated on showAxis = false, so only the circle itself is reproduced here.
#
# Arguments:
#
#   axes       : Matplotlib axes to draw the circle on.
#   x          : X-coordinate of the circle centre.
#   y          : Y-coordinate of the circle centre.
#   r          : Circle radius.
#   line_style : Matplotlib line style for the circle outline.
#
# Returns:
#
#   None.
#
#-----------------------------------------------------------------------------------------------------------------------

def circle ( axes, x, y, r, line_style ):

    # Plot a circle of radius r centred at (x, y).

    # Sample the parametric circle at a fixed number of points and offset it to the requested centre.

    sample_count = 32.0
    t            = np.arange ( 0.0, 2.0 * np.pi + ( 2.0 * np.pi / sample_count ) / 2.0, 2.0 * np.pi / sample_count )
    x_points     = r * np.cos ( t ) + x
    y_points     = r * np.sin ( t ) + y

    # Draw the circle outline.

    axes.plot ( x_points, y_points, linewidth = 1, color = "k", linestyle = line_style )


#-----------------------------------------------------------------------------------------------------------------------
# Function: thrust_chamber_profile
#
# Description:
#
#   Build the inner-surface axial contour of the thrust chamber as a single, continuous (axial, radial) point set,
#   ordered by increasing axial position. This is the same upper-half geometry that engine_contour() draws, but
#   returned as raw arrays (no plotting) so other tools -- such as the interactive 3D viewer -- can consume the
#   profile directly. The five contour segments (injector fillet, combustion chamber, neck, throat parabola, nozzle
#   adaptor) are concatenated in axial order. Construction guide-lines and fillet circles are NOT part of the surface
#   and are therefore excluded.
#
# Arguments:
#
#   chamber_radius : Combustion chamber radius.
#   throat_radius  : Throat radius.
#   exhaust_radius : Nozzle adaptor exhaust radius.
#
# Returns:
#
#   A tuple ( axial, radial ) of NumPy arrays giving the axial position and the corresponding surface radius along
#   the inner contour, in order of increasing axial position.
#
#-----------------------------------------------------------------------------------------------------------------------

def thrust_chamber_profile ( chamber_radius, throat_radius, exhaust_radius ):

    # Build the inner-surface contour as concatenated (axial, radial) arrays.

    # Sectional partitions (hard-coded in the original; same values reproduced here).

    s0 = 0.0        # Origin (injector face).
    s1 = 1.0        # Injector.
    s2 = 6.0        # Combustion chamber.
    s3 = 10.0       # Neck.
    s4 = 12.0       # Throat.
    s5 = 14.0       # Nozzle adaptor.

    # Radii.

    r0 = chamber_radius     # Combustion chamber radius.
    r1 = s1                 # Injector fillet radius.
    r2 = r0 - r1            # Injector injection face radius.
    r3 = throat_radius      # Throat radius.
    r4 = exhaust_radius     # Nozzle adaptor exhaust radius.

    # Derive contour-function coefficients for the throat parabola f(x) and the nozzle adaptor line g(x).

    y0 = r3
    x0 = s3
    x1 = s4
    x2 = s5
    y2 = r4

    a0 =                                                            -( y0 - y2 ) / ( ( x0 - x1 ) * ( x0 + x1 - 2 * x2 ) )
    b0 =                                                ( 2 * x0 * ( y0 - y2 ) ) / ( ( x0 - x1 ) * ( x0 + x1 - 2 * x2 ) )
    c0 = -( -y2 * x0 ** 2 + 2 * x2 * y0 * x0 + y0 * x1 ** 2 - 2 * x2 * y0 * x1 ) / ( ( x0 - x1 ) * ( x0 + x1 - 2 * x2 ) )
    a1 =                                                     ( 2 * ( y0 - y2 ) ) / ( x0 + x1 - 2 * x2 )
    b1 =                                     ( x0 * y2 - 2 * x2 * y0 + x1 * y2 ) / ( x0 + x1 - 2 * x2 )

    # Axial sample points per section (t is the axial sampling step; same value as the 2D renderer).

    t = 0.01

    section_injector = np.arange ( s0, s1 + t / 2.0, t )
    section_chamber  = np.arange ( s1, s2 + t / 2.0, t )
    section_neck     = np.arange ( s2, s3 + t / 2.0, t )
    section_throat   = np.arange ( s3, s4 + t / 2.0, t )
    section_nozzle   = np.arange ( s4, s5 + t / 2.0, t )

    # Sectional contour functions (surface radius at each axial sample).

    injector = r2 + np.sqrt ( r1 ** 2 - ( section_injector - r1 ) ** 2 )
    chamber  = np.full_like ( section_chamber, r0 )
    neck     = r3 + ( r0 - r3 ) * ( 1 + np.cos ( ( section_neck - s2 ) * np.pi / ( s3 - s2 ) ) ) / 2.0
    throat   = a0 * section_throat ** 2 + b0 * section_throat + c0
    nozzle   = a1 * section_nozzle + b1

    # Concatenate the five segments in axial order into a single continuous profile.

    axial  = np.concatenate ( [ section_injector, section_chamber, section_neck, section_throat, section_nozzle ] )
    radial = np.concatenate ( [ injector,         chamber,         neck,         throat,         nozzle         ] )

    # Return the inner-surface contour as (axial, radial) arrays.

    return axial, radial


#-----------------------------------------------------------------------------------------------------------------------
# Function: engine_contour
#
# Description:
#
#   Port of engineContour.m. Builds the five contour segments (injector fillet, combustion chamber, neck, throat
#   parabola, nozzle adaptor), mirrors them about the axis, and draws the construction guide-lines and fillet circles.
#
# Arguments:
#
#   chamber_radius : Combustion chamber radius.
#   throat_radius  : Throat radius.
#   exhaust_radius : Nozzle adaptor exhaust radius.
#
# Returns:
#
#   The Matplotlib figure containing the rendered thrust-chamber contour.
#
#-----------------------------------------------------------------------------------------------------------------------

def engine_contour ( chamber_radius, throat_radius, exhaust_radius ):

    # Build and return the thrust-chamber contour figure.

    # Sectional partitions (hard-coded in the original; same values reproduced here).

    s0 = 0.0        # Origin (injector face).
    s1 = 1.0        # Injector.
    s2 = 6.0        # Combustion chamber.
    s3 = 10.0       # Neck.
    s4 = 12.0       # Throat.
    s5 = 14.0       # Nozzle adaptor.

    # Radii.

    r0 = chamber_radius     # Combustion chamber radius.
    r1 = s1                 # Injector fillet radius.
    r2 = r0 - r1            # Injector injection face radius.
    r3 = throat_radius      # Throat radius.
    r4 = exhaust_radius     # Nozzle adaptor exhaust radius.

    # Derive contour-function coefficients for the throat parabola f(x) and the nozzle adaptor line g(x).

    y0 = r3
    x0 = s3
    x1 = s4
    x2 = s5
    y2 = r4

    a0 =                                                            -( y0 - y2 ) / ( ( x0 - x1 ) * ( x0 + x1 - 2 * x2 ) )
    b0 =                                                ( 2 * x0 * ( y0 - y2 ) ) / ( ( x0 - x1 ) * ( x0 + x1 - 2 * x2 ) )
    c0 = -( -y2 * x0 ** 2 + 2 * x2 * y0 * x0 + y0 * x1 ** 2 - 2 * x2 * y0 * x1 ) / ( ( x0 - x1 ) * ( x0 + x1 - 2 * x2 ) )
    a1 =                                                     ( 2 * ( y0 - y2 ) ) / ( x0 + x1 - 2 * x2 )
    b1 =                                     ( x0 * y2 - 2 * x2 * y0 + x1 * y2 ) / ( x0 + x1 - 2 * x2 )
    y1 =                       ( 2 * x1 * y0 + x0 * y2 - 2 * x2 * y0 - x1 * y2 ) / ( x0 + x1 - 2 * x2 )

    # Model geometric parameters (axial sample points per section).

    t = 0.01

    section_injector = np.arange ( s0, s1 + t / 2.0, t )
    section_neck     = np.arange ( s2, s3 + t / 2.0, t )
    section_throat   = np.arange ( s3, s4 + t / 2.0, t )
    section_nozzle   = np.arange ( s4, s5 + t / 2.0, t )

    # Sectional contour functions.

    injector       = r2 + np.sqrt ( r1 ** 2 - ( section_injector - r1 ) ** 2 )
    neck           = r3 + ( r0 - r3 ) * ( 1 + np.cos ( ( section_neck - s2 ) * np.pi / ( s3 - s2 ) ) ) / 2.0
    throat         = a0 * section_throat ** 2 + b0 * section_throat + c0
    nozzle_adaptor = a1 * section_nozzle + b1

    # Plot model.

    figure, axes = plt.subplots ( figsize = ( 12, 6 ) )

    line_width = 2
    margin     = 2

    # Centre line.

    axes.plot ( [ s0 - margin, s5 + margin ], [ 0, 0 ], linewidth = 1, color = "k", linestyle = "--" )

    # Injector face (vertical wall at the origin).

    axes.plot ( [ 0, 0 ], [ 0, r2 ],  linewidth = line_width, color = "k" )
    axes.plot ( [ 0, 0 ], [ 0, -r2 ], linewidth = line_width, color = "k" )

    # Injector fillet + its guide lines and construction circles.

    axes.plot ( section_injector, injector,  linewidth = line_width, color = "k" )
    axes.plot ( section_injector, -injector, linewidth = line_width, color = "k" )
    axes.plot ( [ s1, s1 ], [ -r0, r0 ],     linewidth = 1, color = "k", linestyle = ":" )
    axes.plot ( [ s0, s1 ], [ r2, r2 ],      linewidth = 1, color = "k", linestyle = ":" )
    axes.plot ( [ s0, s1 ], [ -r2, -r2 ],    linewidth = 1, color = "k", linestyle = ":" )

    circle ( axes, r1, r2, r1, ":" )
    circle ( axes, r1, -r2, r1, ":" )

    # Combustion chamber walls.

    axes.plot ( [ s1, s2 ], [ r0, r0 ],   linewidth = line_width, color = "k" )
    axes.plot ( [ s1, s2 ], [ -r0, -r0 ], linewidth = line_width, color = "k" )
    axes.plot ( [ s2, s2 ], [ -r0, r0 ],  linewidth = 1, color = "k", linestyle = ":" )

    # Neck.

    axes.plot ( section_neck, neck,      linewidth = line_width, color = "k" )
    axes.plot ( section_neck, -neck,     linewidth = line_width, color = "k" )
    axes.plot ( [ s3, s3 ], [ -r3, r3 ], linewidth = 1, color = "k", linestyle = ":" )

    # Throat.

    axes.plot ( section_throat, throat,  linewidth = line_width, color = "k" )
    axes.plot ( section_throat, -throat, linewidth = line_width, color = "k" )
    axes.plot ( [ s4, s4 ], [ -y1, y1 ], linewidth = 1, color = "k", linestyle = ":" )

    # Nozzle adaptor.

    axes.plot ( section_nozzle, nozzle_adaptor,  linewidth = line_width, color = "k" )
    axes.plot ( section_nozzle, -nozzle_adaptor, linewidth = line_width, color = "k" )
    axes.plot ( [ s5, s5 ], [ -y2, y2 ],         linewidth = 1, color = "k", linestyle = ":" )

    # Graphing parameters.

    axes.set_aspect ( "equal", adjustable = "box" )
    axes.set_xlim   ( s0 - margin, s5 + margin )
    axes.set_ylim   ( -r0 - margin, r0 + margin )
    axes.set_xticks ( np.arange ( s0 - 1, s5 + 1 + 1, 1 ) )
    axes.set_yticks ( np.arange ( -r0 - 1, r0 + 1 + 1, 1 ) )

    # Grid parameters (light-grey grid and axes, matching the MATLAB styling).

    axes.grid ( True, linestyle = "-", color = "0.8" )
    axes.spines [ "top" ].set_color ( "0.8" )
    axes.spines [ "bottom" ].set_color ( "0.8" )
    axes.spines [ "left" ].set_color ( "0.8" )
    axes.spines [ "right" ].set_color ( "0.8" )
    axes.tick_params ( colors = "0.5" )

    # Return the assembled figure to the caller.

    return figure

#-----------------------------------------------------------------------------------------------------------------------
# Function: main
#
# Description:
#
#   Command-line entry point. Parses the radius arguments and optional output path, renders the thrust-chamber
#   contour, and saves it as a PNG screenshot.
#
# Arguments:
#
#   None.
#
# Returns:
#
#   None.
#
#-----------------------------------------------------------------------------------------------------------------------

def main ():

    # Parse command-line arguments, render the contour, and save it as a PNG screenshot.

    # Select the headless backend -- this tool renders straight to a PNG, with no interactive window.

    matplotlib.use ( "Agg" )

    # Build the command-line argument parser.

    parser = argparse.ArgumentParser ( description = "Render the filleted-injector rocket engine thrust-chamber contour." )

    # Register the three radius inputs and the optional output-path override.

    parser.add_argument ( "--rc", type = float, default = 4.0, help = "Combustion chamber radius (default 4.0)." )
    parser.add_argument ( "--rt", type = float, default = 1.5, help = "Throat radius (default 1.5)." )
    parser.add_argument ( "--re", type = float, default = 3.0, help = "Nozzle adaptor exhaust radius (default 3.0)." )
    parser.add_argument ( "--out", type = str, default = None, help = "Output PNG path (default ../images/engine-contour.png)." )

    # Parse the command-line arguments.

    arguments = parser.parse_args ()

    # Resolve the output path from the argument, if supplied.

    output_path = arguments.out

    # Fall back to the default output location when no path was given.

    if output_path is None:

        # Locate the output directory relative to this script.

        script_directory = os.path.dirname ( os.path.abspath ( __file__ ) )
        output_directory = os.path.join ( script_directory, "..", "images" )

        # Create the output directory if it does not already exist.

        os.makedirs ( output_directory, exist_ok = True )

        # Use the default output file name within that directory.

        output_path = os.path.join ( output_directory, "engine-contour.png" )

    # Render the contour and save the figure as a PNG screenshot.

    figure = engine_contour ( arguments.rc, arguments.rt, arguments.re )
    figure.savefig ( output_path, dpi = 150, bbox_inches = "tight" )

    # Report the absolute path of the saved screenshot.

    print ( f"Saved thrust-chamber contour to: {os.path.abspath ( output_path )}" )

#-----------------------------------------------------------------------------------------------------------------------
# Program entry point.
#-----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    main ()

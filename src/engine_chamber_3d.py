#!/usr/bin/env python3

#-----------------------------------------------------------------------------------------------------------------------
# Program: Filleted Injector-Chamber-Interface Rocket Engine -- Interactive 3D Wireframe Viewer
# Version: 1.0
# Date:    2019
# Author:  Rohin Gosling
#
# Description:
#
#   Companion to engine_contour.py. Takes the same inner-surface thrust-chamber profile (imported directly from
#   engine_contour.thrust_chamber_profile) and revolves it about the engine axis to build a 3D wireframe model of
#   the chamber's inner surface.
#
#   The revolution uses a step of 2*pi/16, producing a 16-sided model: 16 longitudinal ribs and a regular 16-gon at
#   every cross-section. The contour is resampled to ~40 evenly spaced axial stations so the circumferential hoops
#   read as a clean wireframe rather than a solid mass.
#
#   Rendering matches the 2D diagram's plain "black lines on white" mathematical style and equal-unit scale -- it is
#   the same geometry, just in 3D. The model is shown in an interactive Matplotlib window that can be rotated with
#   the mouse, ready to screenshot. No shading, hidden-surface removal, or depth sorting is applied (by design).
#
# Usage:
#
#   python3 engine_chamber_3d.py                       # defaults: RC=4.0, RT=1.5, RE=3.0 (matches engine_contour.py)
#   python3 engine_chamber_3d.py --rc 4 --rt 1 --re 2  # custom radii
#   python3 engine_chamber_3d.py --sides 16 --stations 40
#
#-----------------------------------------------------------------------------------------------------------------------

import argparse
import os
import sys

import numpy as np
import matplotlib

# Import the shared inner-surface profile from the 2D renderer. Add this script's directory to the module search path
# first, so the import works regardless of the current working directory.

sys.path.insert ( 0, os.path.dirname ( os.path.abspath ( __file__ ) ) )

from engine_contour import thrust_chamber_profile


#-----------------------------------------------------------------------------------------------------------------------
# Function: select_interactive_backend
#
# Description:
#
#   Ensure Matplotlib is using an interactive (GUI) backend so the 3D model can be rotated with the mouse. If the
#   current backend is non-interactive (e.g. the headless "Agg"), try a sequence of common GUI backends in turn.
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

def select_interactive_backend ():

    # Switch to an interactive backend if the current one cannot open a window.

    # Leave the backend alone if it is already interactive.

    if matplotlib.get_backend ().lower () != "agg":

        return

    # Otherwise try a sequence of common GUI backends until one succeeds.

    for backend in ( "TkAgg", "QtAgg", "Qt5Agg", "Qt6Agg", "wxAgg" ):

        try:

            matplotlib.use ( backend, force = True )
            return

        except Exception:

            continue

    # Warn if no interactive backend could be selected (the window will not open).

    print ( "Warning: no interactive Matplotlib backend available; cannot open a rotatable window." )


#-----------------------------------------------------------------------------------------------------------------------
# Function: revolve_profile
#
# Description:
#
#   Revolve a 2D (axial, radial) profile about the engine axis (the x-axis) to produce a 3D surface mesh. The mesh
#   is sampled at side_count angular steps of 2*pi/side_count; one extra angle is appended (a duplicate of the first)
#   so each circumferential hoop closes into a complete polygon.
#
# Arguments:
#
#   axial      : Axial positions of the profile stations (1D array).
#   radial     : Surface radius at each station (1D array, same length as axial).
#   side_count : Number of sides of the revolved polygon (e.g. 16 for a 2*pi/16 step).
#
# Returns:
#
#   A tuple ( mesh_x, mesh_y, mesh_z ) of 2D arrays, each shaped (station_count, side_count + 1), giving the mesh
#   coordinates for Matplotlib's plot_wireframe.
#
#-----------------------------------------------------------------------------------------------------------------------

def revolve_profile ( axial, radial, side_count ):

    # Revolve the profile about the x-axis into a closed wireframe mesh.

    # Sample the revolution angle, repeating the first angle at the end to close each hoop.

    angle = np.linspace ( 0.0, 2.0 * np.pi, side_count + 1 )

    # Build the mesh: x is constant around each hoop; y and z trace each circle of the given radius.

    mesh_x = np.outer ( axial,  np.ones_like ( angle ) )
    mesh_y = np.outer ( radial, np.cos ( angle ) )
    mesh_z = np.outer ( radial, np.sin ( angle ) )

    # Return the revolved surface mesh.

    return mesh_x, mesh_y, mesh_z


#-----------------------------------------------------------------------------------------------------------------------
# Function: render_chamber_3d
#
# Description:
#
#   Resample the inner-surface profile to a fixed number of evenly spaced axial stations, revolve it into a 3D
#   wireframe, and draw it in the plain black-on-white mathematical style of the 2D diagram with equal-unit scaling.
#
# Arguments:
#
#   chamber_radius : Combustion chamber radius.
#   throat_radius  : Throat radius.
#   exhaust_radius : Nozzle adaptor exhaust radius.
#   side_count     : Number of sides of the revolved polygon.
#   station_count  : Number of evenly spaced axial hoops.
#
# Returns:
#
#   The Matplotlib figure containing the rendered 3D wireframe.
#
#-----------------------------------------------------------------------------------------------------------------------

def render_chamber_3d ( chamber_radius, throat_radius, exhaust_radius, side_count, station_count ):

    # Build and return the 3D wireframe figure of the thrust-chamber inner surface.

    import matplotlib.pyplot as plt

    # Obtain the dense inner-surface profile, then resample it to evenly spaced axial stations for a clean wireframe.

    axial_dense, radial_dense = thrust_chamber_profile ( chamber_radius, throat_radius, exhaust_radius )

    axial  = np.linspace ( axial_dense.min (), axial_dense.max (), station_count )
    radial = np.interp ( axial, axial_dense, radial_dense )

    # Revolve the resampled profile into a 3D wireframe mesh.

    mesh_x, mesh_y, mesh_z = revolve_profile ( axial, radial, side_count )

    # Create the 3D figure and axes.

    figure = plt.figure ( figsize = ( 10, 8 ) )
    axes   = figure.add_subplot ( projection = "3d" )

    # Draw the wireframe (plain black lines, matching the 2D contour style).

    axes.plot_wireframe ( mesh_x, mesh_y, mesh_z, rstride = 1, cstride = 1, color = "k", linewidth = 1.0 )

    # Draw the engine centre line (dashed), matching the 2D diagram.

    margin     = 2
    axial_low  = axial.min () - margin
    axial_high = axial.max () + margin

    axes.plot ( [ axial_low, axial_high ], [ 0, 0 ], [ 0, 0 ], linewidth = 1, color = "k", linestyle = "--" )

    # Equal-unit scaling: size the 3D box in proportion to the data span on each axis (1 unit looks the same on all
    # three axes, just like the 2D diagram's equal aspect ratio).

    radius_max = radial.max ()

    axes.set_xlim ( axial_low, axial_high )
    axes.set_ylim ( -radius_max - margin, radius_max + margin )
    axes.set_zlim ( -radius_max - margin, radius_max + margin )

    span_x = axial_high - axial_low
    span_y = 2.0 * ( radius_max + margin )
    span_z = 2.0 * ( radius_max + margin )

    axes.set_box_aspect ( ( span_x, span_y, span_z ) )

    # Styling: light-grey grid and panes, grey ticks -- the 3D equivalent of the 2D diagram's styling.

    axes.xaxis.set_pane_color ( ( 1.0, 1.0, 1.0, 1.0 ) )
    axes.yaxis.set_pane_color ( ( 1.0, 1.0, 1.0, 1.0 ) )
    axes.zaxis.set_pane_color ( ( 1.0, 1.0, 1.0, 1.0 ) )

    axes.grid ( True, linestyle = "-", color = "0.8" )
    axes.tick_params ( colors = "0.5" )

    # Label the axes and give the window a descriptive title.

    axes.set_xlabel ( "axial" )
    axes.set_ylabel ( "radial (y)" )
    axes.set_zlabel ( "radial (z)" )

    figure.canvas.manager.set_window_title ( "Thrust Chamber Inner Surface -- 3D Wireframe" )

    # Return the assembled figure to the caller.

    return figure


#-----------------------------------------------------------------------------------------------------------------------
# Function: main
#
# Description:
#
#   Command-line entry point. Parses the radius and resolution arguments, selects an interactive backend, renders the
#   3D wireframe, and opens it in a rotatable window.
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

    # Parse command-line arguments, render the 3D wireframe, and show it in an interactive window.

    # Ensure an interactive (GUI) backend is active before any figure is created.

    select_interactive_backend ()

    import matplotlib.pyplot as plt

    # Build the command-line argument parser.

    parser = argparse.ArgumentParser ( description = "Interactive 3D wireframe of the filleted-injector thrust-chamber inner surface." )

    # Register the three radius inputs and the resolution controls.

    parser.add_argument ( "--rc",       type = float, default = 4.0, help = "Combustion chamber radius (default 4.0)." )
    parser.add_argument ( "--rt",       type = float, default = 1.5, help = "Throat radius (default 1.5)." )
    parser.add_argument ( "--re",       type = float, default = 3.0, help = "Nozzle adaptor exhaust radius (default 3.0)." )
    parser.add_argument ( "--sides",    type = int,   default = 16,  help = "Number of sides of the revolved model (default 16)." )
    parser.add_argument ( "--stations", type = int,   default = 40,  help = "Number of evenly spaced axial hoops (default 40)." )

    # Parse the command-line arguments.

    arguments = parser.parse_args ()

    # Render the 3D wireframe figure.

    figure = render_chamber_3d ( arguments.rc, arguments.rt, arguments.re, arguments.sides, arguments.stations )

    # Open the interactive window (rotate with the mouse; screenshot when ready).

    print ( "Opening interactive 3D window -- rotate with the mouse, then take a screenshot. Close the window to exit." )

    plt.show ()


#-----------------------------------------------------------------------------------------------------------------------
# Program entry point.
#-----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    main ()

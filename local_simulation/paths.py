"""
paths.py
--------
Predefined path definitions for the mobile robot demo.

Each path is a list of (x, y) waypoints in meters that the controller
in controller.py will drive the robot through sequentially using a
simple proportional heading + distance controller.
"""

import math


def square_path(side=1.0):
    """Return waypoints for a square path of given side length (meters)."""
    return [
        (0.0, 0.0),
        (side, 0.0),
        (side, side),
        (0.0, side),
        (0.0, 0.0),
    ]


def circle_path(radius=1.0, num_points=24):
    """Return waypoints approximating a circle."""
    pts = []
    for i in range(num_points + 1):
        angle = 2 * math.pi * i / num_points
        pts.append((radius * math.cos(angle), radius * math.sin(angle)))
    return pts


def figure_eight_path(scale=1.0, num_points=48):
    """Return waypoints approximating a figure-eight (lemniscate)."""
    pts = []
    for i in range(num_points + 1):
        t = 2 * math.pi * i / num_points
        x = scale * math.sin(t)
        y = scale * math.sin(t) * math.cos(t)
        pts.append((x, y))
    return pts


PATHS = {
    "square": square_path(side=1.5),
    "circle": circle_path(radius=1.0),
    "figure_eight": figure_eight_path(scale=1.2),
}

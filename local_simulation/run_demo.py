"""
run_demo.py
-----------
Runnable entry point for the mobile robot simulation demo.

Usage:
    python3 run_demo.py --path square
    python3 run_demo.py --path circle
    python3 run_demo.py --path figure_eight
    python3 run_demo.py --path square --no-plot   (headless / CI mode)

This script:
  1. Instantiates a DifferentialDriveRobot (robot_model.py)
  2. Loads a predefined path (paths.py)
  3. Drives the robot along the path using the waypoint controller
     (controller.py) -- this is the same control loop structure used
     by the ROS 2 node in gazebo_ros2_package/scripts/robot_controller.py
  4. Logs the resulting trajectory to CSV
  5. Renders a plot of the commanded path vs. actual driven path
"""

import argparse
import csv
import os
import sys

from robot_model import DifferentialDriveRobot
from controller import follow_waypoints
from paths import PATHS


def save_log_csv(log, out_path):
    if not log:
        print("Warning: empty log, nothing to save.")
        return
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["t", "x", "y", "theta", "v", "w", "goal"])
        writer.writeheader()
        for row in log:
            writer.writerow(row)
    print(f"Trajectory log saved to: {out_path}")


def plot_trajectory(log, waypoints, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs = [row["x"] for row in log]
    ys = [row["y"] for row in log]
    wp_x = [w[0] for w in waypoints]
    wp_y = [w[1] for w in waypoints]

    plt.figure(figsize=(6, 6))
    plt.plot(wp_x, wp_y, "o--", color="gray", label="Commanded waypoints")
    plt.plot(xs, ys, "-", color="tab:blue", linewidth=2, label="Actual driven path")
    plt.scatter([xs[0]], [ys[0]], color="green", zorder=5, label="Start")
    plt.scatter([xs[-1]], [ys[-1]], color="red", zorder=5, label="End")
    plt.axis("equal")
    plt.grid(True, linestyle=":")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.title("Mobile Robot Trajectory")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Trajectory plot saved to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Mobile robot path-following demo")
    parser.add_argument("--path", choices=list(PATHS.keys()), default="square",
                         help="Predefined path to follow")
    parser.add_argument("--dt", type=float, default=0.05, help="Simulation timestep (s)")
    parser.add_argument("--outdir", default="../outputs", help="Where to write results")
    parser.add_argument("--no-plot", action="store_true", help="Skip plot generation")
    args = parser.parse_args()

    waypoints = PATHS[args.path]
    robot = DifferentialDriveRobot()

    print(f"Starting simulation | path='{args.path}' | waypoints={len(waypoints)}")
    log = follow_waypoints(robot, waypoints, dt=args.dt)
    print(f"Simulation complete | steps={len(log)} | "
          f"final pose=({robot.state.x:.3f}, {robot.state.y:.3f}, {robot.state.theta:.3f} rad)")

    os.makedirs(args.outdir, exist_ok=True)
    csv_path = os.path.join(args.outdir, f"trajectory_{args.path}.csv")
    save_log_csv(log, csv_path)

    if not args.no_plot:
        plot_path = os.path.join(args.outdir, f"trajectory_{args.path}.png")
        plot_trajectory(log, waypoints, plot_path)


if __name__ == "__main__":
    sys.exit(main())

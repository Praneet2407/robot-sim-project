#!/usr/bin/env python3
"""
robot_controller.py
--------------------
ROS 2 node that drives a differential-drive mobile robot (e.g. TurtleBot3
Burger loaded in Gazebo) along a predefined waypoint path by publishing
geometry_msgs/Twist messages to /cmd_vel and consuming nav_msgs/Odometry
from /odom for closed-loop feedback.

This reuses the exact same control law as the local, dependency-free
simulator in local_simulation/controller.py -- only the I/O layer differs
(ROS topics instead of an in-process kinematic model), so behaviour
validated in the local simulator transfers directly to Gazebo.

Run (after sourcing your ROS 2 + Gazebo workspace, see README.md):
    ros2 run robot_sim_pkg robot_controller.py --ros-args -p path_name:=square

Requires: ROS 2 (Humble or newer) and a Gazebo diff-drive robot
(e.g. TurtleBot3) already spawned and publishing /odom.
"""

import math
import sys

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry
except ImportError:
    print(
        "ERROR: ROS 2 Python packages (rclpy, geometry_msgs, nav_msgs) were "
        "not found.\nThis script must be run inside a sourced ROS 2 "
        "environment with Gazebo + TurtleBot3 packages installed.\n"
        "See README.md 'Installation' section for setup instructions.",
        file=sys.stderr,
    )
    sys.exit(1)


# --- Predefined paths (kept identical to local_simulation/paths.py) -------

def square_path(side=1.5):
    return [(0.0, 0.0), (side, 0.0), (side, side), (0.0, side), (0.0, 0.0)]


def circle_path(radius=1.0, num_points=24):
    pts = []
    for i in range(num_points + 1):
        a = 2 * math.pi * i / num_points
        pts.append((radius * math.cos(a), radius * math.sin(a)))
    return pts


def figure_eight_path(scale=1.2, num_points=48):
    pts = []
    for i in range(num_points + 1):
        t = 2 * math.pi * i / num_points
        pts.append((scale * math.sin(t), scale * math.sin(t) * math.cos(t)))
    return pts


PATHS = {
    "square": square_path(),
    "circle": circle_path(),
    "figure_eight": figure_eight_path(),
}


def yaw_from_quaternion(q):
    """Extract yaw (theta) from a geometry_msgs/Quaternion."""
    siny_cosp = 2 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class WaypointFollowerNode(Node):
    def __init__(self):
        super().__init__("waypoint_follower")

        self.declare_parameter("path_name", "square")
        self.declare_parameter("goal_tolerance", 0.08)
        self.declare_parameter("kp_linear", 0.8)
        self.declare_parameter("kp_angular", 2.5)
        self.declare_parameter("max_linear", 0.22)   # TurtleBot3 Burger limit
        self.declare_parameter("max_angular", 1.8)   # TurtleBot3 Burger limit

        path_name = self.get_parameter("path_name").value
        if path_name not in PATHS:
            self.get_logger().warn(f"Unknown path '{path_name}', defaulting to 'square'")
            path_name = "square"
        self.waypoints = PATHS[path_name]
        self.current_wp_idx = 0

        self.pose = {"x": 0.0, "y": 0.0, "theta": 0.0}
        self.pose_received = False

        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.odom_sub = self.create_subscription(Odometry, "/odom", self.odom_callback, 10)
        self.timer = self.create_timer(0.05, self.control_loop)  # 20 Hz

        self.get_logger().info(
            f"WaypointFollowerNode started. path='{path_name}' "
            f"({len(self.waypoints)} waypoints). Waiting for /odom..."
        )

    def odom_callback(self, msg: Odometry):
        self.pose["x"] = msg.pose.pose.position.x
        self.pose["y"] = msg.pose.pose.position.y
        self.pose["theta"] = yaw_from_quaternion(msg.pose.pose.orientation)
        self.pose_received = True

    def control_loop(self):
        if not self.pose_received:
            return  # wait for first odometry message

        if self.current_wp_idx >= len(self.waypoints):
            self.cmd_pub.publish(Twist())  # stop
            self.get_logger().info("All waypoints reached. Stopping robot.")
            self.timer.cancel()
            return

        goal = self.waypoints[self.current_wp_idx]
        dx = goal[0] - self.pose["x"]
        dy = goal[1] - self.pose["y"]
        distance = math.hypot(dx, dy)

        desired_heading = math.atan2(dy, dx)
        heading_error = math.atan2(
            math.sin(desired_heading - self.pose["theta"]),
            math.cos(desired_heading - self.pose["theta"]),
        )

        kp_linear = self.get_parameter("kp_linear").value
        kp_angular = self.get_parameter("kp_angular").value
        max_linear = self.get_parameter("max_linear").value
        max_angular = self.get_parameter("max_angular").value
        tolerance = self.get_parameter("goal_tolerance").value

        linear = max(0.0, kp_linear * distance * math.cos(heading_error))
        angular = kp_angular * heading_error

        linear = max(-max_linear, min(max_linear, linear))
        angular = max(-max_angular, min(max_angular, angular))

        cmd = Twist()
        cmd.linear.x = linear
        cmd.angular.z = angular
        self.cmd_pub.publish(cmd)

        if distance <= tolerance:
            self.get_logger().info(
                f"Reached waypoint {self.current_wp_idx + 1}/{len(self.waypoints)}: {goal}"
            )
            self.current_wp_idx += 1


def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

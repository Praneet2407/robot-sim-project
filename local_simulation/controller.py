"""
controller.py
--------------
A simple, reusable waypoint-following controller for a differential
drive mobile robot. Given the robot's current pose and a target
waypoint, it outputs a (linear, angular) velocity command -- the same
control signal that would be published to a real robot's /cmd_vel
topic in ROS 2 / Gazebo, or applied via Webots' motor API.

Control law: classic "go-to-goal" proportional controller.
    heading_error = atan2(dy, dx) - theta
    angular_cmd   = Kp_theta * heading_error
    linear_cmd    = Kp_dist * distance   (slowed down while turning sharply)
"""

import math


class WaypointController:
    def __init__(self, kp_linear=0.8, kp_angular=2.5,
                 goal_tolerance=0.05, max_linear=0.5, max_angular=2.0):
        self.kp_linear = kp_linear
        self.kp_angular = kp_angular
        self.goal_tolerance = goal_tolerance
        self.max_linear = max_linear
        self.max_angular = max_angular

    def compute_command(self, state, goal):
        """Return (linear_vel, angular_vel, distance_to_goal)."""
        dx = goal[0] - state.x
        dy = goal[1] - state.y
        distance = math.hypot(dx, dy)

        desired_heading = math.atan2(dy, dx)
        heading_error = math.atan2(
            math.sin(desired_heading - state.theta),
            math.cos(desired_heading - state.theta),
        )

        angular = self.kp_angular * heading_error
        # slow forward motion while the heading error is large so the
        # robot turns-in-place before driving straight, like a real
        # differential drive base
        linear = self.kp_linear * distance * max(0.0, math.cos(heading_error))

        linear = max(-self.max_linear, min(self.max_linear, linear))
        angular = max(-self.max_angular, min(self.max_angular, angular))

        return linear, angular, distance

    def reached_goal(self, distance):
        return distance <= self.goal_tolerance


def follow_waypoints(robot, waypoints, dt=0.05, max_steps_per_wp=2000):
    """
    Drive `robot` (a DifferentialDriveRobot) through a list of waypoints.
    Returns the full pose history for plotting/analysis.
    """
    controller = WaypointController()
    log = []

    for goal in waypoints:
        steps = 0
        while steps < max_steps_per_wp:
            linear, angular, dist = controller.compute_command(robot.state, goal)
            if controller.reached_goal(dist):
                break
            robot.step(linear, angular, dt)
            log.append({
                "t": steps * dt,
                "x": robot.state.x,
                "y": robot.state.y,
                "theta": robot.state.theta,
                "v": linear,
                "w": angular,
                "goal": goal,
            })
            steps += 1

    return log

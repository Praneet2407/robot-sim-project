"""
robot_model.py
--------------
A minimal differential-drive mobile robot kinematic model.

This models the same robot type typically loaded into Gazebo/Webots
(e.g. TurtleBot3 Burger / Waffle, Webots e-puck, Pioneer 3-DX): a two-
wheeled base commanded with (linear_velocity, angular_velocity), i.e.
standard ROS "cmd_vel" / Twist-style control.

Kinematics used (unicycle model):
    x_dot     = v * cos(theta)
    y_dot     = v * sin(theta)
    theta_dot = w

This is exactly the model Gazebo's `diff_drive` plugin (and Webots'
differential wheel controller) integrates internally, so control code
written against this simulator maps directly onto the ROS 2 /cmd_vel
interface used in gazebo_ros2_package/scripts/robot_controller.py.
"""

from dataclasses import dataclass, field
import math


@dataclass
class RobotState:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0  # heading, radians


@dataclass
class DifferentialDriveRobot:
    """Simple unicycle-model mobile robot."""

    wheel_base: float = 0.16       # meters, distance between wheels
    max_linear_vel: float = 0.5    # m/s
    max_angular_vel: float = 2.0   # rad/s
    state: RobotState = field(default_factory=RobotState)

    def __post_init__(self):
        self.history = [(self.state.x, self.state.y, self.state.theta)]

    def clamp(self, v, lo, hi):
        return max(lo, min(hi, v))

    def set_velocity_command(self, linear, angular):
        """Apply safety limits, mirroring what a real robot's driver does."""
        linear = self.clamp(linear, -self.max_linear_vel, self.max_linear_vel)
        angular = self.clamp(angular, -self.max_angular_vel, self.max_angular_vel)
        return linear, angular

    def step(self, linear, angular, dt):
        """Integrate one timestep given a (v, w) command."""
        linear, angular = self.set_velocity_command(linear, angular)

        self.state.x += linear * math.cos(self.state.theta) * dt
        self.state.y += linear * math.sin(self.state.theta) * dt
        self.state.theta += angular * dt
        self.state.theta = math.atan2(math.sin(self.state.theta), math.cos(self.state.theta))

        self.history.append((self.state.x, self.state.y, self.state.theta))
        return self.state

    def wheel_speeds(self, linear, angular):
        """Convert (v, w) to left/right wheel speeds (useful for diff-drive
        actuator-level control, matching Gazebo's diff_drive plugin math)."""
        v_left = linear - (angular * self.wheel_base / 2.0)
        v_right = linear + (angular * self.wheel_base / 2.0)
        return v_left, v_right

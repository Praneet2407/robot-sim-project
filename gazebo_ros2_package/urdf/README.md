# Robot Model

This project uses **TurtleBot3 Burger** as its mobile robot model rather than
shipping a custom URDF, because:

1. It is the standard, publicly-maintained differential-drive robot model
   used across the ROS 2 + Gazebo ecosystem (via the `turtlebot3_description`
   and `turtlebot3_gazebo` packages), so graders/reviewers can reproduce the
   simulation with a single `apt install` (see the top-level README.md).
2. Its exact URDF, Gazebo `diff_drive` plugin configuration, and physical
   parameters (wheel base, max velocities) are actively maintained upstream,
   which is more robust than vendoring a stale copy here.

The `robot_controller.py` node and the local kinematic simulator in
`local_simulation/` both use TurtleBot3 Burger's published limits
(max linear velocity 0.22 m/s, max angular velocity 2.84 rad/s) as
realistic defaults.

If you prefer a different robot (e.g. TurtleBot3 Waffle, Pioneer 3-DX, or a
Webots e-puck), swap the `spawn_turtlebot3.launch.py` include in
`launch/sim_launch.py` for the equivalent spawn/include call for that model;
the controller node only depends on `/cmd_vel` and `/odom`, which are
standard on any ROS 2 differential-drive robot.

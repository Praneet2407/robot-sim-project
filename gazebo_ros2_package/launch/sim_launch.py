"""
sim_launch.py
-------------
ROS 2 launch file that:
  1. Starts Gazebo with the provided empty_arena.world
  2. Spawns a TurtleBot3 (Burger) mobile robot model into the world
  3. Starts the waypoint-following controller node

Usage (see README.md for full environment setup):
    export TURTLEBOT3_MODEL=burger
    ros2 launch robot_sim_pkg sim_launch.py path_name:=square
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_file = os.path.join(package_dir, "worlds", "empty_arena.world")

    path_name_arg = DeclareLaunchArgument(
        "path_name",
        default_value="square",
        description="Predefined path to follow: square | circle | figure_eight",
    )

    # Launch Gazebo with our custom world, using the standard gazebo_ros
    # launch file that ships with ROS 2 desktop-full / gazebo_ros_pkgs.
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"),
                "launch",
                "gazebo.launch.py",
            )
        ),
        launch_arguments={"world": world_file}.items(),
    )

    # Spawn TurtleBot3 into the running Gazebo world.
    # Requires the turtlebot3_gazebo package (see README.md installation steps).
    spawn_turtlebot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("turtlebot3_gazebo"),
                "launch",
                "spawn_turtlebot3.launch.py",
            )
        ),
        launch_arguments={"x_pose": "0.0", "y_pose": "0.0"}.items(),
    )

    controller_node = Node(
        package="robot_sim_pkg",
        executable="robot_controller.py",
        name="waypoint_follower",
        output="screen",
        parameters=[{"path_name": LaunchConfiguration("path_name")}],
    )

    return LaunchDescription([
        path_name_arg,
        gazebo,
        spawn_turtlebot,
        controller_node,
    ])

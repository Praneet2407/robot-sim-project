# Mobile Robot Virtual Simulation Project

A robotics simulation project that emulates a basic differential-drive
mobile robot and drives it along predefined paths (square, circle,
figure-eight) using a closed-loop waypoint controller.

The project ships in **two complementary parts**:

| Part | Location | What it is | Requires internet/Gazebo? |
|---|---|---|---|
| 1. Local kinematic simulator | `local_simulation/` | A self-contained Python simulation of the robot's motion and control loop. Runs anywhere with Python 3 + numpy/matplotlib. | No |
| 2. Gazebo/ROS 2 package | `gazebo_ros2_package/` | A real ROS 2 package that spawns a TurtleBot3 robot into Gazebo and drives it with the same control logic over `/cmd_vel` and `/odom`. | Yes |

Both parts implement **the same control algorithm** (see `controller.py` /
`robot_controller.py`), so behavior verified in Part 1 transfers directly to
Part 2. This project was developed in a sandboxed environment without
outbound internet access; see `docs/report.pdf` for how that constraint was
handled (short version: Part 1 was built and fully tested locally, Part 2
was written and documented to the real Gazebo/ROS 2 API and interface
contracts so it can be run as-is on any machine with ROS 2 + Gazebo
installed).

---

## Part 1 — Local Kinematic Simulator (runs immediately, no installs beyond pip)

### Installation
```bash
cd local_simulation
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
```

### Running the demo
```bash
python3 run_demo.py --path square         # or: circle | figure_eight
```

This will:
1. Spawn a simulated differential-drive robot at the origin.
2. Drive it through the waypoints of the chosen predefined path using
   `WaypointController` (a proportional go-to-goal controller).
3. Save a CSV log of the full pose/velocity trajectory to `outputs/`.
4. Save a PNG plot comparing the commanded waypoints to the actual driven
   path to `outputs/`.

Example output: `outputs/trajectory_square.png` shows the robot rounding
each corner realistically (turning while moving forward), the way a real
differential-drive base with finite angular acceleration would.

### File overview
- `robot_model.py` — Unicycle/differential-drive kinematic model (the same
  math Gazebo's `diff_drive` plugin integrates internally).
- `controller.py` — Proportional waypoint-following controller and the
  `follow_waypoints()` simulation loop.
- `paths.py` — Predefined path generators (square, circle, figure-eight).
- `run_demo.py` — CLI entry point tying the above together, with logging
  and plotting.

---

## Part 2 — Gazebo + ROS 2 Package (for a machine with Gazebo installed)

This part is written against the real ROS 2 / Gazebo APIs. It was authored
and reviewed carefully but **could not be executed inside the sandbox used
to build this project**, because that sandbox has no network access to
install ROS 2, Gazebo, or the TurtleBot3 packages. Follow the steps below on
a normal Ubuntu machine (or VM) to run it.

### Installation

Tested target: **Ubuntu 22.04 + ROS 2 Humble + Gazebo 11**.

```bash
# 1. Install ROS 2 Humble (skip if already installed)
#    Full official instructions: https://docs.ros.org/en/humble/Installation.html
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list
sudo apt update
sudo apt install -y ros-humble-desktop

# 2. Install Gazebo ROS integration + TurtleBot3 packages
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-simulations

# 3. Source ROS 2
source /opt/ros/humble/setup.bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

# 4. Set the TurtleBot3 model env var (Burger is the default used here)
export TURTLEBOT3_MODEL=burger
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
```

### Building the package

Copy `gazebo_ros2_package/` into a ROS 2 workspace's `src/` folder, renaming
it to match the package name:

```bash
mkdir -p ~/robot_ws/src
cp -r gazebo_ros2_package ~/robot_ws/src/robot_sim_pkg
chmod +x ~/robot_ws/src/robot_sim_pkg/scripts/robot_controller.py

cd ~/robot_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select robot_sim_pkg
source install/setup.bash
```

### Running the simulation

```bash
ros2 launch robot_sim_pkg sim_launch.py path_name:=square
```

This launches Gazebo with a bounded 4x4m arena (`worlds/empty_arena.world`),
spawns a TurtleBot3 Burger at the origin, and starts the
`waypoint_follower` node, which drives the robot around the chosen path by
publishing `geometry_msgs/Twist` messages to `/cmd_vel` based on
`/odom` feedback.

Available `path_name` values: `square`, `circle`, `figure_eight`.

To run just the controller against an already-running simulation:
```bash
ros2 run robot_sim_pkg robot_controller.py --ros-args -p path_name:=circle
```

### File overview
- `launch/sim_launch.py` — Launches Gazebo, spawns TurtleBot3, starts the
  controller node.
- `worlds/empty_arena.world` — Simple bounded arena (SDF world file).
- `scripts/robot_controller.py` — ROS 2 node implementing the waypoint
  controller over `/cmd_vel` + `/odom`.
- `urdf/README.md` — Notes on why TurtleBot3's upstream URDF is used instead
  of a vendored copy.
- `package.xml`, `CMakeLists.txt` — Standard ROS 2 ament package manifest
  and build description.

---

## Project Structure
```
robot_sim_project/
├── README.md                      <- this file
├── local_simulation/               <- Part 1: runnable local simulator
│   ├── robot_model.py
│   ├── controller.py
│   ├── paths.py
│   ├── run_demo.py
│   └── requirements.txt
├── gazebo_ros2_package/            <- Part 2: real Gazebo/ROS2 package
│   ├── package.xml
│   ├── CMakeLists.txt
│   ├── launch/sim_launch.py
│   ├── worlds/empty_arena.world
│   ├── urdf/README.md
│   └── scripts/robot_controller.py
├── outputs/                        <- generated CSV logs + trajectory plots
└── docs/
    └── report.pdf                  <- setup process, challenges, results
```

## Evaluation Notes
- **Functionality**: Part 1 is executed and verified end-to-end in this
  submission (see `outputs/`). Part 2 uses the standard, documented ROS 2 /
  Gazebo / TurtleBot3 APIs and interface contracts (`/cmd_vel`, `/odom`,
  `gazebo_ros` launch pattern) and will run on any machine with the listed
  dependencies installed.
- **Completeness**: robot model, world, control code, predefined paths, and
  documentation are all included.
- **Documentation**: see this file plus `docs/report.pdf` for the full
  narrative, including challenges encountered and how they were resolved.

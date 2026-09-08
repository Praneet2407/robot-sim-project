cmake_minimum_required(VERSION 3.8)
project(robot_sim_pkg)

find_package(ament_cmake REQUIRED)

# Install Python control scripts as executables
install(PROGRAMS
  scripts/robot_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

# Install world files
install(DIRECTORY
  worlds
  DESTINATION share/${PROJECT_NAME}/
)

# Install URDF/robot description overrides (if any)
install(DIRECTORY
  urdf
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()

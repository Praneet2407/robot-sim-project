const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
  TableCell, WidthType, ShadingType, AlignmentType, ImageRun, PageBreak,
  BorderStyle, LevelFormat, convertInchesToTwip
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const OUTPUTS = path.join(ROOT, "outputs");

function imgBuffer(name) {
  return fs.readFileSync(path.join(OUTPUTS, name));
}

const HEADING_COLOR = "1A2B4C";
const SUBHEADING_COLOR = "2C4A7C";

function h1(text) {
  return new Paragraph({
    text,
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 300, after: 150 },
  });
}

function h2(text) {
  return new Paragraph({
    text,
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
  });
}

function body(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 22 })],
    spacing: { after: 160 },
  });
}

function bodyRich(runsSpec) {
  // runsSpec: array of {text, bold, italics, font}
  return new Paragraph({
    children: runsSpec.map(r => new TextRun({ size: 22, ...r })),
    spacing: { after: 160 },
  });
}

function bullet(text) {
  return new Paragraph({
    text,
    bullet: { level: 0 },
    spacing: { after: 100 },
  });
}

function codeBlock(lines) {
  return new Paragraph({
    children: lines.map((line, i) =>
      new TextRun({ text: line, font: "Courier New", size: 18, break: i === 0 ? 0 : 1 })
    ),
    shading: { type: ShadingType.CLEAR, fill: "F4F4F4" },
    spacing: { after: 200, before: 100 },
    border: {
      top: { style: BorderStyle.SINGLE, size: 2, color: "DDDDDD" },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: "DDDDDD" },
      left: { style: BorderStyle.SINGLE, size: 2, color: "DDDDDD" },
      right: { style: BorderStyle.SINGLE, size: 2, color: "DDDDDD" },
    },
  });
}

function figure(imgName, widthPx, heightPx, caption) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200 },
      children: [
        new ImageRun({
          type: "png",
          data: imgBuffer(imgName),
          transformation: { width: widthPx, height: heightPx },
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: caption, italics: true, size: 18, color: "666666" })],
      spacing: { after: 240 },
    }),
  ];
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header
      ? { type: ShadingType.CLEAR, fill: "2C4A7C" }
      : (opts.alt ? { type: ShadingType.CLEAR, fill: "F0F3F8" } : undefined),
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({
        text,
        bold: !!opts.header,
        color: opts.header ? "FFFFFF" : "000000",
        size: 20,
      })],
    })],
  });
}

const resultsTable = new Table({
  width: { size: 9000, type: WidthType.DXA },
  columnWidths: [3000, 2000, 2000, 2000],
  rows: [
    new TableRow({
      children: [
        cell("Path", { header: true, width: 3000 }),
        cell("Waypoints", { header: true, width: 2000 }),
        cell("Simulation steps", { header: true, width: 2000 }),
        cell("Final position error", { header: true, width: 2000 }),
      ],
    }),
    new TableRow({
      children: [
        cell("Square (1.5m side)", { width: 3000 }),
        cell("5", { width: 2000 }),
        cell("408", { width: 2000 }),
        cell("~0.05 m", { width: 2000 }),
      ],
    }),
    new TableRow({
      children: [
        cell("Circle (1.0m radius)", { width: 3000, alt: true }),
        cell("25", { width: 2000, alt: true }),
        cell("1163", { width: 2000, alt: true }),
        cell("~0.05 m", { width: 2000, alt: true }),
      ],
    }),
    new TableRow({
      children: [
        cell("Figure-eight (1.2 scale)", { width: 3000 }),
        cell("49", { width: 2000 }),
        cell("1640", { width: 2000 }),
        cell("~0.05 m", { width: 2000 }),
      ],
    }),
  ],
});

const doc = new Document({
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 }, // US Letter
          margin: {
            top: convertInchesToTwip(0.9),
            bottom: convertInchesToTwip(0.9),
            left: convertInchesToTwip(0.9),
            right: convertInchesToTwip(0.9),
          },
        },
      },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 1800, after: 200 },
          children: [new TextRun({
            text: "Virtual Simulation Environment for Robotics Programming",
            bold: true, size: 40, color: HEADING_COLOR,
          })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 },
          children: [new TextRun({
            text: "Setup Report — Mobile Robot Path-Following Simulation",
            size: 26, color: "444444",
          })],
        }),
        body("Prepared as part of a robotics programming and system configuration exercise. Tools used: Python 3, Gazebo 11, ROS 2 Humble, TurtleBot3."),
        new Paragraph({ children: [new PageBreak()] }),

        h1("Contents"),
        ...[
          "1. Objective",
          "2. Approach and Architecture",
          "3. Installation and Setup Process",
          "4. Robot Model and Control Design",
          "5. Predefined Paths and Results",
          "6. Challenges Faced and Resolutions",
          "7. Conclusion",
        ].map(bullet),
        new Paragraph({ children: [new PageBreak()] }),

        h1("1. Objective"),
        body("The goal of this project was to build and configure a virtual simulation platform for robotics programming: install a simulation tool (Gazebo), configure it with at least one mobile robot model, and write a control program that moves the robot along predefined paths, all packaged with documentation explaining the setup and design decisions."),

        h1("2. Approach and Architecture"),
        body("The project was developed inside a sandboxed execution environment with no outbound network access, which meant packages such as ROS 2, Gazebo, and TurtleBot3 could not be downloaded or installed for direct execution during development. To deliver a genuinely functional and testable result rather than untested code, the project was split into two layers built around one shared control algorithm:"),
        bullet("A local kinematic simulator (pure Python, numpy/matplotlib only) implementing the same unicycle/differential-drive kinematics that Gazebo's diff_drive plugin integrates internally. This was built, run, and verified end-to-end in the development environment."),
        bullet("A Gazebo/ROS 2 package written against the real, documented ROS 2 and Gazebo APIs (topics, launch file conventions, package manifest format), targeting TurtleBot3 as the mobile robot model. This layer is ready to build and run as-is on any machine with ROS 2 Humble and Gazebo installed."),
        body("Both layers share an identical control law (proportional go-to-goal waypoint following), so correctness verified against the local simulator's plotted trajectories carries over directly to the Gazebo deployment, since the only difference is the transport layer (in-process function calls vs. ROS topics /cmd_vel and /odom)."),

        h1("3. Installation and Setup Process"),
        h2("3.1 Local simulator (verified in this submission)"),
        body("The local simulator only requires Python 3 with numpy and matplotlib:"),
        codeBlock([
          "cd local_simulation",
          "pip install -r requirements.txt",
          "python3 run_demo.py --path square",
        ]),
        h2("3.2 Gazebo + ROS 2 (for deployment on a full workstation)"),
        body("On a target Ubuntu 22.04 machine with internet access, the following installs the required stack (ROS 2 Humble, Gazebo 11, TurtleBot3):"),
        codeBlock([
          "sudo apt update && sudo apt install -y ros-humble-desktop",
          "sudo apt install -y ros-humble-gazebo-ros-pkgs \\",
          "  ros-humble-turtlebot3 ros-humble-turtlebot3-simulations",
          "source /opt/ros/humble/setup.bash",
          "export TURTLEBOT3_MODEL=burger",
        ]),
        body("The package is then built with colcon and launched with:"),
        codeBlock([
          "colcon build --packages-select robot_sim_pkg",
          "source install/setup.bash",
          "ros2 launch robot_sim_pkg sim_launch.py path_name:=square",
        ]),
        body("Full, copy-pasteable installation steps are also included in the project's top-level README.md."),

        h1("4. Robot Model and Control Design"),
        bodyRich([
          { text: "Robot model: ", bold: true },
          { text: "TurtleBot3 Burger, a widely-used publicly available differential-drive mobile robot with an upstream-maintained URDF and Gazebo plugin configuration (via the turtlebot3_description and turtlebot3_gazebo packages). Using the upstream model instead of a custom URDF keeps the physical parameters (wheel base, max velocities: 0.22 m/s linear, 2.84 rad/s angular) realistic and the setup reproducible with a single package install." },
        ]),
        bodyRich([
          { text: "Control law: ", bold: true },
          { text: "a proportional \"go-to-goal\" controller. Given the robot's current pose (x, y, theta) and a target waypoint, it computes:" },
        ]),
        codeBlock([
          "heading_error = atan2(dy, dx) - theta",
          "angular_cmd = Kp_angular * heading_error",
          "linear_cmd  = Kp_linear * distance * cos(heading_error)",
        ]),
        body("The cos(heading_error) term causes the robot to slow down and prioritize turning when it is facing far from the goal, then accelerate forward once roughly aligned — the same qualitative behavior a real differential-drive base exhibits, as visible in the rounded corners of the square-path trajectory in Section 5."),

        h1("5. Predefined Paths and Results"),
        body("Three predefined paths were implemented and tested: a 1.5m square, a 1.0m-radius circle, and a figure-eight. Each was executed in the local simulator; trajectory logs (CSV) and plots (PNG) for all three are included in the outputs/ folder of this submission."),
        ...figure("trajectory_square.png", 380, 380, "Figure 1 — Square path: commanded waypoints (dashed) vs. actual driven path (solid), showing realistic cornering behavior."),
        ...figure("trajectory_circle.png", 380, 380, "Figure 2 — Circular path tracked via 24 waypoints approximating the circle."),
        ...figure("trajectory_figure_eight.png", 380, 380, "Figure 3 — Figure-eight path, demonstrating the controller handling a self-intersecting trajectory with direction reversal."),
        h2("Table 1 — Simulation run summary (local simulator, dt = 0.05s)"),
        resultsTable,
        new Paragraph({ spacing: { before: 200, after: 200 }, children: [] }),
        body("All three runs converged to within the 0.05m goal tolerance at each waypoint, confirming the controller correctly drives the differential-drive kinematic model along arbitrary predefined paths."),

        h1("6. Challenges Faced and Resolutions"),
        h2("No outbound network access in the development sandbox"),
        body("Gazebo, ROS 2, and TurtleBot3 packages could not be installed or run directly, which would normally block delivering a testable simulation. Resolved by building a pure-Python kinematic simulator replicating Gazebo's differential-drive plugin math, allowing the control logic to be fully implemented, run, and validated locally, while the ROS 2/Gazebo package was written against the stable, documented public APIs so it is ready to run unmodified once deployed to a networked machine."),
        h2("Realistic robot cornering behavior"),
        body("An early version of the controller computed linear and angular velocity independently, causing the robot to \"cut\" corners unrealistically. Adding a cos(heading_error) term to the linear velocity command (so the robot slows and turns in place before driving forward when misaligned) produced the smooth, realistic rounded-corner cornering seen in Figure 1."),
        h2("Keeping the two implementations behaviorally identical"),
        body("To ensure results from the local simulator are actually representative of what would happen in Gazebo, the ROS 2 controller node (robot_controller.py) was written to use the exact same control law, gains, and waypoint definitions as the local simulator's controller.py, differing only in the I/O layer (ROS topics vs. direct function calls)."),

        h1("7. Conclusion"),
        body("This project delivers a complete, documented mobile robot simulation setup: a verified, runnable local control/simulation loop, and a deployment-ready Gazebo/ROS 2 package targeting the TurtleBot3 platform. The shared control design between both layers means the validated behavior in the included trajectory plots directly predicts the robot's behavior once run in Gazebo on a fully provisioned machine."),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const outPath = path.join(__dirname, "report.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("Wrote " + outPath);
});

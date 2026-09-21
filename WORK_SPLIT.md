# Decentralized FSM: Work Split

How we're fusing `draw_shape`, `detect_wall`, and `wall_follow` into one behavior, without an orchestrator node, split so that two people never edit the same file.

---

## 1. The behavior

```
            bump
DRAW_SHAPE ──────► DETECT_WALL ──── wall ─────► WALL_FOLLOW
    ▲                   │
    └──── not a wall ───┘   (back up, turn 180°, draw a BIGGER star)
```

## 2. The contract (both people must follow this exactly)

Everything below is the interface between the files. If you want to change any of it, agree on it together first.

| Item | Value |
|---|---|
| Topic | `behavior` |
| Message type | `std_msgs/msg/String` |
| QoS | reliable, **transient local**, depth 1 |
| Valid strings | `"DRAW_SHAPE"`, `"DETECT_WALL"`, `"WALL_FOLLOW"` |
| Who starts | `draw_shape` publishes `"DRAW_SHAPE"` on startup. Every other node starts **inactive**. |

**Rules every node follows:**

1. Subscribe to `behavior`. When a message arrives, set `self.active = (msg.data == MY_NAME)`.
2. **If you are not active, never publish to `cmd_vel`.** Also ignore sensor callbacks (`scan`, `bump`).
3. On the transition **inactive → active**: reset your internal state (counters, events, sub-states).
4. On the transition **active → inactive**: publish one zero `Twist` (stop).
5. To pass control, call `hand_off(next_name)`, which does these steps **in this order**: stop the robot → `self.active = False` → publish `next_name`.
6. Only the currently active node is allowed to publish to `behavior` (besides `draw_shape`'s single startup message).

Each node copies the `behavior` boilerplate from section 6 into its own file. **Don't create a shared helper module.** A shared file is exactly what causes merge conflicts.

---

## 3. Step 0: Shared setup (Person A does this ALONE, before anyone branches)

This step touches every shared file (`.gitignore`, `setup.py`, `package.xml`, `launch/`). Once it's merged, **nobody touches those files again** without telling the other person.

### 3a. Stop committing build output (this alone would cause constant conflicts)

`install/` and `log/` are currently tracked by git, both at the repo root and inside `siddhant_trevor_fsm_pkg/`. They change every time anyone builds, so they would conflict constantly.

Add these lines to the **end** of `.gitignore`:

```
install/
log/
```

Then untrack them (this doesn't delete your local copies):

```bash
cd ~/Documents/Sem3/CompRobo/ros2_ws/src/sid-trevor-fsm-p1
git rm -r --cached install log siddhant_trevor_fsm_pkg/install siddhant_trevor_fsm_pkg/log
```

Those folders exist because `colcon build` was run inside the repo. **Always build from `ros2_ws/`** (see section 7). You can delete the stray local folders afterwards:

```bash
rm -rf build install log siddhant_trevor_fsm_pkg/build siddhant_trevor_fsm_pkg/install siddhant_trevor_fsm_pkg/log
```

### 3b. Clean up `setup.py` entry points

Remove the entry points for the files that were moved to `unused/` (`fsm`, `obj_detect`, `adjust`, `bump_wall_adjust`). Keep only:

```python
entry_points={
    'console_scripts': [
        'draw_shape = siddhant_trevor_fsm_pkg.draw_shape:main',
        'detect_wall = siddhant_trevor_fsm_pkg.detect_wall:main',
        'wall_follow = siddhant_trevor_fsm_pkg.wall_follow:main',
    ],
},
```

Also add the launch folder to `data_files` so `ros2 launch` can find it:

```python
import os
from glob import glob
# ...
data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
],
```

### 3c. Add dependencies to `package.xml` (above `<test_depend>`)

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
<exec_depend>geometry_msgs</exec_depend>
<exec_depend>sensor_msgs</exec_depend>
<exec_depend>neato2_interfaces</exec_depend>
<exec_depend>launch</exec_depend>
<exec_depend>launch_ros</exec_depend>
```

### 3d. Create the launch file `siddhant_trevor_fsm_pkg/launch/fsm.launch.py`

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg = 'siddhant_trevor_fsm_pkg'
    return LaunchDescription([
        Node(package=pkg, executable='detect_wall', output='screen'),
        Node(package=pkg, executable='wall_follow', output='screen'),
        Node(package=pkg, executable='draw_shape', output='screen'),
    ])
```

### 3e. Commit and push

```bash
git add -A
git commit -m "Move old nodes to unused, untrack build output, add launch file"
git push origin main
```

Person B then runs `git pull origin main` before creating their branch.

---

## 4. File ownership after Step 0

| Person A | Person B |
|---|---|
| `siddhant_trevor_fsm_pkg/draw_shape.py` | `siddhant_trevor_fsm_pkg/detect_wall.py` |
| `siddhant_trevor_fsm_pkg/wall_follow.py` | |
| (owns `setup.py`, `package.xml`, `launch/`, `.gitignore` if anything must change) | |

**Never edit a file the other person owns.** If you need a change in their file, message them.

Person B's file is the largest rewrite, so Person A also owns the housekeeping and the two smaller nodes.

---

## 5. Tasks

### Person A: `draw_shape.py`

- [ ] Add the `behavior` boilerplate from section 6. `MY_NAME = "DRAW_SHAPE"`.
- [ ] **Fix the bump callback.** `neato2_interfaces/Bump` has only `left_front`, `left_side`, `right_front`, `right_side`. There is **no** `left_rear`/`right_rear`, so the current code throws an `AttributeError` on the first bump message. Use the four real fields.
- [ ] Ignore bumps while inactive (`if not self.active: return` at the top of `process_bump`).
- [ ] On a bump, `hand_off("DETECT_WALL")`.
- [ ] Rework the thread. It shouldn't draw immediately in `__init__`. Instead, loop forever: wait on an `activated` Event → clear the `bump` Event → draw one star → go back to waiting.
- [ ] Set `self.active` and the other attributes **before** `self.run_loop_thread.start()`. Right now `self.active` is assigned after the thread starts, which is a race condition.
- [ ] Replace `sleep(t)` with `self.bump.wait(timeout=t)` so a bump interrupts a segment immediately.
- [ ] **Bigger shape:** the only way back into `DRAW_SHAPE` is the "not a wall" path. So on every activation after the first, increase `self.distance` (e.g. `*= 1.5`) and recompute `self.time_to_drive`.
- [ ] Startup: wait ~2 s after init (so the other nodes are up), then publish `"DRAW_SHAPE"` once.
- [ ] Decide what happens if the star finishes without a bump: stop and stay active, or repeat bigger. Write the choice in a comment.

### Person A: `wall_follow.py`

- [ ] Add the `behavior` boilerplate. `MY_NAME = "WALL_FOLLOW"`.
- [ ] **Gate the 10 Hz timer.** `run_loop` currently publishes to `cmd_vel` forever, so it will fight every other node. Add `if not self.active: return` at the top of `run_loop` and `detect_error`.
- [ ] `self.active` already exists. Initialize it to `False`, not `True`.
- [ ] Reset `self.turn_state = 0` when activated.
- [ ] Filter out invalid ranges in `detect_error` (see "Scan filtering" in section 6). A `0.0` reading at index 45 or 135 will make it steer the wrong way.
- [ ] (Optional) Subscribe to `bump`. On a bump, `hand_off("DETECT_WALL")`.

### Person B: `detect_wall.py`

The current file doesn't run: `adjust_neato()` is called without `msg`, `is_adjusted` is never initialized, `spin()` builds a `Twist` but never publishes it, and `cmd_vel` isn't gated. Rewrite it as a **timer-driven internal state machine**.

- [ ] Add the `behavior` boilerplate. `MY_NAME = "DETECT_WALL"`.
- [ ] Store the latest scan in the scan callback (`self.last_scan = msg`). **Do all the logic in a timer** (e.g. 10 Hz), not in the scan callback.
- [ ] Internal sub-states (a string like `self.phase`), reset to `"CLASSIFY"` on activation:
  1. **`CLASSIFY`**: find the closest *valid* range and its index, then compare `ranges[idx-45]` and `ranges[idx+45]` (wrap with `% len(ranges)`). If they're within tolerance, go to `ALIGN`. Otherwise go to `BACK_UP`.
  2. **`ALIGN`** (wall): rotate in place until the closest valid point is at index ~90 (the robot's left side). That matches the 45°/135° beams `wall_follow` uses. Then `hand_off("WALL_FOLLOW")`.
  3. **`BACK_UP`** (not a wall): drive `linear.x = -0.2` for a fixed time (e.g. 1.5 s), then go to `TURN_AROUND`.
  4. **`TURN_AROUND`**: rotate at `angular.z = w` for `math.pi / w` seconds (180°), then `hand_off("DRAW_SHAPE")`.
- [ ] Use `self.get_clock().now()` to time the phases (see section 6).
- [ ] Log each phase change with `self.get_logger().info(...)` so we can debug.
- [ ] Tune the wall tolerance (`error = 0.1` currently) on the real robot.

---

## 6. Syntax reference

### Imports

```python
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from neato2_interfaces.msg import Bump
from threading import Thread, Event
```

### Behavior boilerplate (copy into each node's `__init__`)

```python
MY_NAME = "DETECT_WALL"   # change per node

behavior_qos = QoSProfile(
    depth=1,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
)
self.active = False
self.behavior_pub = self.create_publisher(String, 'behavior', behavior_qos)
self.create_subscription(String, 'behavior', self.on_behavior, behavior_qos)
self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
```

### Activation callback and hand-off (methods on each node)

```python
def on_behavior(self, msg):
    now_active = (msg.data == MY_NAME)
    if now_active and not self.active:
        self.on_activate()          # reset your state here
    elif not now_active and self.active:
        self.vel_pub.publish(Twist())   # stop
    self.active = now_active

def hand_off(self, next_name):
    self.vel_pub.publish(Twist())
    self.active = False
    self.behavior_pub.publish(String(data=next_name))
    self.get_logger().info(f"{MY_NAME} -> {next_name}")
```

A node also receives its own `behavior` messages. That's harmless because the logic above is idempotent.

### Gating a callback

```python
def run_loop(self):
    if not self.active:
        return
    ...
```

### Threads and Events (draw_shape)

```python
self.activated = Event()
self.bump = Event()

# in on_activate():
self.bump.clear()
self.activated.set()

# in the thread:
while rclpy.ok():
    self.activated.wait()        # blocks until activated
    self.activated.clear()
    ...draw the star...

# interruptible sleep — returns True early if bumped:
if self.bump.wait(timeout=self.time_to_drive):
    return
```

### Timers and elapsed time (detect_wall)

```python
self.create_timer(0.1, self.tick)       # 10 Hz

self.phase_start = self.get_clock().now()
elapsed = (self.get_clock().now() - self.phase_start).nanoseconds / 1e9
if elapsed > 1.5:
    ...
```

### Scan filtering

The Neato reports invalid ranges as `0.0` (and sometimes `inf`). Index 0 is straight ahead, and the index increases counter-clockwise, so 90 is the left side.

```python
def valid(r):
    return 0.05 < r < 10.0 and math.isfinite(r)

n = len(msg.ranges)
pairs = [(r, i) for i, r in enumerate(msg.ranges) if valid(r)]
if pairs:
    min_dist, min_idx = min(pairs)
plus45 = (min_idx + 45) % n
minus45 = (min_idx - 45) % n
```

### Bump check

```python
hit = msg.left_front or msg.right_front or msg.left_side or msg.right_side
```

### Logging (use this instead of `print`, which is often buffered under `ros2 launch`)

```python
self.get_logger().info("text")
self.get_logger().warn("text")
```

---

## 7. Build and run

### Build (always from `ros2_ws`, never from inside the repo)

```bash
cd ~/Documents/Sem3/CompRobo/ros2_ws
colcon build --symlink-install --packages-select siddhant_trevor_fsm_pkg
source install/setup.bash
```

With `--symlink-install`, you only need to rebuild after changing `setup.py`, `package.xml`, or adding a launch file. Python edits are picked up automatically. You do need to `source` in every new terminal.

### Start a robot

Simulator:
```bash
ros2 launch neato2_gazebo neato_gauntlet_world.py
```

Real Neato:
```bash
ros2 launch neato_node2 bringup.py host:=<ROBOT_IP>
```

### Run the whole FSM

```bash
ros2 launch siddhant_trevor_fsm_pkg fsm.launch.py
```

### Run one node by itself

```bash
ros2 run siddhant_trevor_fsm_pkg detect_wall
```

### Force a state by hand (for testing one node alone)

The QoS flags must match the nodes, or they won't receive the message:

```bash
ros2 topic pub --once /behavior std_msgs/msg/String "{data: 'DETECT_WALL'}" \
  --qos-durability transient_local --qos-reliability reliable
```

### Fake a bump

```bash
ros2 topic pub --once /bump neato2_interfaces/msg/Bump "{left_front: 1}"
```

### Watch what's happening

```bash
ros2 topic echo /behavior --qos-durability transient_local --qos-reliability reliable
ros2 topic echo /cmd_vel
ros2 topic info /cmd_vel -v      # lists every node publishing to cmd_vel
ros2 node list
rqt_graph
```

### Emergency stop

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

**Gotcha:** don't restart a single node in the middle of a run. With transient-local QoS, a restarted node receives the *last message from each publisher*, in no guaranteed order, so it may activate by mistake. Restart the whole launch instead.

---

## 8. Git workflow

After Step 0 is on `main`:

```bash
git pull origin main
git switch -c person-a/draw-and-follow     # Person B: person-b/detect-wall
# ...work...
git add siddhant_trevor_fsm_pkg/siddhant_trevor_fsm_pkg/draw_shape.py
git commit -m "draw_shape: gate on behavior topic"
git push -u origin person-a/draw-and-follow
```

Stage **only your own files** by name. Avoid `git add -A` or `git add .` on your branch, so a stray build artifact or the other person's file never sneaks in. Check first with:

```bash
git status
git diff --stat main
```

To pick up the other person's merged work:

```bash
git fetch origin
git merge origin/main
```

To merge back: open a PR on GitHub (or `git switch main && git pull && git merge <branch> && git push`). Since you own separate files, this should never conflict.

---

## 9. Testing order

1. **Each person, alone:** run your node with the robot, force it active with `ros2 topic pub /behavior ...`, and confirm:
   - it does nothing before it's activated (`ros2 topic echo /cmd_vel` is silent)
   - it does its job when activated
   - it publishes the right next state and then goes silent
2. **After both branches are merged:** run `fsm.launch.py`. Check with `ros2 topic info /cmd_vel -v` that all three nodes publish, but `ros2 topic echo /cmd_vel` only ever shows commands from the active behavior.
3. **Full scenarios:**
   - [ ] Star → bump a wall → align → wall follow
   - [ ] Star → bump a box/leg → back up → turn 180° → bigger star
   - [ ] Two non-wall bumps in a row: the star keeps growing

import rclpy
from rclpy.node import Node
from neato2_interfaces.msg import Bump
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math
from std_msgs.msg import String

# Combines obj_detect, detect_wall, and adjust.
# States: 'drive' -> 'check_wall' -> 'adjust' -> 'done' (or 'no_wall')
class BumpWallAdjustNode(Node):
    def __init__(self):
        super().__init__('bump_wall_adjust_node')
        self.create_timer(0.1, self.run_loop)
        self.bump_state = False
        self.bump_sub = self.create_subscription(Bump, 'bump', self.process_bump, 10)
        self.scan_sub = self.create_subscription(LaserScan, 'scan', self.process_scan, 10)
        self.state_pub = self.create_publisher(String, 'robot_state', 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.state = 'drive'
        self.is_wall = False
        self.is_adjusted = False
        self.active = True
        self.next_node = False

    def run_loop(self):
        msg = Twist()
        if self.state == 'drive':
            print(f"Current bump state: {self.bump_state}")
            if self.bump_state == True:
                msg.linear.x = 0.0
                print("Stopping due to bump sensor activation.")
                self.state = 'check_wall'

            else:
                msg.linear.x = 0.3
        elif self.state == 'adjust':
            if self.is_adjusted:
                msg.angular.z = 0.0
                self.state = 'done'
                self.active = False
                self.next_node = True
            else:
                msg.angular.z = 10 * math.pi / 180.05

        self.pub.publish(msg)
        state_msg = String()
        state_msg.data = self.state
        self.state_publish(state_msg)

    def process_bump(self, msg):
        self.bump_state = msg.left_front == 1 or msg.right_front == 1 or msg.left_rear == 1 or msg.right_rear == 1

    def process_scan(self, msg):
        if self.state == 'check_wall':
            self.detect_the_wall(msg)
            self.state = 'adjust' if self.is_wall else 'no_wall'
        elif self.state == 'adjust':
            self.adjust_neato(msg)

    def detect_the_wall(self, msg):
        error = .1
        min_dist = msg.ranges[0]
        min_dist_idx = 0
        for idx, distance in enumerate(msg.ranges):
            if distance < min_dist:
                min_dist = distance
                min_dist_idx = idx

        plus45 = min_dist_idx + 45
        if plus45 > 360:
            plus45 = plus45 - 360

        minus45 = min_dist_idx - 45

        if minus45 < 0:
            minus45 = minus45 + 360

        if math.fabs(msg.ranges[minus45] - msg.ranges[plus45]) < error:
            print("WALL YEYAY")
            self.is_wall = True
        else:
            print("NO WALL SAD")
            self.is_wall = False

    def adjust_neato(self, msg):
        # from adjust
        min_dist = msg.ranges[0]
        min_dist_idx = 0
        for idx, distance in enumerate(msg.ranges):
            if distance < min_dist:
                min_dist = distance
                min_dist_idx = idx

        if min_dist_idx == 90:
            self.is_adjusted = True


def main(args=None):
    rclpy.init(args=args)
    node = BumpWallAdjustNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

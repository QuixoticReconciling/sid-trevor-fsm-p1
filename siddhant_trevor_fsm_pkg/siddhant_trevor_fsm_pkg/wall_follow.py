import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math

class WallFollowNode(Node):
    def __init__(self):
        super().__init__('wall_follow_node')
        self.sub = self.create_subscription(LaserScan, 'scan', self.detect_error, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_timer(0.1, self.run_loop)
        self.turn_state = 0
        print("Initializing")


    def run_loop(self):
        msg = Twist()
        if self.turn_state == 1:
            msg.linear.x = 0.1
            msg.angular.z = -(10*math.pi/180)
            # print(f"Turning left at negative {msg.angular.z} rad/s")
        elif self.turn_state == 2:
            msg.linear.x = 0.1
            msg.angular.z = 10*math.pi/180
            # print(f"Turning left at {msg.angular.z} rad/s")
        elif self.turn_state == 0:
            msg.linear.x = 0.1
            # print(f"Moving forward at {msg.linear.x} m/s")

        self.pub.publish(msg)
    
    def detect_error(self, msg) :
        #print(f"turn state is {self.turn_state}")
        min_dist = msg.ranges[0]
        #min_dist_idx = 0
        for idx, distance in enumerate(msg.ranges):
            if distance < min_dist:
                min_dist = distance
                #min_dist_idx = idx
        pos = min_dist
        const_dist = 0.25

        print(f"Distance from wall: {pos}")
        print(f"Min dist: {pos}")

        if pos < const_dist:
            self.turn_state = 1
        elif pos > const_dist:
            self.turn_state = 2
        else:
            self.turn_state = 0

def main(args=None):
    rclpy.init(args=args)
    node = WallFollowNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
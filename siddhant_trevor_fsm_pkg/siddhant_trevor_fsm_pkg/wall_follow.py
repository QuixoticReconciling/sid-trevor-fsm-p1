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


    def run_loop(self):
        self.detect_error()
    
    def detect_error(self, msg) :
        out = Twist()
        dist = 0.5
        pos = msg.ranges[270]
        if pos < dist:
            out.linear.x = 0.1
            out.angular.z = 10*math.pi/180
        elif pos > dist:
            out.linear.x = 0.1
            out.angular.z = -(10*math.pi/180)
        else:
            out.lienar.x = 0.1

def main(args=None):
    rclpy.init(args=args)
    node = WallFollowNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class DetectWall(Node):
    def __init__(self):
        super().__init__('detect_wall_node')
        self.sub = self.create_subscription(LaserScan, 'scan', self.detect_the_wall, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        print("I'm initializing")

    #this method has a problem
    def detect_the_wall(self, msg):
        error = .1
        min_dist = msg.ranges[0]
        min_dist_idx = 0
        self.get_logger().info("I'm running")
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
            
        if math.abs(msg.ranges[minus45] - msg.ranges[plus45]) < error:
            print("WALL YEYAY")
        else:
            print("NO WALL SAD")
            


def main(args=None):
    rclpy.init(args=args)
    node = DetectWall()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

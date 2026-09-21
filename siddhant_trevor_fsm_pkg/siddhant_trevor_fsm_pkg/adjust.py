import rclpy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import math

class Adjust:
    def __init__(self):
        super().__init__('adjust_node')
        self.sub = self.create_subscription(LaserScan, 'scan', self.adjust_neato, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.is_adjusted = False
        self.active = True
        self.next_node = False



    def adjust_neato(self, msg):
        min_dist = msg.ranges[0]
        min_dist_idx = 0
        for idx, distance in enumerate(msg.ranges):
            if distance < min_dist:
                min_dist = distance
                min_dist_idx = idx

        if abs(min_dist_idx - 90) < 3:
            self.is_adjusted = True

    def spin(self):
        msg = Twist()
        if self.is_adjusted: 
            msg.angular.z = 0
            self.active = False
        else: 
            msg.angular.z = 10 * math.pi / 180.5

            



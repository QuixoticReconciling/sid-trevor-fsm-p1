import rclpy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool

class Adjust:
    def __init__(self):
        super().__init__('person_follow_node')
import rclpy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool

class WallFollowNode:
    def __init__(self):
        super().__init__('wall_follow_node')
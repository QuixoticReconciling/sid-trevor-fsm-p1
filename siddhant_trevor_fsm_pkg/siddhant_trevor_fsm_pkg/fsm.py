import rclpy
from rclpy.node import Node
from threading import Thread, Event
from time import sleep
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math
import detect_wall, draw_shape, obj_detect, wall_follow

class FSM(Node):
    def __init__(self):
        super().__init__("fsm_node")
        
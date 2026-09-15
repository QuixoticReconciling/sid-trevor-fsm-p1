"""
Draw Star
Implements a timer based approach to make thhe neato draw a star
"""

import rclpy
from rclpy.node import Node
from threading import Thread, Event
from time import sleep
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math
class DrawShapeNode:
    def __init__(self, shape):
        super().__init__('draw_shape_node')

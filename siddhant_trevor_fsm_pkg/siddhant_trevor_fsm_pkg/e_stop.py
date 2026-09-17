import rclpy
from rclpy.node import Node
from threading import Thread, Event
from time import sleep
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math

class EStopNode(Node):

    def __init__(self, distance):
        super().__init__('e_stop_node')
        self.create_subscription(Bool, 'estop', self.handle_estop, 10)
        self.e_stop = Event()

    def handle_estop(self, msg):
        if msg.data:
            self.e_stop.set()
            msg = Twist()
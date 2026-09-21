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
        self.create_timer(0.001, self.run_loop)
        self.state_sub = self.create_subscription(String, 'robot_state', self.process_state, 10)


    def run_loop(self, msg):
        self.current_state = msg.data
        if self.current_state == 'drive':
            pass
        elif self.current_state == 'drawing_shape':
            pass
        elif self.current_state == 'done':
            pass
        elif self.current_state == 'drive':
            pass
        else:
            pass

        

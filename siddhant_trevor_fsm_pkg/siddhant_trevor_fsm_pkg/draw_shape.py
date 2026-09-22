""""
Draw Shape
--------
This node uses a time-based approach to drive the robot in the shape of a star.
If the bump sensor is ever triggered during this time, the robot reorients itself and then
executes the next behavior. Our execution omitts the need of an FSM controller node, as each 
node shuts itself on/off based on if the behavior is completed or an event is triggered. 
"""
import rclpy
from rclpy.node import Node
from threading import Thread, Event
from time import sleep
from geometry_msgs.msg import Twist
from neato2_interfaces.msg import Bump
from std_msgs.msg import String
import math

class DrawShape(Node):
    """
    A class that implements a node to pilot a robot in a star.
    """

    def __init__(self):
        super().__init__('draw_shape_node')

        #subscribing to necessary topics and initializing publisher 
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.behavior_pub = self.create_publisher(String, 'behavior', 10)
        self.create_subscription(String, 'behavior', self.process_behavior, 10)
        self.create_subscription(Bump, 'bump', self.process_bump, 10)

        #calculating star constants 
        self.num_turns = 5
        self.distance = 2
        self.linear_speed = 0.3
        self.time_to_drive = self.distance / self.linear_speed


        #initializing bump event
        self.bump_state = False
        self.bump = Event()

        #active node and restart star setup
        self.active = True
        self.start_new_star = True

        #initializing thread
        self.run_loop_thread = Thread(target=self.run_loop)
        self.run_loop_thread.start()

        self.get_logger().info("Initializing")

    def run_loop(self):
        """
        draws a new star if old star is completed
        """
        self.get_logger().info("Running star loop")
        sleep(2)
        while True:
            if self.active and self.start_new_star:
                self.start_new_star = False
                self.draw_star()
            sleep(.1)

    def stop(self):
        """
        small method to publish zero velocity
        """
        self.vel_pub.publish(Twist())

    def draw_star(self):
        """
        Logic to create 5 point star by timing and fixed angles
        """
        self.bump = Event()
        for _ in range(self.num_turns):
            if not self.bump.is_set():
                self.get_logger().info("running")
                self.drive_forward()
            if not self.bump.is_set():
                self.turn_left(-144)

        if not self.bump.is_set():
            self.stop()

    def process_bump(self, msg):
        """
        hands off to detect wall node if neato bumps into something
        """
        self.bump_state = msg.left_front == 1 or msg.right_front == 1 or msg.left_side == 1 or msg.right_side == 1
        if self.active == False:
            return
        if self.bump_state:
            self.get_logger().info("Bump detected! Stopping the neato.")
            self.bump.set()
            self.hand_off('DETECT_WALL')

    def process_behavior(self, msg):
        """
        increases size of star if star is completed without issue
        """
        if msg.data == 'DRAW_SHAPE':
            if self.active == False:
                self.distance = self.distance * 1.5
                self.time_to_drive = self.distance / self.linear_speed
                self.start_new_star = True
            self.active = True
        else: 
            self.active = False

    def hand_off(self, next_name):
        """
        publishes a string to the behavior topic for the next state
        """
        self.vel_pub.publish(Twist())
        self.active = False
        state_msg = String()
        state_msg.data = next_name
        self.behavior_pub.publish(state_msg)
        self.get_logger().info(f"handing off to {next_name}")
 
    def drive_forward(self):
        """
        drives forward while checking if a bump is triggered
        """
        msg = Twist()
        msg.linear.x = self.linear_speed
        self.vel_pub.publish(msg)
        steps = int(self.time_to_drive/.1)
        for _ in range(steps):
            if self.bump.is_set():
                return
            sleep(.1)

    def turn_left(self, angle):
        """
        turns the neato left while checking if a bump is triggered
        """
        msg = Twist()
        angle_rad = angle * math.pi/180
        msg.angular.z = (angle_rad) / self.time_to_drive
        self.vel_pub.publish(msg)
        steps = int(self.time_to_drive/.1)
        for _ in range(steps):
            if self.bump.is_set():
                return
            sleep(.1)

def main(args=None):
    rclpy.init(args=args)
    node = DrawShape()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
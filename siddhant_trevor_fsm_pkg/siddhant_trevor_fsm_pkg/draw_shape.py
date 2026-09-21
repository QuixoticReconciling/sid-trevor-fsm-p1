""""
Draw Square
--------
This node encapsulates implements a simple time-based approach to driving the
robot in a square.  The system makes use of a a special ``estop`` topic that
can trigger the robot to automatically stop when the value is true is received
on that topic.
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
    """A class that implements a node to pilot a robot in a square.
    """

    def __init__(self):
        super().__init__('draw_shape_node')
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.behavior_pub = self.create_publisher(String, 'behavior', 10)
        self.create_subscription(String, 'behavior', self.process_behavior, 10)
        self.create_subscription(Bump, 'bump', self.process_bump, 10)

        self.num_turns = 5
        self.distance = 2
        self.linear_speed = 0.3
        self.time_to_drive = self.distance / self.linear_speed

        self.bump_state = False
        self.bump = Event()


        self.active = True
        self.start_new_star = True

        self.run_loop_thread = Thread(target=self.run_loop)
        self.run_loop_thread.start()

        print("Initializing")

    def run_loop(self):
        print("Running star loop")
        sleep(2)
        while True:
            if self.active and self.start_new_star:
                self.start_new_star = False
                self.draw_star()
            sleep(.1)


            
    def stop(self):
        self.vel_pub.publish(Twist())

    def draw_star(self):
        self.bump = Event()
        for _ in range(self.num_turns):
            if not self.bump.is_set():
                print("running")
                self.drive_forward()
            if not self.bump.is_set():
                self.turn_left(-144)

        if not self.bump.is_set():
            self.stop()


    def process_bump(self, msg):
        self.bump_state = msg.left_front == 1 or msg.right_front == 1 or msg.left_side == 1 or msg.right_side == 1
        if self.active == False:
            return
        if self.bump_state:
            print("Bump detected! Stopping the neato.")
            self.bump.set()
            self.hand_off('DETECT_WALL')

    def process_behavior(self, msg):
        if msg.data == 'DRAW_SHAPE':
            if self.active == False:
                self.distance = self.distance * 1.5
                self.time_to_drive = self.distance / self.linear_speed
                self.start_new_star = True
            self.active = True
        else: 
            self.active = False

    def hand_off(self, next_name):
        self.vel_pub.publish(Twist())
        self.active = False
        state_msg = String()
        state_msg.data = next_name
        self.behavior_pub.publish(state_msg)
        print(f"handing off to {next_name}")


    def drive_forward(self):
        msg = Twist()
        msg.linear.x = self.linear_speed
        self.vel_pub.publish(msg)
        steps = int(self.time_to_drive/.1)
        for _ in range(steps):
            if self.bump.is_set():
                return
            sleep(.1)

    def turn_left(self, angle):
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
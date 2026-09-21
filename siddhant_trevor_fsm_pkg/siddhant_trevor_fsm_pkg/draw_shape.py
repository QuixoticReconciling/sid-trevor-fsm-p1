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
        # create a thread to handle long-running component
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        self.hit_pub = self.create_publsiher(String, 'found_object', 10)

        self.num_turns = 5
        self.distance = 2
        self.linear_speed = 0.3
        self.time_to_drive = self.distance / self.linear_speed

        self.create_subscription(Bump, 'bump', self.process_bump, 10)
        self.bump_state = False
        self.bump = Event()

        self.run_loop_thread = Thread(target=self.run_loop)
        self.run_loop_thread.start()
        self.active = True
        self.next_node = False

        print("Initializing")

    def run_loop(self):
        print("Begin")
        for _ in range(self.num_turns):
            if not self.bump.is_set():
                print("running")
                self.drive_forward()
            if not self.bump.is_set():
                self.turn_left(-144)
        self.stop()
            
    def stop(self):
        self.vel_pub.publish(Twist())        


    def process_bump(self, msg):
        self.bump_state = msg.left_front == 1 or msg.right_front == 1 or msg.left_rear == 1 or msg.right_rear == 1
        if self.bump_state:
            print("Bump detected! Stopping the neato.")
            self.bump.set()
            self.stop()


    def drive_forward(self):
        msg = Twist()
        msg.linear.x = self.linear_speed
        self.vel_pub.publish(msg)
        sleep(self.time_to_drive)

    def turn_left(self, angle):
        msg = Twist()
        angle_rad = angle * math.pi/180
        msg.angular.z = (angle_rad) / self.time_to_drive
        self.vel_pub.publish(msg)
        sleep(self.time_to_drive)

def main(args=None):
    rclpy.init(args=args)
    node = DrawShape()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
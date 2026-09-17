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
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math

class DrawShape(Node):
    """A class that implements a node to pilot a robot in a square.
    """

    def __init__(self, distance):
        super().__init__('draw_shape_node')
        # create a thread to handle long-running component
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        self.num_turns = 5
        self.distance = distance
        self.linear_speed = 0.1
        self.time_to_drive = self.distance / self.linear_speed

        self.run_loop_thread = Thread(target=self.run_loop)
        self.run_loop_thread.start()

    def run_loop(self):
        self.drive_forward(0.0)
        for _ in range(self.num_turns):
            self.drive_forward(self.distance)
            self.turn_left(-144)
        self.stop()
            

    def stop(self):
        self.vel_pub.publish(Twist())


    def drive_forward(self, distance):
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
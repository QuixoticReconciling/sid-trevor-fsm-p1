import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool, String
import math

class WallFollowNode(Node):


    def __init__(self):
        super().__init__('wall_follow_node')
        self.sub = self.create_subscription(LaserScan, 'scan', self.detect_error, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)

        self.behavior_pub = self.create_publisher(String, 'behavior', 10)
        self.create_subscription(String, 'behavior', self.process_behavior, 10)

        self.create_timer(0.1, self.run_loop)
        self.turn_state = 0
        self.get_logger().info("Initializing")
        self.is_left = True
        self.active = False

    def process_behavior(self, msg):
        """
        regulates turning on the node based on behavior topic
        """
        if msg.data == 'WALL_FOLLOW':
            if not self.active:
                self.turn_state = 0
            self.active = True
        else: 
            self.active = False

    def hand_off(self, next_name):
        """
        manages handing off to the next behavior based on detect wall's decision
        """
        self.pub.publish(Twist())          # stop the robot
        self.active = False
        state_msg = String()
        state_msg.data = next_name
        self.behavior_pub.publish(state_msg)
        self.get_logger().info(f"handing off to {next_name}")


    def run_loop(self):
        """
        handles adjusting the position of the neato after the next state is determined
        """
        if self.active == False:
            return
        out = Twist()
        if self.turn_state == 1:
            out.linear.x = 0.1
            out.angular.z = -(10*math.pi/180)
        elif self.turn_state == 2:
            out.linear.x = 0.1
            out.angular.z = 10*math.pi/180
            
        elif self.turn_state == 0:
            out.linear.x = 0.1

        self.pub.publish(out)

    
    def detect_error(self, msg) :
        """
        calculates the error and allows neato to drive straight
        """
        if self.active == False:
            return
        
        self.get_logger().info(f"turn state is {self.turn_state}")
        idx_a = 90-30
        idx_b = 90+30

        a = msg.ranges[idx_a]
        b = msg.ranges[idx_b]

        if not math.isfinite(a) or not math.isfinite(b):
            return
        if a > 1 or b > 1:
            self.hand_off('DRAW_SHAPE')
        
        self.get_logger().info(f"err: {a - b}")
        self.get_logger().info(f"distance for b: {b}")
        self.get_logger().info(f"a: {a}")


        if self.is_left:
            if a < b :
                self.turn_state = 1
            elif a > b:
                self.turn_state = 2
            else:
                self.turn_state = 0

def main(args=None):
    rclpy.init(args=args)
    node = WallFollowNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
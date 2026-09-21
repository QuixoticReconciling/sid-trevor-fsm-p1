import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math
from std_msgs.msg import String

class DetectWall(Node):

    

    def __init__(self):
        super().__init__('detect_wall_node')
        self.create_timer(0.1, self.run_loop)
        self.sub = self.create_subscription(LaserScan, 'scan', self.detect_the_wall, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)

        self.behavior_pub = self.create_publisher(String, 'behavior', 10)
        self.create_subscription(String, 'behavior', self.process_behavior, 10)
        self.state = 'detecting'
        self.is_wall = False
        self.active = True
        self.ticks = 0
        self.is_adjusted = False


        print("I'm initializing")

    def run_loop(self):
        if self.active == False:
            return
        msg = Twist()
        if self.state == 'detecting':
            pass
        elif self.state == 'adjust':
            if self.is_adjusted:
                self.hand_off('WALL_FOLLOW')
                return
            msg.angular.z = 0.0
        elif self.state == 'backup':
            msg.linear.x = -0.1
            self.ticks = self.ticks + 1
            if self.ticks >= 15:
                self.ticks = 0
                self.state = 'turn_around'
        elif self.state == 'turn_around':
            msg.angular.z = 30 * math.pi /180
            self.ticks = self.ticks + 1
        if self.ticks >= 60:
            self.hand_off('DRAW_SHAPE')
            return

        self.pub.publish(msg)
        
    def process_scan(self, msg):
        if self.active == False:
            return
        if self.state == 'classify':
            self.detect_the_wall(msg)
            if self.is_wall:
                self.state = 'adjust'
            else:
                self.state = 'backup'
        elif self.state == 'adjust':
            self.adjust_neato(msg)


    def detect_the_wall(self, msg):
        if self.active == False:
            return
        error = .1
        min_dist = msg.ranges[0]
        min_dist_idx = 0
        print("I'm running")
        for idx, distance in enumerate(msg.ranges):
            if distance < min_dist:
                min_dist = distance
                min_dist_idx = idx

        plus45 = min_dist_idx + 45
        if plus45 >= 360:
            plus45 = plus45 - 360

        minus45 = min_dist_idx - 45

        if minus45 < 0:
            minus45 = minus45 + 360
            
        if math.fabs(msg.ranges[minus45] - msg.ranges[plus45]) < error:
            print("WALL YEYAY")
            self.is_wall = True
        else:
            print("NO WALL SAD")
            self.is_wall = False

    def adjust_neato(self, msg):
        min_dist = msg.ranges[0]
        min_dist_idx = 0
        for idx, distance in enumerate(msg.ranges):
            if distance < min_dist:
                min_dist = distance
                min_dist_idx = idx

        if math.fabs(min_dist_idx - 90) < 15:
            self.is_adjusted = True          

def main(args=None):
    rclpy.init(args=args)
    node = DetectWall()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

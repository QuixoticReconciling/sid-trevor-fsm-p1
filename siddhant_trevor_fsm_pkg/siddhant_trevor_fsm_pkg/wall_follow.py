import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math

class WallFollowNode(Node):
    def __init__(self):
        super().__init__('wall_follow_node')
        self.sub = self.create_subscription(LaserScan, 'scan', self.detect_error, 10)
        #self.sub = self.create_subscription(LaserScan, 'scan', self.get_follow_dist, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_timer(0.1, self.run_loop)
        self.turn_state = 0
        print("Initializing")
        self.is_left = True
        self.active = True
        self.next_node = False
        #self.follow_distance = get_follow_dist()


    def run_loop(self):
        out = Twist()
        if self.turn_state == 1:
            out.linear.x = 0.1
            out.angular.z = -(10*math.pi/180)
            # print(f"Turning left at negative {out.angular.z} rad/s")
        elif self.turn_state == 2:
            out.linear.x = 0.1
            out.angular.z = 10*math.pi/180
            
        elif self.turn_state == 0:
            out.linear.x = 0.1
            # print(f"Moving forward at {out.linear.x} m/s")

        self.pub.publish(out)

    # def get_follow_dist(self, msg):
    #     min_dist = msg.ranges[0]

    #     for distance in msg.ranges:
    #         if distance < min_dist:
    #             min_dist = distance

    #     return min_dist
    
    def detect_error(self, msg) :
        print(f"turn state is {self.turn_state}")
        idx_a = 90-45
        idx_b = 90+45

        a = msg.ranges[idx_a]
        b = msg.ranges[idx_b]
        #max_dist = .4
        
        print(f"err: {a - b}")
        #print(f"distance for b: {b}")


        # print(f"Distance from wall: {pos}")
        # print(f"Min dist: {pos}")
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
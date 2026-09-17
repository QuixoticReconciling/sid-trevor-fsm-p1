import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class ObjDetect(Node):
    def __init__(self):
        super().__init__('obj_detect_node')
        self.create_timer(0.1, self.run_loop)
        self.sub = self.create_subscription(LaserScan, 'scan', self.process_scan, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.distance_to_obstacle = None
        self.target_distance = 0.5

    def run_loop(self):
        msg = Twist()
        print(range)
        if self.distance_to_obstacle is None:
            msg.linear.x = 0.1
        else:
            msg.linear.x = 0.0
            print(f"velocity is currently set to {msg.linear.x} and {msg.linear.y}")

        self.pub.publish(msg)

    def process_scan(self, msg):
        if msg.ranges[0] < self.target_distance:
            self.distance_to_obstacle = msg.ranges[0]
            print(f"Distance to obstacle: {self.distance_to_obstacle}")

def main(args=None):
    rclpy.init(args=args)
    node = ObjDetect()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

import rclpy
from rclpy.node import Node
from neato2_interfaces.msg import Bump
from geometry_msgs.msg import Twist

class ObjDetectNode(Node):
    def __init__(self):
        super().__init__('obj_detect_node')
        self.create_timer(0.1, self.run_loop)
        self.bump_state = False
        self.sub = self.create_subscription(Bump, 'bump', self.process_bump, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)

    def run_loop(self):
        msg = Twist()
        print(f"Current bump state: {self.bump_state}")
        if self.bump_state == True:
            msg.linear.x = 0.0
            print("Stopping due to bump sensor activation.")
        else:
            msg.linear.x = 0.3

        self.pub.publish(msg)

    def process_bump(self, msg):

        self.bump_state = msg.left_front == 1 or msg.right_front == 1 or msg.left_rear == 1 or msg.right_rear == 1
        print("Bump detected! Stopping the robot.")


def main(args=None):
    rclpy.init(args=args)
    node = StopOnBumpNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

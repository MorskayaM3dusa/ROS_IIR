import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

try:
    from turtlesim.msg import Pose
except ImportError:
    from turtlesim_msgs.msg import Pose


def compute_command(pose):
    """Возвращает Twist на основе последней позы или None.

    Если pose is None — нулевая команда.
    Иначе — linear.x = 0.5, angular.z = 0.3.
    """
    cmd = Twist()
    if pose is None:
        return cmd
    cmd.linear.x = 0.5
    cmd.angular.z = 0.3
    return cmd


class Patrol(Node):
    def __init__(self):
        super().__init__('patrol')
        self.last_pose = None
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def pose_callback(self, msg):
        self.last_pose = msg

    def timer_callback(self):
        cmd = compute_command(self.last_pose)
        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

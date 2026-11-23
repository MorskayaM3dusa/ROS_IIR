import math

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist

from turtlesim.msg import Pose


def compute_command(pose, linear_speed=0.5, turn_rate=0.3):
    """Возвращает Twist на основе последней позы или None.

    Если pose is None — нулевая команда.
    Иначе — linear.x = linear_speed, angular.z = turn_rate.
    """
    cmd = Twist()
    if pose is None:
        return cmd
    cmd.linear.x = float(linear_speed)
    cmd.angular.z = float(turn_rate)
    return cmd


class Patrol(Node):
    def __init__(self):
        super().__init__('patrol')
        self.last_pose = None
        self.linear_speed = 0.5
        self.turn_rate = 0.3
        self.publish_hz = 10.0
        self.timer = None

        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)
        self.declare_parameter('publish_hz', 10.0)

        self.linear_speed = float(self.get_parameter('linear_speed').value)
        self.turn_rate = float(self.get_parameter('turn_rate').value)
        self.publish_hz = float(self.get_parameter('publish_hz').value)

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self._create_timer()

        self.add_on_set_parameters_callback(self._parameter_callback)

        self.get_logger().info(
            f'Patrol запущен: linear_speed={self.linear_speed}, '
            f'turn_rate={self.turn_rate}, publish_hz={self.publish_hz}'
        )

    def _create_timer(self):
        """Останавливает старый таймер (если есть) и создаёт новый с текущей publish_hz."""
        if self.timer is not None:
            self.timer.cancel()
        period = 1.0 / self.publish_hz
        self.timer = self.create_timer(period, self.timer_callback)

    def _parameter_callback(self, params):
        """Валидирует входящие параметры до изменения состояния и таймера."""
        result = SetParametersResult(successful=True)

        for param in params:
            name = param.name
            value = param.value

            if name == 'linear_speed':
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    result.successful = False
                    result.reason = (
                        f'linear_speed должен быть конечным числом, получено {value!r}'
                    )
                    return result
                if value < 0 or value > 1:
                    result.successful = False
                    result.reason = (
                        f'linear_speed должен быть в диапазоне [0, 1] м/с, '
                        f'получено {value}'
                    )
                    return result
                self.linear_speed = float(value)
                self.get_logger().info(f'linear_speed установлен: {self.linear_speed} м/с')

            elif name == 'turn_rate':
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    result.successful = False
                    result.reason = (
                        f'turn_rate должен быть конечным числом, получено {value!r}'
                    )
                    return result
                if value < -1 or value > 1:
                    result.successful = False
                    result.reason = (
                        f'turn_rate должен быть в диапазоне [-1, 1] рад/с, '
                        f'получено {value}'
                    )
                    return result
                self.turn_rate = float(value)
                self.get_logger().info(f'turn_rate установлен: {self.turn_rate} рад/с')

            elif name == 'publish_hz':
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    result.successful = False
                    result.reason = (
                        f'publish_hz должен быть конечным числом, получено {value!r}'
                    )
                    return result
                if value < 1 or value > 30:
                    result.successful = False
                    result.reason = (
                        f'publish_hz должен быть в диапазоне [1, 30] Гц, '
                        f'получено {value}'
                    )
                    return result
                old_hz = self.publish_hz
                self.publish_hz = float(value)
                self._create_timer()
                self.get_logger().info(
                    f'publish_hz изменён: {old_hz} -> {self.publish_hz} Гц '
                    f'(период таймера {1.0 / self.publish_hz:.3f} с)'
                )

        return result

    def pose_callback(self, msg):
        self.last_pose = msg

    def timer_callback(self):
        cmd = compute_command(self.last_pose, self.linear_speed, self.turn_rate)
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

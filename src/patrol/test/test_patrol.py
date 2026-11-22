import unittest
from geometry_msgs.msg import Twist
from patrol.patrol import compute_command


class TestComputeCommand(unittest.TestCase):
    def test_no_pose_returns_zero_command(self):
        """При отсутствии позы команда должна быть нулевой."""
        cmd = compute_command(None)
        self.assertEqual(cmd.linear.x, 0.0)
        self.assertEqual(cmd.linear.y, 0.0)
        self.assertEqual(cmd.linear.z, 0.0)
        self.assertEqual(cmd.angular.x, 0.0)
        self.assertEqual(cmd.angular.y, 0.0)
        self.assertEqual(cmd.angular.z, 0.0)

    def test_with_pose_returns_movement_command(self):
        """При наличии позы команда содержит linear.x=0.5, angular.z=0.3."""
        cmd = compute_command(object())
        # object() не имеет полей x/y/theta, но compute_command не обращается
        # к полям pose, только проверяет на None.
        self.assertEqual(cmd.linear.x, 0.5)
        self.assertEqual(cmd.angular.z, 0.3)


if __name__ == '__main__':
    unittest.main()

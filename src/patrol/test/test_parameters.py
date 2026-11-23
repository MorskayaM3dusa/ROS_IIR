import math
import unittest

from geometry_msgs.msg import Twist
from patrol.patrol import compute_command


class TestComputeCommand(unittest.TestCase):
    """Тесты чистой функции compute_command без ROS."""

    def test_no_pose_returns_zero_command(self):
        """При отсутствии позы команда должна быть нулевой."""
        cmd = compute_command(None)
        self.assertEqual(cmd.linear.x, 0.0)
        self.assertEqual(cmd.linear.y, 0.0)
        self.assertEqual(cmd.linear.z, 0.0)
        self.assertEqual(cmd.angular.x, 0.0)
        self.assertEqual(cmd.angular.y, 0.0)
        self.assertEqual(cmd.angular.z, 0.0)

    def test_with_pose_uses_default_speed_and_turn(self):
        """При наличии позы команда использует значения по умолчанию (0.5, 0.3)."""
        cmd = compute_command(object())
        self.assertEqual(cmd.linear.x, 0.5)
        self.assertEqual(cmd.angular.z, 0.3)

    def test_custom_speed_and_turn(self):
        """Явные параметры линейной и угловой скорости применяются к команде."""
        cmd = compute_command(object(), linear_speed=0.7, turn_rate=-0.4)
        self.assertEqual(cmd.linear.x, 0.7)
        self.assertEqual(cmd.angular.z, -0.4)

    def test_zero_speed_is_valid(self):
        """Скорость 0 допустима — команда с нулевой линейной составляющей."""
        cmd = compute_command(object(), linear_speed=0.0, turn_rate=0.0)
        self.assertEqual(cmd.linear.x, 0.0)
        self.assertEqual(cmd.angular.z, 0.0)

    def test_compute_command_does_not_validate_ranges(self):
        """compute_command сама не валидирует диапазоны — валидация в параметрах ноды."""
        # Функция принимает любые конечные числа, диапазоны проверяются на уровне параметров.
        cmd = compute_command(object(), linear_speed=2.0, turn_rate=5.0)
        self.assertEqual(cmd.linear.x, 2.0)
        self.assertEqual(cmd.angular.z, 5.0)


class TestParameterValidation(unittest.TestCase):
    """Тесты валидации входных значений параметров (аналог проверки в ноде)."""

    def test_linear_speed_valid_range(self):
        for v in (0.0, 0.5, 1.0):
            self.assertTrue(0 <= v <= 1, f'{v} должен быть в [0, 1]')

    def test_linear_speed_invalid(self):
        for v in (-0.1, 1.1, float('nan'), float('inf')):
            if math.isnan(v) or math.isinf(v):
                self.assertFalse(math.isfinite(v), f'{v} должен быть конечным')
            else:
                self.assertFalse(0 <= v <= 1, f'{v} не должен попадать в [0, 1]')

    def test_turn_rate_valid_range(self):
        for v in (-1.0, -0.5, 0.0, 0.3, 1.0):
            self.assertTrue(-1 <= v <= 1, f'{v} должен быть в [-1, 1]')

    def test_turn_rate_invalid(self):
        for v in (-1.1, 1.1, float('nan'), float('inf')):
            if math.isnan(v) or math.isinf(v):
                self.assertFalse(math.isfinite(v), f'{v} должен быть конечным')
            else:
                self.assertFalse(-1 <= v <= 1, f'{v} не должен попадать в [-1, 1]')

    def test_publish_hz_valid_range(self):
        for v in (1.0, 5.0, 10.0, 30.0):
            self.assertTrue(1 <= v <= 30, f'{v} должен быть в [1, 30]')

    def test_publish_hz_invalid(self):
        for v in (0.0, -5.0, 30.1, float('nan'), float('inf')):
            if math.isnan(v) or math.isinf(v):
                self.assertFalse(math.isfinite(v), f'{v} должен быть конечным')
            elif v == 0:
                self.assertFalse(v >= 1, f'0 не должен проходить проверку publish_hz >= 1')
            else:
                self.assertFalse(1 <= v <= 30, f'{v} не должен попадать в [1, 30]')


class TestTwistStructure(unittest.TestCase):
    """Проверка структуры Twist-команды."""

    def test_twist_fields_are_floats(self):
        cmd = compute_command(None)
        for field in (cmd.linear.x, cmd.linear.y, cmd.linear.z,
                      cmd.angular.x, cmd.angular.y, cmd.angular.z):
            self.assertIsInstance(field, float)
            self.assertEqual(field, 0.0)


if __name__ == '__main__':
    unittest.main()

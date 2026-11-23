# PR04 — Параметры движения patrol

## Команда проверки типа позы
```bash
ros2 topic type /turtle1/pose
```
Ожидаемый вывод: `turtlesim/msg/Pose`

## Запуск ноды patrol
```bash
ros2 run patrol patrol
```
В отдельном терминале проверяем, что нода доступна:
```bash
ros2 node list --no-daemon --spin-time 2
# /patrol
```

## Посмотр текущих параметров
```bash
ros2 param list /patrol
#   linear_speed
#   publish_hz
#   start_type_description_service
#   turn_rate
#   use_sim_time

ros2 param get /patrol linear_speed
# Double value is: 0.5

ros2 param get /patrol turn_rate
# Double value is: 0.3

ros2 param get /patrol publish_hz
# Double value is: 10.0
```

## Допустимая смена частоты 10 → 5 Гц
```bash
ros2 param set /patrol publish_hz 5.0
# Set parameter successful
```
После команды в логе ноды должно появиться сообщение о пересоздании таймера:
```
[INFO] [1795415866.935964077] [patrol]: publish_hz изменён: 10.0 -> 5.0 Гц (период таймера 0.200 с)
```

## Попытка установить 0 (дефект — должна быть отклонена)
```bash
ros2 param set /patrol publish_hz 0.0
# Setting parameter failed: publish_hz должен быть в диапазоне [1, 30] Гц, получено 0.0
# Параметр НЕ применён, старое значение сохранено.
```

## Попытка установить отрицательное значение
```bash
ros2 param set /patrol publish_hz -5.0
# Setting parameter failed: publish_hz должен быть в диапазоне [1, 30] Гц, получено -5.0
```

## Попытка установить NaN
```bash
ros2 param set /patrol publish_hz nan
# Setting parameter failed: Wrong parameter type, expected 'Type.DOUBLE' got 'Type.STRING'

# CLI ros2 param set не передаёт nan как Double — ошибка типа возникает до вызова колбэка. Проверка NaN выполнена в юнит-тесте test_publish_hz_invalid (см. tests.txt)
```



## Проверка linear_speed и turn_rate
```bash
ros2 param set /patrol linear_speed 0.8
# Set parameter successful
# [INFO] [1795416009.353785672] [patrol]: linear_speed установлен: 0.8 м/с

ros2 param set /patrol linear_speed 1.5
# Setting parameter failed: linear_speed должен быть в диапазоне [0, 1] м/с, получено 1.5

ros2 param set /patrol turn_rate -0.7
# Set parameter successful
# [INFO] [1795416120.340796011] [patrol]: turn_rate установлен: -0.7 рад/с

ros2 param set /patrol turn_rate 2.0
# Setting parameter failed: turn_rate должен быть в диапазоне [-1, 1] рад/с, получено 2.0
```

## Вызов готового сервиса /clear и проверка действия поворота
```bash
ros2 service call /clear std_srvs/srv/Empty
# requester: making request: std_srvs.srv.Empty_Request()

# response:
# std_srvs.srv.Empty_Response()

# Очищает следы черепахи с экрана

ros2 action list -t
# /turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
```

### Отличие запроса от цели
Сервис — это синхронный вызов типа «вопрос-ответ»: клиент отправляет запрос и просто ждет, пока сервер не вернет результат (например, /clear мгновенно очищает экран). Экшен - это асинхронная длительная задача: клиент ставит цель (goal), получает промежуточный фидбек (feedback) о прогрессе и может отменить задачу в любой момент, что идеально подходит для таких процессов, как поворот черепахи на определенный угол.

## Воспроизведение дефекта (этап «сломать»)

Временно убрана проверка `publish_hz >= 1`. Команда:
```bash
ros2 param set /patrol publish_hz 0.0
```
Результат: нода падает с `ZeroDivisionError: float division by zero` в `_create_timer`, так как период таймера `1.0 / 0.0`.

Вывод из терминала:
```
Traceback (most recent call last):
  File "/mnt/c/Work/3 kurs/robotic_1/install/patrol/lib/patrol/patrol", line 33, in <module>
    sys.exit(load_entry_point('patrol', 'console_scripts', 'patrol')())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Work/3 kurs/robotic_1/build/patrol/patrol/patrol.py", line 144, in main
    rclpy.spin(node)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/__init__.py", line 247, in spin
    executor.spin_once()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 926, in spin_once
    self._spin_once_impl(timeout_sec)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 918, in _spin_once_impl
    raise handler.exception()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/task.py", line 286, in _execute_coroutine_step
    result = coro.send(None)
             ^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 592, in handler
    await call_coroutine()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 531, in _execute
    response = await await_or_execute(srv.callback, request, srv.srv_type.Response())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 115, in await_or_execute
    return callback(*args)
           ^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/parameter_service.py", line 117, in _set_parameters_callback
    result = node.set_parameters_atomically([param])
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 839, in set_parameters_atomically
    return self._set_parameters_atomically(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 859, in _set_parameters_atomically
    return self._set_parameters_atomically_common(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 909, in _set_parameters_atomically_common
    result = callback(parameter_list)
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Work/3 kurs/robotic_1/build/patrol/patrol/patrol.py", line 124, in _parameter_callback
    self._create_timer()
  File "/mnt/c/Work/3 kurs/robotic_1/build/patrol/patrol/patrol.py", line 63, in _create_timer
    period = 1.0 / self.publish_hz
             ~~~~^~~~~~~~~~~~~~~~~
ZeroDivisionError: float division by zero
[ros2run]: Process exited with failure 1
```

## Исправление (этап «исправить»)

Проверка возвращена. Выполнено:
```bash
ros2 param set /patrol publish_hz 5.0
# Set parameter successful
# [INFO] [1795416298.268751239] [patrol]: publish_hz изменён: 5.0 -> 5.0 Гц (период таймера 0.200 с)

ros2 param set /patrol publish_hz 0.0
# Setting parameter failed: publish_hz должен быть в диапазоне [1, 30] Гц, получено 0.0

ros2 param get /patrol publish_hz
# Double value is: 5.0  (старое значение сохранено, таймер не троган)
```

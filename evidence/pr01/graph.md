# Граф ROS 2 — ПР01

## Команды и вывод

### Список нод
```bash
ros2 node list --no-daemon --spin-time 2
```
Вывод:
```
/turtlesim
```

### Список топиков с типами
```bash
ros2 topic list -t
```
Вывод:
```
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

### Информация о ноде /turtlesim
```bash
ros2 node info /turtlesim
```
Вывод:
```
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```

### Топик позы
```bash
ros2 topic type /turtle1/pose
```
Вывод:
```
turtlesim/msg/Pose
```

### Пример позы
```bash
ros2 topic echo /turtle1/pose --once
```
Вывод:
```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```

### Частота публикации позы
```bash
ros2 topic hz /turtle1/pose
```
Вывод (10 секунд измерения):
```
average rate: 62.531
	min: 0.014s max: 0.018s std dev: 0.00067s window: 64
average rate: 62.518
	min: 0.014s max: 0.018s std dev: 0.00062s window: 127
average rate: 62.502
	min: 0.013s max: 0.018s std dev: 0.00067s window: 190
average rate: 62.495
	min: 0.013s max: 0.018s std dev: 0.00064s window: 253
average rate: 62.472
	min: 0.013s max: 0.019s std dev: 0.00066s window: 316
average rate: 62.505
	min: 0.013s max: 0.019s std dev: 0.00065s window: 379
average rate: 62.493
	min: 0.013s max: 0.019s std dev: 0.00064s window: 442
average rate: 62.499
	min: 0.013s max: 0.019s std dev: 0.00064s window: 505
average rate: 62.499
	min: 0.013s max: 0.019s std dev: 0.00063s window: 568
average rate: 62.498
	min: 0.013s max: 0.019s std dev: 0.00063s window: 631
```

**Измеренная частота:** ~62.5 Гц (при норме 60–62.5 Гц)

## Ноды и их роли

| Нода | Роль |
|------|------|
| `/turtlesim` | Симулятор черепахи. Публикует позу (`/turtle1/pose`) и цвет (`/turtle1/color_sensor`), подписывается на команды движения (`/turtle1/cmd_vel`). Предоставляет сервисы управления (spawn, kill, reset, teleport, set_pen). |
| `/teleop_turtle` | Управление с клавиатуры. Публикует команды движения в `/turtle1/cmd_vel`. |

## Топики

| Топик | Тип | Направление |
|-------|-----|-------------|
| `/turtle1/pose` | `turtlesim/msg/Pose` | Публикуется `/turtlesim` |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Публикуется `/teleop_turtle`, подписывается `/turtlesim` |
| `/turtle1/color_sensor` | `turtlesim/msg/Color` | Публикуется `/turtlesim` |
| `/parameter_events` | `rcl_interfaces/msg/ParameterEvent` | Публикуется всеми нодами |
| `/rosout` | `rcl_interfaces/msg/Log` | Публикуется всеми нодами |

## Сравнение «до / сбой / после»

### До (домен 45)
- Ноды: `/turtlesim`, `/teleop_turtle`
- Поза публикуется, частота ~62.5 Гц
- Управление с клавиатуры работает

### Сбой (домен 63)
- teleop запущен в домене 63, turtlesim в домене 45
- Ноды не видят друг друга
- Поза не приходит (timeout, exit=124)
- Управление не работает

### После (домен 45)
- Обе ноды в домене 45
- Поза приходит (exit=0)
- Управление работает

## Объяснение

`ROS_DOMAIN_ID` определяет область обнаружения участников DDS. При запуске ноды с другим `ROS_DOMAIN_ID` она попадает в другую область обнаружения и не может обмениваться данными с нодами из другой области. Для восстановления связи необходимо, чтобы обе ноды использовали одинаковый `ROS_DOMAIN_ID`.

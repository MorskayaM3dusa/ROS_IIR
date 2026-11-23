# Практические работы по курсу «Робототехника»

## Окружение

- ОС: Ubuntu 24.04.5 LTS (WSL2)
- ROS 2: Jazzy
- RMW: rmw_fastrtps_cpp
- Gazebo: 8.15.0

---

## ПР01. Окружение и граф ROS 2

### Описание

Запуск готовой системы ROS 2 (`turtlesim`), исследование графа через терминал, разрыв и восстановление связи между нодами с разными `ROS_DOMAIN_ID`.

### Запуск

#### 1. Подготовка окружения

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=45
```

#### 2. Запуск симулятора и управления

**Терминал A** — симулятор:
```bash
ros2 run turtlesim turtlesim_node
```

**Терминал B** — управление с клавиатуры:
```bash
ros2 run turtlesim turtle_teleop_key
```

**Терминал C** — наблюдение:
```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

#### 3. Разрыв связи (другой домен)

```bash
# Терминал B: остановить teleop (Ctrl+C), затем:
export ROS_DOMAIN_ID=63
ros2 run turtlesim turtle_teleop_key

# Терминал C:
export ROS_DOMAIN_ID=63
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

#### 4. Восстановление связи

```bash
# Терминал B: остановить teleop (Ctrl+C), затем:
export ROS_DOMAIN_ID=45
ros2 run turtlesim turtle_teleop_key

# Терминал C:
export ROS_DOMAIN_ID=45
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

### Результаты ПР01

- Граф ROS 2 описан в `evidence/pr01/graph.md`
- Информация об окружении в `evidence/pr01/environment.json`
- Отчёт в `evidence/pr01/report.json`

---

## ПР02. Терминал, пакет и запуск turtlesim

### Описание

Создание ROS-пакета `turtle_bringup`, сборка через `colcon`, запуск `turtlesim` через launch-файл, проверка доставки команды движения в `/turtle1/cmd_vel`, разбор сбоя с неправильным именем топика.

### Запуск ПР02 (turtle_bringup)

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
source install/setup.bash
export ROS_DOMAIN_ID=45

# Сборка пакета
colcon build --symlink-install --packages-select turtle_bringup

# Запуск turtlesim через launch
ros2 launch turtle_bringup sim.launch.py

# В другом терминале — проверка графа
ros2 node list --no-daemon --spin-time 2

# Публикация команды движения
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

### Результаты ПР02

- ROS-пакет `turtle_bringup` в `src/turtle_bringup/`
- Лог первоначальной сборки (пустой пакет): `evidence/pr02/build-empty.txt`
- Лог итоговой сборки (с launch): `evidence/pr02/build.txt`
- Разбор команд и сбоя: `evidence/pr02/commands.md`
- Типы сообщений: `evidence/pr02/types.md`
- Отчёт в `evidence/pr02/report.json`

---

## ПР03. Первая нода: поза и команда

### Описание

Создание первой ROS 2 ноды на Python (`rclpy`) в пакете `patrol`. Нода подписывается на `/turtle1/pose`, хранит последнюю позу и по таймеру 0.1 с публикует `geometry_msgs/msg/Twist` в относительный топик `cmd_vel`. Связь исправляется через remap `-r cmd_vel:=/turtle1/cmd_vel`.

### Запуск ПР03

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
source install/setup.bash
export ROS_DOMAIN_ID=45

# Сборка пакета
colcon build --symlink-install --packages-select patrol

# Запуск ноды (в одном терминале, вместе с turtlesim)
ros2 run patrol patrol

# В другом терминале — проверка графа
ros2 node list --no-daemon --spin-time 2

# Исправление имени топика через remap
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel

# Измерение частоты команд
ros2 topic hz /turtle1/cmd_vel

# Тесты
python3 -m pytest src/patrol/test -v
```

### Результаты ПР03

- ROS-пакет `patrol` в `src/patrol/`
- Описание демонстрации: `evidence/pr03/demo.md`
- Результаты тестов: `evidence/pr03/tests.txt`
- Отчёт в `evidence/pr03/report.json`

---

## ПР04. Параметризуем движение

### Описание

Модификация пакета `patrol` из ПР03: добавление параметров `linear_speed`, `turn_rate`, `publish_hz` с валидацией входных значений, динамическим пересозданием таймера при изменении частоты, защитой от недопустимых значений (0, отрицательные, NaN, вне диапазона).

### Запуск ПР04

```bash
source /opt/ros/jazzy/setup.bash
cd "$(git rev-parse --show-toplevel)"
source install/setup.bash
export ROS_DOMAIN_ID=45

# Сборка пакета
colcon build --symlink-install --packages-select patrol

# Запуск ноды (в одном терминале, вместе с turtlesim)
ros2 run patrol patrol

# Просмотр параметров
ros2 param list --node /patrol

# Допустимая смена частоты
ros2 param set /patrol publish_hz 5.0

# Недопустимая частота (должна быть отклонена)
ros2 param set /patrol publish_hz 0.0

# Проверка сохранения старого значения
ros2 param get /patrol publish_hz

# Тесты
python3 -m pytest src/patrol/test -v
```

### Результаты ПР04

- Модифицирован `src/patrol/patrol/patrol.py` — параметры с валидацией и пересозданием таймера
- Добавлены тесты: `src/patrol/test/test_parameters.py`
- Описание параметров и команд: `evidence/pr04/parameters.md`
- Результаты тестов: `evidence/pr04/tests.txt`
- Отчёт в `evidence/pr04/report.json`

### Полная структура репозитория

```
.
├── .course-kit/          # Комплект входных материалов (не в git)
├── .github/
│   └── workflows/
│       └── ci.yml        # CI workflow (проверка ПР01, ПР02, ПР03)
├── src/
│   ├── turtle_bringup/   # ROS-пакет для ПР02
│   └── patrol/           # ROS-пакет для ПР03
│       ├── package.xml
│       ├── setup.py
│       ├── setup.cfg
│       ├── resource/
│       │   └── patrol
│       ├── patrol/
│       │   ├── __init__.py
│       │   └── patrol.py
│       └── test/
│           ├── __init__.py
│           └── test_patrol.py
├── evidence/
│   ├── pr01/             # Результаты ПР01
│   ├── pr02/             # Результаты ПР02
│   └── pr03/             # Результаты ПР03
│       ├── demo.md
│       ├── tests.txt
│       └── report.json
│   └── pr04/             # Результаты ПР04
│       ├── parameters.md
│       ├── tests.txt
│       └── report.json
├── AI_USAGE.md           # Декларация использования ИИ
└── README.md
```


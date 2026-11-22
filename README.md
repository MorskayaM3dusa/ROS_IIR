# Практические работы ПР01 и ПР02 по курсу «Робототехника»

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

## Структура репозитория

```
.
├── .course-kit/          # Комплект входных материалов (не в git)
├── .github/
│   └── workflows/
│       └── ci.yml        # CI workflow (проверка ПР01 и ПР02)
├── src/
│   └── turtle_bringup/   # ROS-пакет для ПР02
│       ├── package.xml
│       ├── setup.py
│       ├── setup.cfg
│       ├── resource/
│       │   └── turtle_bringup
│       ├── turtle_bringup/
│       │   └── __init__.py
│       └── launch/
│           └── sim.launch.py
├── evidence/
│   ├── pr01/             # Результаты ПР01
│   │   ├── doctor.txt
│   │   ├── graph.md
│   │   ├── environment.json
│   │   ├── report.json
│   │   ├── pose-broken.txt
│   │   └── pose-fixed.txt
│   └── pr02/             # Результаты ПР02
│       ├── build-empty.txt
│       ├── build.txt
│       ├── commands.md
│       ├── types.md
│       └── report.json
├── AI_USAGE.md           # Декларация использования ИИ
└── README.md
```

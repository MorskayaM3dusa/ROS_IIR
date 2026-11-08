# ПР01. Окружение и граф ROS 2

## Описание

Практическая работа по курсу «Робототехника» — запуск готовой системы ROS 2 (turtlesim), исследование графа через терминал, разрыв и восстановление связи между нодами с разными `ROS_DOMAIN_ID`.

## Окружение

- ОС: Ubuntu 24.04.5 LTS (WSL2)
- ROS 2: Jazzy
- RMW: rmw_fastrtps_cpp
- Gazebo: 8.15.0

## Запуск

### 1. Подготовка окружения

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=45
```

### 2. Запуск симулятора и управления

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

### 3. Разрыв связи (другой домен)

```bash
# Терминал B: остановить teleop (Ctrl+C), затем:
export ROS_DOMAIN_ID=63
ros2 run turtlesim turtle_teleop_key

# Терминал C:
export ROS_DOMAIN_ID=63
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

### 4. Восстановление связи

```bash
# Терминал B: остановить teleop (Ctrl+C), затем:
export ROS_DOMAIN_ID=45
ros2 run turtlesim turtle_teleop_key

# Терминал C:
export ROS_DOMAIN_ID=45
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

## Структура репозитория

```
.
├── .course-kit/          # Комплект входных материалов (не в git)
├── .github/
│   └── workflows/
│       └── ci.yml        # CI workflow
├── evidence/
│   └── pr01/             # Результаты ПР01
│       ├── doctor.txt
│       ├── graph.md
│       ├── environment.json
│       ├── report.json
│       ├── pose-broken.txt
│       └── pose-fixed.txt
├── AI_USAGE.md           # Декларация использования ИИ
└── README.md
```

## Результаты

- Граф ROS 2 описан в `evidence/pr01/graph.md`
- Информация об окружении в `evidence/pr01/environment.json`
- Отчёт в `evidence/pr01/report.json`

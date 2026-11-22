# Команды Linux — ПР02

## Три команды из этапа 1

### 1. `pwd`

**Назначение:** вывести полный путь к текущей рабочей директории, чтобы убедиться, что терминал открыт в корне репозитория (workspace).

**Команда:**
```bash
pwd
```

**Результат:**
```
/mnt/c/Work/3 kurs/robotic_1
```

---

### 2. `mkdir -p src evidence/pr02`

**Назначение:** создать директории для исходников пакета (`src`) и для файлов отчёта второго задания (`evidence/pr02`). Флаг `-p` позволяет создавать вложенные директории и не выдавать ошибку, если они уже существуют.

**Команда:**
```bash
mkdir -p src evidence/pr02
```

**Результат:** директории созданы, ошибок нет.

---

### 3. `ros2 pkg prefix turtlesim`

**Назначение:** вывести путь к установленному пакету `turtlesim` в системе. Это путь к уже установленному пакету, а не к вашему workspace.

**Команда:**
```bash
ros2 pkg prefix turtlesim
```

**Результат:**
```
/opt/ros/jazzy
```

---

## Отличие `>` от `|`

| Оператор | Что делает | Пример |
|----------|------------|--------|
| `>` | Перенаправляет **stdout** команды в файл, заменяя его содержимое. Вывод не показывается в терминале. | `colcon build ... > build.txt` |
| `\|` | Передает **stdout** одной команды на **stdin** следующей (конвейер). | `colcon build ... \| tee build.txt` |

В практической работе использовалась комбинация `2>&1 \| tee file.txt`: поток ошибок объединяется с обычным выводом, а затем одновременно показывается в терминале (`tee`) и сохраняется в файл.

---

## Отличие `source` от запуска новой программы

- **`source /opt/ros/jazzy/setup.bash`** — выполняет скрипт в **текущем** процессе оболочки. Переменные окружения (`ROS_DISTRO`, `ROS_PACKAGE_PATH`, `PATH` и т.д.) остаются доступными после завершения скрипта.
- **Запуск новой программы** (например, простое выполнение скрипта или запуск нового bash) создаёт дочерний процесс. Изменения окружения в дочернем процессе не возвращаются в родительский терминал.

Поэтому перед работой с ROS всегда делают `source` в текущем терминале.

---

## Запуск, проверка графа и остановка launch

**Терминал A — запуск через launch:**
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=45
ros2 launch turtle_bringup sim.launch.py
```

**Вывод:**
```
[INFO] [launch]: All log files can be found below /home/roma/.ros/log/2026-11-22-...
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [turtlesim_node-1]: process started with pid [1671]
[turtlesim_node-1] [INFO] [...] [turtlesim]: Starting turtlesim with node name /turtlesim
[turtlesim_node-1] [INFO] [...] [turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]
```

**Терминал C — проверка графа:**
```bash
ros2 node list --no-daemon --spin-time 2
```

**Вывод:**
```
/turtlesim
```

**Остановка launch:** `Ctrl+C` в терминале A.

**Вывод:**
```
^C[WARNING] [launch]: user interrupted with ctrl-c (SIGINT)
[turtlesim_node-1] [INFO] [...] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[INFO] [turtlesim_node-1]: process has finished cleanly [pid 1671]
```

---

## Сравнение «до / сбой / после» (этап 5)

### До — правильное имя `/turtle1/cmd_vel`

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

**Вывод:**
```
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```

Черепаха движется.

---

### Сбой — ошибочное имя `/cmd_vel`

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

**Вывод (фрагмент):**
```
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
publishing #2: ...
```

Черепаха **не движется**.

Проверка в другом терминале:
```bash
ros2 topic info /cmd_vel --verbose
```

**Вывод:**
```
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_1795
Node namespace: /
Topic type: geometry_msgs/msg/Twist
...
Subscription count: 0
```

```bash
ros2 topic info /turtle1/cmd_vel --verbose
```

**Вывод:**
```
Type: geometry_msgs/msg/Twist

Publisher count: 0

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
...
```

Издатель есть, но подписчика в топике `/cmd_vel` нет — черепаха слушает `/turtle1/cmd_vel`.

---

### После — исправлено на `/turtle1/cmd_vel`

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

**Вывод:**
```
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(...)
publishing #2: ...
...
```

Проверка:
```bash
ros2 topic info /turtle1/cmd_vel --verbose
```

**Вывод:**
```
Publisher count: 1
Subscription count: 1

Node name: _ros2cli_1817
Node name: turtlesim
...
```

Черепаха снова движется.

---

## Почему правильного типа недостаточно

Тип сообщения `geometry_msgs/msg/Twist` совпадает в обоих случаях, но ROS 2 определяет связь издатель-подписчик по **полному имени топика**. `/cmd_vel` и `/turtle1/cmd_vel` — это **разные** топики, поэтому издатель и подписчик не находят друг друга, даже если типы сообщений идентичны.

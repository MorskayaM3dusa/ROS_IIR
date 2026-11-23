# Демонстрация и разбор — ПР03

## Роли init, spin, callback и Ctrl+C

- **`rclpy.init()`** — инициализирует клиентскую библиотеку ROS 2. Вызывается один раз в начале `main()`, прежде чем создавать ноду.
- **`Node.__init__()`** — здесь создаются подписчики, издатели и таймеры. В нашем ноде:
  - подписка на `/turtle1/pose` (сохраняет последнюю позу в `self.last_pose`);
  - издатель в `cmd_vel` (относительный топик);
  - таймер с периодом 0.1 с, который вызывает `timer_callback`.
- **`rclpy.spin(node)`** — входит в цикл обработки событий ROS 2. Пока крутится spin, вызываются callback-функции подписки и таймера. Без spin нода «висит» и ничего не делает.
- **`Ctrl+C`** — генерирует `KeyboardInterrupt`. В нашем коде он перехватывается, нода корректно уничтожается через `destroy_node()`, и `rclpy.shutdown()` завершает работу библиотеки.

## Запуск и проверка графа

1. Собрать пакет:
   ```bash
   colcon build --symlink-install --packages-select patrol
   source install/setup.bash
   ```
2. Запустить ноду (в отдельном терминале, вместе с turtlesim):
   ```bash
   ros2 run patrol patrol
   ```
3. Проверить в другом терминале:
   ```bash
   ros2 node list --no-daemon --spin-time 2
   # Ожидается: /patrol, /turtlesim
   ros2 topic info cmd_vel --verbose
   # Ожидается: Publisher count: 1, Subscription count: 0 (сбой имени)
   ros2 topic info /turtle1/cmd_vel --verbose
   # Ожидается: Subscription count: 1 (подписчик /turtlesim)
   ```

## Разрыв имени и исправление

Нода публикует в относительный топик `cmd_vel`. Черепаха (`/turtlesim`) подписана на `/turtle1/cmd_vel`. Поэтому при запуске без remap команда уходит в никуда, черепаха не движется.

Исправление через remap:
```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

После этого издатель `/patrol` и подписчик `/turtlesim` соединяются по `/turtle1/cmd_vel`, черепаха начинает двигаться.

## Измерение частоты команды

Запустить ноду с remap и измерить частоту публикации в `/turtle1/cmd_vel`:
```bash
ros2 topic hz /turtle1/cmd_vel
```
```
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00015s window: 11
average rate: 9.999
        min: 0.100s max: 0.100s std dev: 0.00014s window: 22
average rate: 10.001
        min: 0.100s max: 0.100s std dev: 0.00014s window: 33
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00016s window: 43
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00015s window: 54
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00015s window: 64
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00015s window: 75
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00015s window: 86
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00014s window: 96
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00014s window: 107
average rate: 10.000
        min: 0.100s max: 0.100s std dev: 0.00014s window: 118
average rate: 10.000
        min: 0.100s max: 0.101s std dev: 0.00015s window: 129
average rate: 10.000
        min: 0.100s max: 0.101s std dev: 0.00015s window: 140
average rate: 10.000
        min: 0.100s max: 0.101s std dev: 0.00014s window: 150
average rate: 8.108
        min: 0.100s max: 3.625s std dev: 0.28588s window: 151
```

## Остановка и поведение turtlesim

После остановки ноды `patrol` через `Ctrl+C` публикация команд прекращается. Черепаха продолжает движение по инерции последней nonzero-команды некоторое время, затем останавливается (в turtlesim команда без повторов приводит к остановке). Не следует считать исчезновение процесса мгновенной командой торможения.

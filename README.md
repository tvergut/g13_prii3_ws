# g13_prii3_ws

PRII3 - Grupo 13 - Sprint 1. La tortuga de turtlesim dibuja el 13.

Necesita Ubuntu 22.04 y ROS 2 Humble.

## Compilar

```bash
source /opt/ros/humble/setup.bash
git clone https://github.com/tvergut/g13_prii3_ws.git
cd g13_prii3_ws
rosdep install --from-paths src --ignore-src -y
colcon build
source install/setup.bash
```

## Ejecutar

```bash
ros2 launch g13_prii3_turtlesim draw_number_launch.py
```

## Servicios

```bash
ros2 service call /draw/stop std_srvs/srv/Trigger
ros2 service call /draw/resume std_srvs/srv/Trigger
ros2 service call /draw/restart std_srvs/srv/Trigger
```

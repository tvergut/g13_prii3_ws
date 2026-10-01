# g13_prii3_ws — PRII3 Grupo 13 (Sprint 1)

Workspace ROS 2 Humble con el paquete `g13_prii3_turtlesim`, que contiene un nodo en Python
(`draw_number`) que mueve la tortuga de `turtlesim` publicando velocidades en
`/turtle1/cmd_vel` para dibujar el número del grupo: **13**.

## Requisitos

- Ubuntu 22.04
- ROS 2 Humble (`ros-humble-desktop`), con `colcon` y `rosdep`

```bash
sudo apt install ros-humble-desktop python3-colcon-common-extensions python3-rosdep
```

## Instalación y compilación

```bash
source /opt/ros/humble/setup.bash
git clone <URL_DEL_REPOSITORIO> g13_prii3_ws
cd g13_prii3_ws
rosdep install --from-paths src --ignore-src -y
colcon build
source install/setup.bash
```

## Ejecución

Un único fichero launch arranca el simulador `turtlesim` y el nodo de dibujo:

```bash
ros2 launch g13_prii3_turtlesim draw_number_launch.py
```

La tortuga se desplaza (con el lápiz levantado entre trazos) y dibuja el "13".

## Servicios para controlar el dibujo

El nodo ofrece tres servicios de tipo `std_srvs/srv/Trigger`. En otra terminal
(tras hacer `source install/setup.bash`):

```bash
# Detener el dibujo
ros2 service call /draw/stop std_srvs/srv/Trigger

# Reanudar desde donde se quedó
ros2 service call /draw/resume std_srvs/srv/Trigger

# Reiniciar: borra la pantalla y vuelve a dibujar desde el principio
ros2 service call /draw/restart std_srvs/srv/Trigger
```

## Estructura

```
g13_prii3_ws/
└── src/
    └── g13_prii3_turtlesim/
        ├── g13_prii3_turtlesim/
        │   └── draw_number.py        # nodo de control
        ├── launch/
        │   └── draw_number_launch.py # launch: turtlesim + nodo
        ├── package.xml
        └── setup.py
```

## Funcionamiento

- El nodo se suscribe a `/turtle1/pose` y publica `geometry_msgs/Twist` en `/turtle1/cmd_vel`.
- El número se define como una lista de waypoints `(x, y, lápiz)`. Para cada uno, el nodo
  sube o baja el lápiz con el servicio `/turtle1/set_pen`, gira hasta orientarse hacia el
  punto y avanza con un controlador proporcional.
- `restart` usa el servicio `/clear` de turtlesim para borrar el dibujo anterior.

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen
from std_srvs.srv import Empty, Trigger


# Parámetros del controlador
DIST_TOL = 0.05       # distancia para dar un waypoint por alcanzado
ANG_TOL = 0.02        # error angular (rad) a partir del cual se avanza
MAX_LIN = 2.0         # velocidad lineal máxima
MAX_ANG = 3.0         # velocidad angular máxima
K_LIN = 1.5           # ganancia proporcional lineal
K_ANG = 5.0           # ganancia proporcional angular


class DrawNumberNode(Node):
    def __init__(self):
        super().__init__('draw_number')

        # Publicador de velocidades y suscriptor de la pose de la tortuga
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        # Clientes de servicios de turtlesim (lápiz y limpiar pantalla)
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.clear_client = self.create_client(Empty, '/clear')

        self.get_logger().info('Esperando a los servicios de turtlesim...')
        self.pen_client.wait_for_service()
        self.clear_client.wait_for_service()
        self.get_logger().info('Servicios disponibles.')

        self.waypoints = self._build_number_13()
        self.pose = None
        self.index = 0
        self.pen_index = -1      # waypoint cuyo lápiz ya está configurado
        self.pen_future = None
        self.running = True

        # Servicios propios para controlar el dibujo
        self.create_service(Trigger, 'draw/stop', self.stop_callback)
        self.create_service(Trigger, 'draw/resume', self.resume_callback)
        self.create_service(Trigger, 'draw/restart', self.restart_callback)

        self.timer = self.create_timer(0.02, self.control_loop)

    def _build_number_13(self):
        # Lista de waypoints (x, y, lápiz_bajado) que forman el número 13
        wp = []

        # Dígito "1": línea vertical
        x1 = 3.0
        wp.append((x1, 9.0, False))
        wp.append((x1, 2.0, True))

        # Dígito "3": estilo siete segmentos
        x0, x1b = 6.0, 8.0
        y_top, y_mid, y_bot = 9.0, 5.5, 2.0

        wp.append((x0, y_top, False))
        wp.append((x1b, y_top, True))
        wp.append((x1b, y_mid, True))
        wp.append((x0, y_mid, True))
        wp.append((x1b, y_mid, False))
        wp.append((x1b, y_bot, True))
        wp.append((x0, y_bot, True))

        return wp

    def pose_callback(self, msg):
        self.pose = msg

    def set_pen(self, down: bool):
        req = SetPen.Request()
        req.r = 255
        req.g = 255
        req.b = 255
        req.width = 3
        req.off = 0 if down else 1
        return self.pen_client.call_async(req)

    def stop_turtle(self):
        self.cmd_pub.publish(Twist())

    def control_loop(self):
        if not self.running or self.pose is None:
            return
        if self.index >= len(self.waypoints):
            self.stop_turtle()
            self.get_logger().info('Dibujo completado.')
            self.running = False
            return

        x, y, pen_down = self.waypoints[self.index]

        # Antes de cada tramo se sube o baja el lápiz y se espera a que se aplique
        if self.pen_index != self.index:
            if self.pen_future is None:
                self.pen_future = self.set_pen(pen_down)
            if not self.pen_future.done():
                return
            self.pen_future = None
            self.pen_index = self.index

        dx = x - self.pose.x
        dy = y - self.pose.y
        dist = math.hypot(dx, dy)

        if dist < DIST_TOL:
            self.stop_turtle()
            self.index += 1
            return

        # Error angular normalizado a [-pi, pi]
        target = math.atan2(dy, dx)
        err = math.atan2(math.sin(target - self.pose.theta),
                         math.cos(target - self.pose.theta))

        cmd = Twist()
        cmd.angular.z = max(-MAX_ANG, min(MAX_ANG, K_ANG * err))
        # Primero se orienta y después avanza, para que los trazos salgan rectos
        if abs(err) < ANG_TOL:
            cmd.linear.x = min(MAX_LIN, K_LIN * dist)
        self.cmd_pub.publish(cmd)

    def stop_callback(self, request, response):
        self.running = False
        self.stop_turtle()
        response.success = True
        response.message = 'Dibujo detenido.'
        return response

    def resume_callback(self, request, response):
        if self.index >= len(self.waypoints):
            response.success = False
            response.message = 'No hay nada pendiente, usa restart.'
        else:
            self.running = True
            response.success = True
            response.message = 'Dibujo reanudado.'
        return response

    def restart_callback(self, request, response):
        # Borra lo dibujado y vuelve a empezar desde el primer waypoint
        self.stop_turtle()
        self.clear_client.call_async(Empty.Request())
        self.index = 0
        self.pen_index = -1
        self.pen_future = None
        self.running = True
        response.success = True
        response.message = 'Dibujo reiniciado desde el principio.'
        return response


def main(args=None):
    rclpy.init(args=args)
    node = DrawNumberNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

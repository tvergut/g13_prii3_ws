import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen, TeleportAbsolute
from std_srvs.srv import Empty, Trigger

GIRO = math.pi / 2

# (avance, giro, lapiz bajado)
STEPS = [
    (0.0, GIRO, False),
    (3.5, 0.0, False),
    (0.0, GIRO, False),
    (2.5, 0.0, False),
    (0.0, GIRO, True),
    (7.0, 0.0, True),
    (0.0, GIRO, False),
    (3.0, 0.0, False),
    (0.0, GIRO, False),
    (7.0, 0.0, False),
    (0.0, -GIRO, True),
    (2.0, 0.0, True),
    (0.0, -GIRO, True),
    (3.5, 0.0, True),
    (0.0, -GIRO, True),
    (2.0, 0.0, True),
    (0.0, math.pi, False),
    (2.0, 0.0, False),
    (0.0, -GIRO, True),
    (3.5, 0.0, True),
    (0.0, -GIRO, True),
    (2.0, 0.0, True),
]


class DrawNumberNode(Node):
    def __init__(self):
        super().__init__('draw_number')

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.teleport_client = self.create_client(
            TeleportAbsolute, '/turtle1/teleport_absolute')
        self.clear_client = self.create_client(Empty, '/clear')
        self.pen_client.wait_for_service()
        self.teleport_client.wait_for_service()
        self.clear_client.wait_for_service()

        self.index = 0
        self.running = True

        self.create_service(Trigger, 'draw/stop', self.stop_callback)
        self.create_service(Trigger, 'draw/resume', self.resume_callback)
        self.create_service(Trigger, 'draw/restart', self.restart_callback)

        self.timer = self.create_timer(1.2, self.loop)

    def set_pen(self, down):
        req = SetPen.Request()
        req.r = 255
        req.g = 255
        req.b = 255
        req.width = 3
        req.off = 0 if down else 1
        self.pen_client.call_async(req)

    def loop(self):
        if not self.running:
            return
        if self.index >= len(STEPS):
            self.get_logger().info('Dibujo completado')
            self.running = False
            return

        avance, giro, lapiz = STEPS[self.index]
        self.set_pen(lapiz)
        cmd = Twist()
        cmd.linear.x = avance
        cmd.angular.z = giro
        self.cmd_pub.publish(cmd)
        self.index += 1

    def stop_callback(self, request, response):
        self.running = False
        response.success = True
        response.message = 'Dibujo detenido'
        return response

    def resume_callback(self, request, response):
        if self.index >= len(STEPS):
            response.success = False
            response.message = 'Ya ha terminado, usa restart'
        else:
            self.running = True
            response.success = True
            response.message = 'Dibujo reanudado'
        return response

    def restart_callback(self, request, response):
        self.cmd_pub.publish(Twist())
        self.set_pen(False)
        req = TeleportAbsolute.Request()
        req.x = 5.544445
        req.y = 5.544445
        req.theta = 0.0
        self.teleport_client.call_async(req)
        self.clear_client.call_async(Empty.Request())
        self.index = 0
        self.running = True
        response.success = True
        response.message = 'Dibujo reiniciado'
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

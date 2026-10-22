import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty, Trigger

GIRO = math.pi / 2
ESCALA = 0.1
VEL_LINEAL = 0.1
VEL_ANGULAR = 0.5
PERIODO = 0.1

# (metros hacia delante, giro en radianes)
STEPS = [
    (0.0, GIRO),
    (3.5, 0.0),
    (0.0, GIRO),
    (2.5, 0.0),
    (0.0, GIRO),
    (7.0, 0.0),
    (0.0, GIRO),
    (3.0, 0.0),
    (0.0, GIRO),
    (7.0, 0.0),
    (0.0, -GIRO),
    (2.0, 0.0),
    (0.0, -GIRO),
    (3.5, 0.0),
    (0.0, -GIRO),
    (2.0, 0.0),
    (0.0, math.pi),
    (2.0, 0.0),
    (0.0, -GIRO),
    (3.5, 0.0),
    (0.0, -GIRO),
    (2.0, 0.0),
]


def movimiento(avance, giro):
    cmd = Twist()
    if avance != 0.0:
        cmd.linear.x = VEL_LINEAL
        ticks = round(avance * ESCALA / VEL_LINEAL / PERIODO)
    else:
        cmd.angular.z = math.copysign(VEL_ANGULAR, giro)
        ticks = round(abs(giro) / VEL_ANGULAR / PERIODO)
    return cmd, ticks


class DrawNumberNode(Node):
    def __init__(self):
        super().__init__('draw_number')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.reset_client = self.create_client(Empty, '/reset_world')

        self.index = 0
        self.ticks = 0
        self.running = True

        self.create_service(Trigger, 'draw/stop', self.stop_callback)
        self.create_service(Trigger, 'draw/resume', self.resume_callback)
        self.create_service(Trigger, 'draw/restart', self.restart_callback)

        self.timer = self.create_timer(PERIODO, self.loop)

    def loop(self):
        if not self.running:
            return
        if self.ticks == 0:
            if self.index >= len(STEPS):
                self.cmd_pub.publish(Twist())
                self.get_logger().info('Dibujo completado')
                self.running = False
                return
            avance, giro = STEPS[self.index]
            self.cmd, self.ticks = movimiento(avance, giro)
            self.index += 1
        self.cmd_pub.publish(self.cmd)
        self.ticks -= 1

    def stop_callback(self, request, response):
        self.running = False
        self.cmd_pub.publish(Twist())
        response.success = True
        response.message = 'Dibujo detenido'
        return response

    def resume_callback(self, request, response):
        if self.index >= len(STEPS) and self.ticks == 0:
            response.success = False
            response.message = 'Ya ha terminado, usa restart'
        else:
            self.running = True
            response.success = True
            response.message = 'Dibujo reanudado'
        return response

    def restart_callback(self, request, response):
        self.cmd_pub.publish(Twist())
        if self.reset_client.service_is_ready():
            self.reset_client.call_async(Empty.Request())
        self.index = 0
        self.ticks = 0
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
        node.cmd_pub.publish(Twist())
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

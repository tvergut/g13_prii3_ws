import math
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

GIRO = math.pi / 2
ESCALA = 0.1
VEL_LINEAL = 0.1
VEL_ANGULAR = 0.5
PERIODO = 0.1
DIST_PARADA = 0.4
DIST_LIBRE = 0.6
ANGULO = math.radians(10)
GIRO_LIDAR = math.pi

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


class CollisionAvoidanceNode(Node):
    def __init__(self):
        super().__init__('collision_avoidance')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        self.frente = float('inf')
        self.index = 0
        self.ticks = 0
        self.cmd = Twist()
        self.parado = False

        self.timer = self.create_timer(PERIODO, self.loop)

    def scan_callback(self, msg):
        validos = []
        for i, r in enumerate(msg.ranges):
            ang = msg.angle_min + i * msg.angle_increment - GIRO_LIDAR
            ang = math.atan2(math.sin(ang), math.cos(ang))
            if abs(ang) < ANGULO and msg.range_min < r < msg.range_max:
                validos.append(r)
        self.frente = min(validos) if validos else float('inf')

    def loop(self):
        cmd = Twist()

        if self.parado:
            if self.frente > DIST_LIBRE:
                self.parado = False
                self.get_logger().info('Camino libre, el robot continua')
        elif self.frente < DIST_PARADA:
            self.parado = True
            self.get_logger().info('Obstaculo detectado, robot detenido')
        elif self.ticks > 0 or self.index < len(STEPS):
            if self.ticks == 0:
                avance, giro = STEPS[self.index]
                self.cmd, self.ticks = movimiento(avance, giro)
                self.index += 1
            cmd = self.cmd
            self.ticks -= 1
        else:
            self.get_logger().info('Dibujo completado')
            self.timer.cancel()

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = CollisionAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    try:
        for _ in range(5):
            node.cmd_pub.publish(Twist())
            time.sleep(0.05)
    except Exception:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()

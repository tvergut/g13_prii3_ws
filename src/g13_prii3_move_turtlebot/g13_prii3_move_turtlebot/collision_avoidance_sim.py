import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from gazebo_msgs.srv import DeleteEntity, SpawnEntity

GIRO = math.pi / 2
ESCALA = 0.1
VEL_LINEAL = 0.1
VEL_ANGULAR = 0.5
PERIODO = 0.1
DIST_PARADA = 0.6
DIST_LIBRE = 1.0
ANGULO = math.radians(15)
PASO_CUBO = 6
DIST_CUBO = 1.0
TICKS_ESPERA = 50

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

CUBO = """<sdf version="1.6">
  <model name="cubo">
    <static>false</static>
    <link name="link">
      <collision name="collision">
        <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
      </collision>
      <visual name="visual">
        <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
      </visual>
    </link>
  </model>
</sdf>"""


def movimiento(avance, giro):
    cmd = Twist()
    if avance != 0.0:
        cmd.linear.x = VEL_LINEAL
        ticks = round(avance * ESCALA / VEL_LINEAL / PERIODO)
    else:
        cmd.angular.z = math.copysign(VEL_ANGULAR, giro)
        ticks = round(abs(giro) / VEL_ANGULAR / PERIODO)
    return cmd, ticks


class CollisionAvoidanceSimNode(Node):
    def __init__(self):
        super().__init__('collision_avoidance_sim')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_client = self.create_client(DeleteEntity, '/delete_entity')
        self.spawn_client.wait_for_service()
        self.delete_client.wait_for_service()

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.frente = float('inf')
        self.index = 0
        self.ticks = 0
        self.cmd = Twist()
        self.parado = False
        self.espera = 0

        self.timer = self.create_timer(PERIODO, self.loop)

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self.x = pos.x
        self.y = pos.y
        self.yaw = math.atan2(2 * q.w * q.z, 1 - 2 * q.z * q.z)

    def scan_callback(self, msg):
        validos = []
        for i, r in enumerate(msg.ranges):
            ang = msg.angle_min + i * msg.angle_increment
            ang = math.atan2(math.sin(ang), math.cos(ang))
            if abs(ang) < ANGULO and msg.range_min < r < msg.range_max:
                validos.append(r)
        self.frente = min(validos) if validos else float('inf')

    def poner_cubo(self):
        req = SpawnEntity.Request()
        req.name = 'cubo'
        req.xml = CUBO
        req.initial_pose.position.x = self.x + DIST_CUBO * math.cos(self.yaw)
        req.initial_pose.position.y = self.y + DIST_CUBO * math.sin(self.yaw)
        req.initial_pose.position.z = 0.25
        req.reference_frame = 'world'
        self.spawn_client.call_async(req)
        self.get_logger().info('Cubo colocado')

    def borrar_cubo(self):
        req = DeleteEntity.Request()
        req.name = 'cubo'
        self.delete_client.call_async(req)
        self.get_logger().info('Cubo borrado')

    def loop(self):
        cmd = Twist()

        if self.parado:
            self.espera += 1
            if self.espera == TICKS_ESPERA:
                self.borrar_cubo()
            if self.frente > DIST_LIBRE:
                self.parado = False
                self.get_logger().info('Camino libre, el robot continua')
        elif self.frente < DIST_PARADA:
            self.parado = True
            self.espera = 0
            self.get_logger().info('Obstaculo detectado, robot detenido')
        elif self.ticks > 0 or self.index < len(STEPS):
            if self.ticks == 0:
                avance, giro = STEPS[self.index]
                self.cmd, self.ticks = movimiento(avance, giro)
                self.index += 1
                if self.index == PASO_CUBO:
                    self.poner_cubo()
            cmd = self.cmd
            self.ticks -= 1
        else:
            self.get_logger().info('Dibujo completado')
            self.timer.cancel()

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = CollisionAvoidanceSimNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.cmd_pub.publish(Twist())
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from gazebo_msgs.srv import DeleteEntity, SpawnEntity

VELOCIDAD = 0.15
DIST_PARADA = 0.6
DIST_LIBRE = 1.0
META_X = 2.5
TICKS_SPAWN = 50
TICKS_ESPERA = 50

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


class ObstacleStopNode(Node):
    def __init__(self):
        super().__init__('obstacle_stop')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_client = self.create_client(DeleteEntity, '/delete_entity')

        self.x = None
        self.frente = float('inf')
        self.estado = 'avanza'
        self.ticks = 0
        self.cubo_puesto = False
        self.cubo_borrado = False

        self.timer = self.create_timer(0.1, self.loop)

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x

    def scan_callback(self, msg):
        n = len(msg.ranges)
        sector = msg.ranges[:15] + msg.ranges[n - 15:]
        validos = [r for r in sector if msg.range_min < r < msg.range_max]
        self.frente = min(validos) if validos else float('inf')

    def poner_cubo(self):
        req = SpawnEntity.Request()
        req.name = 'cubo'
        req.xml = CUBO
        req.initial_pose.position.x = self.x + 1.3
        req.initial_pose.position.z = 0.25
        req.reference_frame = 'world'
        self.spawn_client.call_async(req)
        self.cubo_puesto = True
        self.get_logger().info('Cubo colocado')

    def borrar_cubo(self):
        req = DeleteEntity.Request()
        req.name = 'cubo'
        self.delete_client.call_async(req)
        self.cubo_borrado = True
        self.get_logger().info('Cubo borrado')

    def loop(self):
        if self.x is None or self.estado == 'fin':
            return

        cmd = Twist()
        self.ticks += 1

        if self.x >= META_X:
            self.estado = 'fin'
            self.get_logger().info('Trayectoria completada')
        elif self.estado == 'avanza':
            if self.frente < DIST_PARADA:
                self.estado = 'parado'
                self.ticks = 0
                self.get_logger().info('Obstaculo detectado, robot detenido')
            else:
                cmd.linear.x = VELOCIDAD
                if not self.cubo_puesto and self.ticks >= TICKS_SPAWN:
                    self.poner_cubo()
        elif self.estado == 'parado':
            if self.cubo_puesto and not self.cubo_borrado \
                    and self.ticks >= TICKS_ESPERA:
                self.borrar_cubo()
            if self.frente > DIST_LIBRE and \
                    (self.cubo_borrado or not self.cubo_puesto):
                self.estado = 'avanza'
                self.get_logger().info('Camino libre, el robot continua')

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleStopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.cmd_pub.publish(Twist())
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

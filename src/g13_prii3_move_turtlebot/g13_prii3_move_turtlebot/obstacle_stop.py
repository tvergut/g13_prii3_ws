import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from gazebo_msgs.srv import DeleteEntity, SpawnEntity

VELOCIDAD = 0.15
DIST_PARADA = 0.6
DIST_LIBRE = 1.0
CUBO_X = 2.0
TICKS_SPAWN = 20
TICKS_ESPERA = 50
TICKS_FIN = 100

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

        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_client = self.create_client(DeleteEntity, '/delete_entity')
        self.spawn_client.wait_for_service()
        self.delete_client.wait_for_service()

        self.frente = float('inf')
        self.estado = 'avanza'
        self.t = 0
        self.t_estado = 0

        self.timer = self.create_timer(0.1, self.loop)

    def scan_callback(self, msg):
        n = len(msg.ranges)
        sector = msg.ranges[:15] + msg.ranges[n - 15:]
        validos = [r for r in sector if msg.range_min < r < msg.range_max]
        self.frente = min(validos) if validos else float('inf')

    def poner_cubo(self):
        req = SpawnEntity.Request()
        req.name = 'cubo'
        req.xml = CUBO
        req.initial_pose.position.x = CUBO_X
        req.initial_pose.position.z = 0.25
        req.reference_frame = 'world'
        self.spawn_client.call_async(req)
        self.get_logger().info('Cubo colocado')

    def borrar_cubo(self):
        req = DeleteEntity.Request()
        req.name = 'cubo'
        self.delete_client.call_async(req)
        self.get_logger().info('Cubo borrado')

    def cambiar(self, estado, mensaje):
        self.estado = estado
        self.t_estado = self.t
        self.get_logger().info(mensaje)

    def loop(self):
        self.t += 1
        espera = self.t - self.t_estado
        cmd = Twist()

        if self.t == TICKS_SPAWN:
            self.poner_cubo()

        if self.estado == 'avanza':
            if self.frente < DIST_PARADA:
                self.cambiar('parado', 'Obstaculo detectado, robot detenido')
            else:
                cmd.linear.x = VELOCIDAD
        elif self.estado == 'parado':
            if espera == TICKS_ESPERA:
                self.borrar_cubo()
            if espera > TICKS_ESPERA and self.frente > DIST_LIBRE:
                self.cambiar('continua', 'Camino libre, el robot continua')
        elif self.estado == 'continua':
            cmd.linear.x = VELOCIDAD
            if espera == TICKS_FIN:
                self.cambiar('fin', 'Trayectoria completada')

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

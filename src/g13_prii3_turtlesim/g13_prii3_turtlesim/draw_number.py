import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen
from std_srvs.srv import Empty, Trigger


class DrawNumberNode(Node):
    def __init__(self):
        super().__init__('draw_number')

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.clear_client = self.create_client(Empty, '/clear')
        self.pen_client.wait_for_service()
        self.clear_client.wait_for_service()

        self.waypoints = self.build_13()
        self.pose = None
        self.index = 0
        self.pen_index = -1
        self.pen_future = None
        self.running = True

        self.create_service(Trigger, 'draw/stop', self.stop_callback)
        self.create_service(Trigger, 'draw/resume', self.resume_callback)
        self.create_service(Trigger, 'draw/restart', self.restart_callback)

        self.timer = self.create_timer(0.02, self.loop)

    def build_13(self):
        # (x, y, lapiz bajado)
        return [
            (3.0, 9.0, False),
            (3.0, 2.0, True),
            (6.0, 9.0, False),
            (8.0, 9.0, True),
            (8.0, 5.5, True),
            (6.0, 5.5, True),
            (8.0, 5.5, False),
            (8.0, 2.0, True),
            (6.0, 2.0, True),
        ]

    def pose_callback(self, msg):
        self.pose = msg

    def set_pen(self, down):
        req = SetPen.Request()
        req.r = 255
        req.g = 255
        req.b = 255
        req.width = 3
        req.off = 0 if down else 1
        return self.pen_client.call_async(req)

    def stop_turtle(self):
        self.cmd_pub.publish(Twist())

    def loop(self):
        if not self.running or self.pose is None:
            return
        if self.index >= len(self.waypoints):
            self.stop_turtle()
            self.get_logger().info('Dibujo completado')
            self.running = False
            return

        x, y, pen_down = self.waypoints[self.index]

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

        if dist < 0.05:
            self.stop_turtle()
            self.index += 1
            return

        target = math.atan2(dy, dx)
        err = math.atan2(math.sin(target - self.pose.theta),
                         math.cos(target - self.pose.theta))

        cmd = Twist()
        cmd.angular.z = max(-3.0, min(3.0, 5.0 * err))
        if abs(err) < 0.02:
            cmd.linear.x = min(2.0, 1.5 * dist)
        self.cmd_pub.publish(cmd)

    def stop_callback(self, request, response):
        self.running = False
        self.stop_turtle()
        response.success = True
        response.message = 'Dibujo detenido'
        return response

    def resume_callback(self, request, response):
        if self.index >= len(self.waypoints):
            response.success = False
            response.message = 'Ya ha terminado, usa restart'
        else:
            self.running = True
            response.success = True
            response.message = 'Dibujo reanudado'
        return response

    def restart_callback(self, request, response):
        self.stop_turtle()
        self.clear_client.call_async(Empty.Request())
        self.index = 0
        self.pen_index = -1
        self.pen_future = None
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

import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

class ArionXFullMission(Node):
    def __init__(self):
        super().__init__('arionx_full_mission')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Publishers
        self.offboard_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.command_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos_profile)

        self.timer = self.create_timer(0.05, self.timer_callback) # 20Hz Loop
        self.counter = 0
        self.state = "STARTUP" 

    def timer_callback(self):
        # 1. Always send Heartbeat to stay in Offboard mode
        self.publish_offboard_control_mode()

        # 2. STATE MACHINE LOGIC
        if self.state == "STARTUP":
            self.publish_trajectory_setpoint(0.0, 0.0, 0.0) # Stay at origin
            if self.counter > 30: # Wait 1.5 seconds
                self.engage_offboard_mode()
                self.arm_drone()
                self.state = "TAKEOFF"
                self.get_logger().info("--- MISSION START: TAKEOFF TO 3M ---")
            
        elif self.state == "TAKEOFF":
            self.publish_trajectory_setpoint(0.0, 0.0, -3.0) # Go to 3m UP
            if self.counter > 200: # Approx 10 seconds total
                self.state = "HOVER"
                self.get_logger().info("--- HOVERING AT 3M ---")

        elif self.state == "HOVER":
            self.publish_trajectory_setpoint(0.0, 0.0, -3.0) # Stay still
            if self.counter > 400: # Hover for 10 more seconds
                self.state = "LANDING"
                self.get_logger().info("--- DESCENDING FOR LANDING ---")

        elif self.state == "LANDING":
            # Command the drone to touch the ground (0.0) but keep X and Y at 0.0
            self.publish_trajectory_setpoint(0.0, 0.0, 0.1) 
            if self.counter > 550: # Give it time to descend
                self.state = "DISARMING"

        elif self.state == "DISARMING":
            self.disarm_drone() # TURN OFF MOTORS
            self.get_logger().info("--- MISSION COMPLETE: MOTORS OFF ---")
            self.state = "FINISHED"
            # Optional: Kill the node
            # rclpy.shutdown()

        self.counter += 1

    # --- COMMANDS ---
    def arm_drone(self):
        self.send_cmd(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)

    def disarm_drone(self):
        # Param1 = 0.0 tells Pixhawk to stop the motors immediately
        self.send_cmd(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 0.0)

    def engage_offboard_mode(self):
        self.send_cmd(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)

    def send_cmd(self, command, p1=0.0, p2=0.0):
        msg = VehicleCommand(command=command, param1=p1, param2=p2, target_system=1, target_component=1, from_external=True)
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.command_pub.publish(msg)

    def publish_offboard_control_mode(self):
        msg = OffboardControlMode(position=True, timestamp=int(self.get_clock().now().nanoseconds / 1000))
        self.offboard_pub.publish(msg)

    def publish_trajectory_setpoint(self, x, y, z):
        msg = TrajectorySetpoint(position=[x, y, z], yaw=0.0, timestamp=int(self.get_clock().now().nanoseconds / 1000))
        self.trajectory_pub.publish(msg)

def main():
    rclpy.init()
    rclpy.spin(ArionXFullMission())

if __name__ == '__main__':
    main()
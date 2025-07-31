import time
import os
import unittest
from eip.client import EIPBaseClient
from eip.controller_libraries.nanotec_motor_controller.NanotecCE5MotorController import NanotecCE5MotorController

accel = 1000  # RPM
decel = 1000  # RPM
speed = 100  # RPM
open = 5000
close = -5000
current = 1000  # mA
voltage = 12000  # 6.16V
count = 0
target = 5000
lastReading = 0
try:
    motor = NanotecCE5MotorController(deviceIpAddress="195.168.1.100")
    time.sleep(1)
    motor.reset_fault()

    # motor.write_pole_pair_count(stepAngle=1.8)
    motor.write_max_motor_voltage(voltageValue=voltage)
    motor.write_max_motor_current(currentValue=current)
    motor.write_rated_motor_current(currentValue=current)  # Save parameters
    # motor.write_acceleration(accelValue=accel)
    # motor.write_deceleration(decelValue=decel)
    motor.write_analog_1_mode("current")
    motor.configure_analog_current()
    motor.write_closed_loop_mode()
    print(motor.od_read(index=0x3321, subindex=0x01, signed=True))
    # motor.write_open_loop_mode()
    # print(motor.is_closed_loop())
    # motor.reset_fault()
    motor.move_to_position(pdiCmd="ProfileVelocity", targetPosition=300, maxSpeed=speed, bypassError=True)

    # motor.auto_setup()

    # motor.enable_current_reduction(idleTimeout=5000, currRedPercent=95)

    #     print(f"Current draw: {motor.read_actual_current()}")
    print(f"Max Current: {motor.read_max_motor_current()}")
    print(f"Rated Current: {motor.read_rated_motor_current()}")
    print(f"Voltage: {motor.read_max_motor_voltage()}")
#     print(f"Open Loop? {motor.is_open_loop()}")
#     print(f"Current Reduction idle time: {motor.read_current_reduction_idle_time()}")
#     print(f"Current Reduction Enable: {motor.read_current_reduction_status()}")
#     print(f"Current Reduction Percent: {motor.read_current_reduction_value()}")
#     # motor.move_to_position(pdiCmd="ProfilePosRel", targetPosition=5000, maxSpeed=speed, bypassError=True, failCountThreshold=50000)
#     # print(motor.read_analog_1_input())
#     motor.move_to_position(pdiCmd="ProfileVelocity", targetPosition=600, maxSpeed=speed, bypassError=False, failCountThreshold=50000)

except Exception as e:
    print(e)
    motor.move_to_position(pdiCmd="ProfileVelocity", targetPosition=0, maxSpeed=speed, bypassError=True)
    motor.eeipClient.forward_close()
    motor.eeipClient.unregister_session()
    print("Closed Session")
try:
    while True:
        time.sleep(0.1)
        print((motor.read_analog_1_input() / 1000) * 1.0137)
        print(os.system("ping -c 1 195.168.1.100") == 0)
        reading = motor.read_analog_1_input()
        if reading == lastReading:
            # print("Readings Equal")
            count += 1
        else:
            count = 0
        if count >= 100:
            print("BREAKING!!!!")
            motor.eeipClient.forward_close()
            motor.eeipClient.unregister_session()
            print("Session unregistered")
            time.sleep(8)
            motor = NanotecCE5MotorController(deviceIpAddress="195.168.1.100")
            motor.write_analog_1_mode("current")
            motor.configure_analog_current()
            motor.move_to_position(pdiCmd="ProfileVelocity", targetPosition=100, maxSpeed=speed, bypassError=True)
            count = 0
        # print(reading)
        # print(count)
        lastReading = reading

except KeyboardInterrupt:
    print("Stopping...")
    motor.move_to_position(pdiCmd="ProfileVelocity", targetPosition=0, maxSpeed=speed, bypassError=True)
    time.sleep(1)

finally:
    # motor.move_to_position(pdiCmd="ProfilePosRel", targetPosition=close, maxSpeed=speed, bypassError=True)
    motor.eeipClient.forward_close()
    motor.eeipClient.unregister_session()
    print("Closed Session")

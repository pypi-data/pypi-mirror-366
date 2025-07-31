import time
import unittest
from eip.client import EIPBaseClient
from eip.controller_libraries.nanotec_motor_controller.NanotecCE5MotorController import NanotecCE5MotorController


class TestCE5MotorController(unittest.TestCase):
    controller: NanotecCE5MotorController = None  # Class-level attribute to track the controller

    @classmethod
    def setUpClass(cls):
        """Set up the motor controller connection once before all tests."""
        cls.controller = NanotecCE5MotorController(deviceIpAddress="195.168.1.100")
        print("Motor connection established...")
        cls.controller.reset_fault()

    @classmethod
    def tearDownClass(cls):
        """Clean up the motor controller connection once after all tests."""
        cls.controller.eeipClient.forward_close()
        cls.controller.eeipClient.unregister_session()
        print("Motor connection closed...")

    def test_01_auto_setup(self):
        print("Starting Auto Setup...")
        self.controller.auto_setup()
        print("Auto Setup Complete!")

    def test_02_enable_current_reduction(self):
        idleTimeout = 500
        currRedPercent = 90
        self.controller.enable_current_reduction(idleTimeout=idleTimeout, currRedPercent=currRedPercent)
        self.assertEqual(self.controller.read_current_reduction_idle_time(), idleTimeout)
        self.assertEqual(self.controller.read_current_reduction_value(), -abs(currRedPercent))
        self.assertTrue(self.controller.read_current_reduction_status())
        self.controller.disable_current_reduction()
        self.assertFalse(self.controller.read_current_reduction_status())
        print(f"Current Reduction disabled...")

    def test_03_read_loop_configuration(self):
        self.controller.write_open_loop_mode()
        openLoop = self.controller.is_open_loop()
        closedLoop = self.controller.is_closed_loop()
        self.assertTrue(openLoop)
        self.assertFalse(closedLoop)
        self.controller.write_closed_loop_mode()
        openLoop = self.controller.is_open_loop()
        closedLoop = self.controller.is_closed_loop()
        self.assertTrue(closedLoop)
        self.assertFalse(openLoop)
        print(f"Controller is in {"open-loop" if openLoop else "closed-loop" } mode...")

    def test_04_read_write_pole_pair_count(self):
        initial = self.controller.read_pole_pair_count()
        print(f"Starting pole Pair Count: {initial}")
        self.controller.write_pole_pair_count(0.9)
        polePairValue1 = self.controller.read_pole_pair_count()
        self.assertEqual(polePairValue1, 100)
        self.controller.write_pole_pair_count(1.8)
        polePairValue2 = self.controller.read_pole_pair_count()
        self.assertEqual(polePairValue2, 50)
        print(f"Motor pole pairs set to 100 and then to 50 sucessfully")

    def test_05_read_write_acceleration(self):
        """Test that the controller can set the acceleration value"""
        value1 = 2000
        value2 = 2100
        self.controller.write_acceleration(accelValue=value1)
        accelValue = self.controller.read_acceleration()
        self.assertEqual(accelValue, value1)
        self.controller.write_acceleration(accelValue=value2)
        accelValue = self.controller.read_acceleration()
        self.assertEqual(accelValue, value2)
        print("Motor acceleration written and read...")

    def test_06_read_write_deceleration(self):
        """Test that the controller can set the deceleration value"""
        value1 = 2000
        value2 = 2100
        self.controller.write_deceleration(decelValue=value1)
        decelValue = self.controller.read_deceleration()
        self.assertEqual(decelValue, value1)
        self.controller.write_deceleration(decelValue=value2)
        decelValue = self.controller.read_deceleration()
        self.assertEqual(decelValue, value2)
        print("Motor deceleration written and read...")

    def test_07_read_write_motor_current(self):
        value1 = 4000
        value2 = 1000
        self.controller.write_max_motor_current(currentValue=value1)
        maValue1 = self.controller.read_max_motor_current()
        self.assertEqual(value1, maValue1)
        self.controller.write_max_motor_current(currentValue=value2)
        maValue2 = self.controller.read_max_motor_current()
        self.assertEqual(value2, maValue2)
        print(f"Max motor current values written and read...")
        self.controller.write_rated_motor_current(4000)
        self.assertTrue(self.controller.read_rated_motor_current(), 4000)
        self.controller.write_rated_motor_current(1000)
        self.assertTrue(self.controller.read_rated_motor_current(), 1000)
        print(f"Max rated motor current values written and read...")

    def test_08_read_write_motor_voltage(self):
        self.controller.write_max_motor_voltage(12000)
        voltage = self.controller.read_max_motor_voltage()
        self.assertEqual(voltage, 12000)
        print("Voltage set to 12V...")

    def test_09_analog_configurations(self):
        self.controller.configure_analog_current()
        self.controller.write_analog_1_mode("current")
        self.controller.write_analog_2_mode("current")
        self.assertEqual(self.controller.read_analog_1_mode(), "current")
        self.assertEqual(self.controller.read_analog_2_mode(), "current")
        self.controller.write_analog_1_mode("voltage")
        self.assertEqual(self.controller.read_analog_1_mode(), "voltage")
        self.assertEqual(self.controller.read_analog_2_mode(), "current")
        self.controller.write_analog_1_mode("current")
        self.controller.write_analog_2_mode("Current")
        self.assertEqual(self.controller.read_analog_1_mode(), "current")
        self.assertEqual(self.controller.read_analog_2_mode(), "current")
        self.controller.write_analog_2_mode("Voltage")
        self.assertEqual(self.controller.read_analog_1_mode(), "current")
        self.assertEqual(self.controller.read_analog_2_mode(), "voltage")
        self.controller.write_analog_1_mode("voltage")
        self.controller.write_analog_2_mode("voltage")
        self.assertEqual(self.controller.read_analog_1_mode(), "voltage")
        self.assertEqual(self.controller.read_analog_2_mode(), "voltage")
        self.controller.write_analog_1_mode("current")
        self.assertEqual(self.controller.read_analog_1_mode(), "current")
        self.assertEqual(self.controller.read_analog_2_mode(), "voltage")
        self.controller.write_analog_1_mode("voltage")
        self.controller.write_analog_2_mode("voltage")
        self.assertEqual(self.controller.read_analog_1_mode(), "voltage")
        self.assertEqual(self.controller.read_analog_2_mode(), "voltage")
        self.controller.write_analog_2_mode("cUrrent")
        self.assertEqual(self.controller.read_analog_1_mode(), "voltage")
        self.assertEqual(self.controller.read_analog_2_mode(), "current")
        with self.assertRaises(ValueError):
            self.controller.write_analog_2_mode("GirlBossGaslightGatekeep")
        self.controller.write_analog_1_mode("current")
        self.controller.write_analog_2_mode("current")
        print("Configured Analog Inputs...")

    def test_10_move_pos_rel(self):
        """Test sending relative position move command to 11000."""
        self.controller.move_to_position(pdiCmd="ProfilePosRel", targetPosition=5000, maxSpeed=1000, bypassError=True)
        print("Motor moved to 5000 steps, move relative command functional...")
        self.controller.move_to_position(pdiCmd="ProfilePosRel", targetPosition=-5000, maxSpeed=1000, bypassError=True)
        print("Motor moved to -5000 steps, move relative command functional...")

    def test_11_move_twice_pos_rel(self):
        """Test sending relative position move back and forth one time to test the toggle function."""
        self.controller.move_to_position(pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000)
        self.controller.move_to_position(pdiCmd="ProfilePosRel", targetPosition=-11000, maxSpeed=2000)
        self.controller.move_to_position(pdiCmd="ProfilePosRel", targetPosition=-11000, maxSpeed=2000)
        print(f"Motor moved two times, toggle functional...")

    def test_12_move_0_pos_abs(self):
        """Test sending absolute position move command to 0."""
        self.controller.move_to_position(pdiCmd="ProfilePosAbs", targetPosition=0, maxSpeed=2000)
        print("Motor moved to 0 steps, move abs command functional...")

    def test_13_move_11000_pos_abs(self):
        """Test sending absolute position move command to 0."""
        self.controller.move_to_position(pdiCmd="ProfilePosAbs", targetPosition=11000, maxSpeed=2000)
        self.controller.move_to_position(pdiCmd="ProfilePosAbs", targetPosition=0, maxSpeed=2000)
        print("Motor moved to 11000 steps, move abs command functional...")

    def test_14_read_field_forming_current(self):
        fieldFormingCurrentValue = []
        for i in range(0, 20):
            fieldFormingCurrentValue.append(self.controller.read_field_forming_current())
        print(f"Field Forming Current Value: {fieldFormingCurrentValue} mA")

    def test_15_read_torque_forming_current(self):
        torqueFormingCurrentValue = []
        for i in range(0, 20):
            torqueFormingCurrentValue.append(self.controller.read_torque_forming_current())
        print(f"Torque Forming Current Value: {torqueFormingCurrentValue} mA")

    def test_16_read_actual_current(self):
        actualCurrentValue = []
        for i in range(0, 20):
            actualCurrentValue.append(self.controller.read_actual_current())
        print(f"Actual Current Value: {actualCurrentValue} mA")

    def test_17_move_and_gather_torque_current_average(self):
        filterBelow = 50
        returnData = self.controller.move_with_torque_current_avg(
            pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=100, failCountThreshold=10000
        )
        print(f"No Filter Average Current: {returnData['average']} --- Dataset: {returnData['data']}")
        returnData = self.controller.move_with_torque_current_avg(
            pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000, filterBelow=filterBelow
        )
        print(f"Filter Below {filterBelow} Average Current: {returnData['average']} --- Dataset: {returnData['data']}")
        returnData = self.controller.move_with_torque_current_avg(pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000)
        print(f"No Filter Average Current: {returnData['average']} --- Dataset: {returnData['data']}")
        returnData = self.controller.move_with_torque_current_avg(
            pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000, filterBelow=filterBelow
        )
        print(f"Filter Below {filterBelow} Average Current: {returnData['average']} --- Dataset: {returnData['data']}")

    def test_18_raise_motor_value_error(self):
        print("Hold the motor in place for error testing...")
        time.sleep(5)
        self.controller.set_failure_timer_duration(1)
        with self.assertRaises(RuntimeError):
            self.controller.move_to_position(pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000)
        with self.assertRaises(RuntimeError):
            self.controller.move_with_torque_current_avg(pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000)
        print("Motor correctly raised RuntimeErrors...")
        self.controller.move_to_position(pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000, bypassError=True)
        self.controller.move_with_torque_current_avg(pdiCmd="ProfilePosRel", targetPosition=11000, maxSpeed=2000, bypassError=True)
        print("Motor correctly bypassed movement errors, let go of motor...")
        time.sleep(5)

    def test_19_move_with_velocity(self):
        startTime = time.perf_counter()
        targetPosition = 2000
        print("Bring motor to speed...")
        self.controller.set_failure_timer_duration(5)
        self.controller.move_to_position(pdiCmd="ProfileVelocity", targetPosition=targetPosition, maxSpeed=0)
        while (time.perf_counter() - startTime) < 2:
            time.sleep(0.01)
            targetPosition += 10
            self.controller.move_to_position(pdiCmd="ProfileVelocity", targetPosition=targetPosition, maxSpeed=0)
        print("Stop Motor...")
        self.controller.move_to_position(pdiCmd="ProfileVelocity", targetPosition=0, maxSpeed=0)

    def test_20_digital_outputs(self):
        self.controller.write_digital_output(
            outputIndex=1,
            outputValue=0,
        )
        self.controller.write_digital_output(
            outputIndex=2,
            outputValue=0,
        )
        self.controller.write_digital_output(
            outputIndex=3,
            outputValue=0,
        )
        time.sleep(3)
        self.assertEqual(self.controller.read_digital_output(outputIndex=1), False)
        self.assertEqual(self.controller.read_digital_output(outputIndex=2), False)
        self.assertEqual(self.controller.read_digital_output(outputIndex=3), False)
        self.controller.write_digital_output(
            outputIndex=1,
            outputValue=1,
        )
        self.assertEqual(self.controller.read_digital_output(outputIndex=1), True)
        self.assertEqual(self.controller.read_digital_output(outputIndex=2), False)
        self.assertEqual(self.controller.read_digital_output(outputIndex=3), False)


if __name__ == "__main__":
    unittest.main()

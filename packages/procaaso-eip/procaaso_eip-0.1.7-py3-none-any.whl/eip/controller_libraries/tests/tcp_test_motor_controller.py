import time
import unittest
from eip.client import EIPBaseClient
from eip.controller_libraries.nanotec_motor_controller.NanotecC5E11ExplicitController import NanotecC5E11ExplicitController


class TestCE5MotorController(unittest.TestCase):
    controller: NanotecC5E11ExplicitController = None  # Class-level attribute to track the controller

    @classmethod
    def setUpClass(cls):
        """Set up the motor controller connection once before all tests."""
        cls.controller: NanotecC5E11ExplicitController = NanotecC5E11ExplicitController(deviceIpAddress="195.168.1.100")

        print("Motor connection established...")

    @classmethod
    def tearDownClass(cls):
        """Clean up the motor controller connection once after all tests."""
        cls.controller.eeipClient.unregister_session()
        print("Motor connection closed...")

    def test_01_auto_setup(self):
        print("Testing Auto Setup...")
        self.controller.set_auto_setup()

    def test_02_loop_configuration(self):
        print("Testing Loop Configuration...")
        self.controller.set_open_loop()
        self.assertTrue(self.controller.get_is_open_loop())
        self.assertFalse(self.controller.get_is_closed_loop())
        self.controller.set_closed_loop()
        self.assertFalse(self.controller.get_is_open_loop())
        self.assertTrue(self.controller.get_is_closed_loop())
        self.controller.set_open_loop()
        self.assertTrue(self.controller.get_is_open_loop())
        self.assertFalse(self.controller.get_is_closed_loop())

    def test_03_current_reduction(self):
        print("Testing Current Reduction...")
        self.controller.set_enable_current_reduction()
        dict = self.controller.get_current_reduction_settings()
        self.assertEqual(dict["Current Reduction Enabled"], True)
        self.assertEqual(dict["Idle Timeout"], 500)
        self.assertEqual(dict["Reduction Percent"], -90)
        self.controller.set_disable_current_reduction()
        dict = self.controller.get_current_reduction_settings()
        self.assertEqual(dict["Current Reduction Enabled"], False)
        self.assertEqual(dict["Idle Timeout"], 500)
        self.assertEqual(dict["Reduction Percent"], -90)
        self.controller.set_enable_current_reduction()
        dict = self.controller.get_current_reduction_settings()
        self.assertEqual(dict["Current Reduction Enabled"], True)
        self.assertEqual(dict["Idle Timeout"], 500)
        self.assertEqual(dict["Reduction Percent"], -90)

    def test_04_pole_pair(self):
        print("Testing Pole Pair...")
        self.assertTrue(self.controller.set_pole_pair(0.9))
        self.assertEqual(self.controller.get_pole_pair(), 100)
        self.assertTrue(self.controller.set_pole_pair(1.8))
        self.assertEqual(self.controller.get_pole_pair(), 50)

    def test_05_relative_movement(self):
        print("Testing Relative Movement Command...")
        self.controller.set_move(moveType="relative", targetPosition=1000, maxSpeed=300)
        self.controller.set_move(moveType="RelAtivE", targetPosition=-1000, maxSpeed=300)

    def test_06_analog_config(self):
        print(f"Testing Analog Config...")
        self.controller.set_analog_config()
        dict = self.controller.get_analog_config()
        self.assertEqual(dict["Analog 1 Offset"], 0)
        self.assertEqual(dict["Analog 1 Upper Limit"], 20000)
        self.assertEqual(dict["Analog 1 ADC Resolution"], 1023)
        self.assertEqual(dict["Analog 2 Offset"], 0)
        self.assertEqual(dict["Analog 2 Upper Limit"], 20000)
        self.assertEqual(dict["Analog 2 ADC Resolution"], 1023)
        print("Testinig Analog Modes...")
        self.controller.set_analog_1_mode("voltage")
        self.controller.set_analog_2_mode("current")
        self.assertEqual(self.controller.get_analog_1_mode(), "voltage")
        self.assertEqual(self.controller.get_analog_2_mode(), "current")
        self.controller.set_analog_1_mode("current")
        self.controller.set_analog_2_mode("voltage")
        self.assertEqual(self.controller.get_analog_1_mode(), "current")
        self.assertEqual(self.controller.get_analog_2_mode(), "voltage")
        self.controller.set_analog_1_mode("voltage")
        self.controller.set_analog_2_mode("voltage")
        self.assertEqual(self.controller.get_analog_1_mode(), "voltage")
        self.assertEqual(self.controller.get_analog_2_mode(), "voltage")
        self.controller.set_analog_1_mode("current")
        self.controller.set_analog_2_mode("current")
        self.assertEqual(self.controller.get_analog_1_mode(), "current")
        self.assertEqual(self.controller.get_analog_2_mode(), "current")

    def test_07_digital_outputs(self):
        print("Testing Digital Outputs...")
        self.controller.set_digital_output(1, 0)
        self.assertFalse(self.controller.get_digital_output(1))
        time.sleep(2)
        self.controller.set_digital_output(1, 1)
        self.assertTrue(self.controller.get_digital_output(1))
        self.controller.set_digital_output(5, 1)
        self.assertTrue(self.controller.get_digital_output(5))
        self.controller.set_digital_output(5, 0)
        self.assertFalse(self.controller.get_digital_output(5))

    def test_08_current_monitoring(self):
        print("Testing Current Monitoring...")
        filterBelow = 50
        data = self.controller.set_move_torque_current_avg(moveType="relative", targetPosition=5000, maxSpeed=300, filterBelow=filterBelow)
        print(f"Filter Below {filterBelow} Average Current: {data['average']} --- Dataset: {data['data']}")
        data = self.controller.set_move_torque_current_avg(
            moveType="relative",
            targetPosition=-5000,
            maxSpeed=300,
        )
        print(f"No Filter Below Average Current: {data['average']} --- Dataset: {data['data']}")

    def test_09_voltage_limit(self):
        print("Testing Voltage Limit...")
        self.controller.set_max_voltage(6000)
        self.assertEqual(self.controller.get_max_voltage(), 6000)
        self.controller.set_max_voltage(12000)
        self.assertEqual(self.controller.get_max_voltage(), 12000)

    def test_10_current_limit(self):
        print("Testing Current Limit...")
        self.controller.set_max_current(1000)
        self.assertEqual(self.controller.get_max_current(), 1000)
        self.controller.set_max_current(1800)
        self.assertEqual(self.controller.get_max_current(), 1800)

    def test_11_accel_decel(self):
        print("Testing Acceleration and Deceleration...")
        self.controller.set_acceleration(accelValue=5000)
        self.assertEqual(self.controller.get_accleration(), 5000)
        self.controller.set_acceleration(accelValue=2000)
        self.assertEqual(self.controller.get_accleration(), 2000)
        self.controller.set_deceleration(decelValue=5000)
        self.assertEqual(self.controller.get_deceleration(), 5000)
        self.controller.set_deceleration(decelValue=2000)
        self.assertEqual(self.controller.get_deceleration(), 2000)


if __name__ == "__main__":
    unittest.main()

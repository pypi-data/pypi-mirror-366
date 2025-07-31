import time
from random import uniform
from eip.client import EIPBaseClient
from eip.models import OutputAssembly, InputAssembly


class NanotecCE5MotorController:
    def __init__(
        self,
        deviceIpAddress: str,
        originatorUdpPort: int = 2222,
        lockUdpPort: bool = True,
        inputId: int = 0x68,
        inputSize: int = 8,
        inputRPI: int = 10000,
        outputId: int = 0x69,
        outputSize: int = 8,
        outputRPI: int = 10000,
    ):
        """
        Initialize the Nanotec C5-E-11 Motor Controller.

        Parameters:
        deviceIpAddress (str): The IP address of the motor controller.
        originatorUdpPort (int): The UDP port used for communication. Default is 2222.
        lockUdpPort (bool): Whether to lock the UDP port. Default is True.
        inputId (int): The input assembly ID. Default is 0x68.
        inputSize (int): The size of the input assembly in bytes. Default is 8.
        inputRPI (int): The Requested Packet Interval (RPI) for input in microseconds. Default is 10000.
        outputId (int): The output assembly ID. Default is 0x69.
        outputSize (int): The size of the output assembly in bytes. Default is 8.
        outputRPI (int): The Requested Packet Interval (RPI) for output in microseconds. Default is 10000.

        Raises:
        Exception: If an error occurs while initializing communication with the motor controller.

        Notes:
        - Initializes an EtherNet/IP client for communication with the controller.
        - Registers a session with the motor controller using the provided IP address.
        - Configures input and output assembly settings.
        - Opens a communication session with the controller.
        """
        try:
            self.eeipClient: EIPBaseClient = EIPBaseClient(originator_udp_port=originatorUdpPort, lock_udp_port=lockUdpPort)
        except Exception as e:
            raise e
        try:
            self.eeipClient.list_identity()  # Gather a list of potential targets
        except Exception as e:
            raise e
        try:
            self.eeipClient.register_session(deviceIpAddress)
        except Exception as e:
            raise e
        self.eeipClient.output_assembly.output_assembly = outputId
        self.eeipClient.output_assembly.output_size = outputSize
        self.eeipClient.output_assembly.output_rpi = outputRPI
        self.eeipClient.input_assembly.input_assembly = inputId
        self.eeipClient.input_assembly.input_size = inputSize
        self.eeipClient.input_assembly.input_rpi = inputRPI
        try:
            self.eeipClient.forward_open()
        except Exception as e:
            raise e
        self.pdiCmd = {
            "Switch Off": 1,
            "Clear Error": 2,
            "Quick Stop": 3,
            "OD-Read": 14,
            "OD-Write": 15,
            "Auto Setup": 16,
            "Home-Current_Pos": 17,
            "Homing": 18,
            "ProfilePosAbs": 20,
            "ProfilePosRel": 21,
            "ProfileVelocity": 23,
            "ProfileTorque": 25,
        }
        self._pdiStatusMapping = {
            "PdiStatusOperationEnabled": 0,
            "PdiStatusWarning": 1,
            "PdiStatusFault": 2,
            "PdiStatusTargetReached": 3,
            "PdiStatusFollowingError": 4,
            "PdiStatusLimitReached": 5,
            "PdiStatusQsHaltBit": 7,
            "PdiStatusHomingDone": 3,
            "PdiStatusAutosetupDone": 4,
            "PdiStatusToggleCmd": 6,
            "PdiStatusError": 7,
        }
        self.stableCount = 0
        self.lastPdiStatus = None
        self.pdiStatus = None
        self.toggle = False
        self.timerDuration = 5
        self.failureTimer = time.perf_counter()

    def is_open_loop(self) -> bool:
        """
        Determine if the motor controller is configured for open-loop operation.

        Returns:
        bool: True if the controller is in open-loop mode, False if it is in closed-loop mode.

        Notes:
        - Reads from index 0x3202, subindex 0x00 in the object dictionary.
        - Checks bit position 0 to determine if the controller is operating in open-loop mode.
        - If the bit is 0, the controller is in open-loop mode; otherwise, it is in closed-loop mode.
        """
        statusWord = self.od_read(index=0x3202, subindex=0x00)
        return self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=0,
            expectedValue=0,
        )

    def is_closed_loop(self) -> bool:
        """
        Determine if the motor controller is configured for closed-loop operation.

        Returns:
        bool: True if the controller is in closed-loop mode, False if it is in open-loop mode.

        Notes:
        - Reads from index 0x3202, subindex 0x00 in the object dictionary.
        - Checks bit position 0 to determine if the controller is operating in closed-loop mode.
        - If the bit is 1, the controller is in closed-loop mode; otherwise, it is in open-loop mode.
        """
        statusWord = self.od_read(index=0x3202, subindex=0x00)
        return self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=0,
            expectedValue=1,
        )

    def write_open_loop_mode(self):
        """
        Set the Motor Drive Submode Select to Open-Loop mode. Check to see if we already in Open-Loop, if so return.

        Parameters:
        None

        Returns:
        None

        Notes:
        - Writes to index 0x3202 in the object dictionary, which controls the motor sub mode functions.
        - Toggling this value is not possible in the Operation Enable State.
        - The bit for Open/Closed Loop (CL/OL) is bit 0 in  3202
        """
        statusWord = self.od_read(index=0x3202, subindex=0x00)
        isOpenLoop = self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=0,
            expectedValue=0,
        )
        if isOpenLoop:
            return
        # Modify the specified output bit
        modifiedByte = self._modify_bit(bitIndex=0, value=0, byteToModify=statusWord[4])
        statusWord[4] = modifiedByte
        # Convert the modified byte array to an integer
        modifiedValue = int.from_bytes(statusWord[4:8], byteorder="little", signed=False)
        self.od_write(index=0x3202, subindex=0x00, value=modifiedValue, signed=False)

    def write_closed_loop_mode(self):
        """
        Set the Motor Drive Submode Select to Closed-Loop mode. Check to see if we already in Closed-Loop, if so return.

        Parameters:
        None

        Returns:
        None

        Notes:
        - Writes to index 0x3202 in the object dictionary, which controls the motor sub mode functions.
        - Toggling this value is not possible in the Operation Enable State.
        - The bit for Open/Closed Loop (CL/OL) is bit 0 in 0x3202
        """
        statusWord = self.od_read(index=0x3202, subindex=0x00)
        isClosedLoop = self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=0,
            expectedValue=1,
        )
        if isClosedLoop:
            return
        # Modify the specified output bit
        modifiedByte = self._modify_bit(bitIndex=0, value=1, byteToModify=statusWord[4])
        statusWord[4] = modifiedByte
        # Convert the modified byte array to an integer
        modifiedValue = int.from_bytes(statusWord[4:8], byteorder="little", signed=False)
        self.od_write(index=0x3202, subindex=0x00, value=modifiedValue, signed=False)

    def read_pole_pair_count(self):
        """
        Read the pole pair count from the motor controller.

        Returns:
        int: The current pole pair count read from the motor controller.

        Notes:
        - Reads from index 0x2030, subindex 0x00 in the object dictionary.
        - The pole pair count determines the relationship between the motor's electrical input and mechanical output.
        - This information is useful for ensuring proper motor operation and configuration.
        - The returned value is converted from bytes with a data size of 32 bits and unsigned format.
        """
        statusWord = self.od_read(index=0x2030, subindex=0x00, signed=False)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=False)

    def write_pole_pair_count(self, stepAngle: float = 1.8):
        """
        Set the pole pair number using an Object Dictionary (OD) write.

        Parameters:
        stepAngle (float): The step angle of the motor. Valid values are 0.9 or 1.8. Default is 1.8.

        Returns:
        None

        Raises:
        ValueError: If the provided step angle is not 0.9 or 1.8.

        Notes:
        - Writes to index 0x2030, subindex 0x00 in the object dictionary.
        - Sets the value to 50 for a step angle of 1.8.
        - Sets the value to 100 for a step angle of 0.9.
        """
        if stepAngle in [1.8]:
            self.od_write(index=0x2030, subindex=0x00, value=50)
        elif stepAngle in [0.9]:
            self.od_write(index=0x2030, subindex=0x00, value=100)
        else:
            raise ValueError(f"Step Angle {stepAngle} is not a valid value")

    def read_acceleration(self):
        """
        Read the profile acceleration setting from the motor controller.

        Returns:
        int: The profile acceleration value.

        Notes:
        - Reads from index 0x6083, subindex 0x00 in the object dictionary.
        - The value is returned as an unsigned 32-bit integer.
        """
        statusWord = self.od_read(index=0x6083, subindex=0x00)
        return self.convert_bytes(value=statusWord, dataSize=32)

    def write_acceleration(self, accelValue: int, index: int = 0x6083, subindex: int = 0x00):
        """
        Set the profile acceleration using an Object Dictionary (OD) write.

        Parameters:
        accelValue (int): The acceleration value to write.
        index (int): The index in the object dictionary. Default is 0x6083.
        subindex (int): The subindex in the object dictionary. Default is 0x00.

        Returns:
        None

        Notes:
        - Writes to index 0x6083 in the object dictionary, which controls the acceleration profile.
        - The acceleration value should be within the motor's supported range.
        """
        self.od_write(index=index, subindex=subindex, value=accelValue)

    def read_deceleration(self):
        """
        Read the profile deceleration setting from the motor controller.

        Returns:
        int: The profile deceleration value.

        Notes:
        - Reads from index 0x6084, subindex 0x00 in the object dictionary.
        - The value is returned as an unsigned 32-bit integer.
        """
        statusWord = self.od_read(index=0x6084, subindex=0x00)
        return self.convert_bytes(value=statusWord, dataSize=32)

    def write_deceleration(self, decelValue: int, index: int = 0x6084, subindex: int = 0x00):
        """
        Set the profile deceleration using an Object Dictionary (OD) write.

        Parameters:
        decelValue (int): The deceleration value to write.
        index (int): The index in the object dictionary. Default is 0x6084.
        subindex (int): The subindex in the object dictionary. Default is 0x00.

        Returns:
        None

        Notes:
        - Writes to index 0x6084 in the object dictionary, which controls the deceleration profile.
        - The deceleration value should be within the motor's supported range.
        """
        self.od_write(index=index, subindex=subindex, value=decelValue)

    def move_to_position(
        self,
        pdiCmd: str,
        targetPosition: int = 5000,
        maxSpeed: int = 200,
        bypassError: bool = False,
    ):
        """
        Move the motor to a specified position.

        Parameters:
        pdiCmd (str): The PDI command to execute (e.g., 'ProfilePosAbs').
        targetPosition (int): The target position in encoder counts. Default is 5000.
        maxSpeed (int): The maximum speed for the movement. Default is 200.
        bypassError (bool): If True, allows the move to continue without raising an error when the timer expires.

        Returns:
        None

        Notes:
        - Uses `_write_move_command` to initiate the move.
        - Monitors position completion with `monitor_position_reached()`.
        - Uses `_start_timer()` to track movement duration.
        - If `bypassError` is False, raises a `RuntimeError` if the move exceeds the allowed time.
        """
        # Execute the move command
        self._write_move_command(pdiCmd=pdiCmd, targetPosition=targetPosition, maxSpeed=maxSpeed)
        self._start_timer()

        # Monitor until position is reached or timeout occurs
        while not self.monitor_position_reached():
            time.sleep(0.0001)

            # Handle timeout conditions
            if bypassError:
                if self._timer_is_done():
                    break
            else:
                if self._timer_is_done():
                    raise RuntimeError(f"Motor failed to reach position in {self.timerDuration} seconds")

    def read_max_motor_current(self):
        """
        Read the maximum motor current setting from the motor controller.

        Returns:
        int: The maximum motor current in milliamps.

        Notes:
        - Reads from index 0x2031, subindex 0x00 in the object dictionary.
        - The value is returned as an unsigned 32-bit integer.
        """
        statusWord = self.od_read(index=0x2031, subindex=0x00)
        return self.convert_bytes(value=statusWord, dataSize=32)

    def write_max_motor_current(self, currentValue: int = 6000):
        """
        Set the maximum motor current using an Object Dictionary (OD) write.

        Parameters:
        currentValue (int): The maximum current value in milliamps. Default is 6000.
            - The value should be within the motor's current handling capacity.

        Returns:
        None

        Notes:
        - Writes to index 0x2031, subindex 0x00 in the object dictionary.
        - Exceeding the motor's rated current may cause overheating or damage.
        - The value is written as an unsigned integer.
        """
        self.od_write(index=0x2031, subindex=0x00, value=currentValue, signed=False)

    def read_rated_motor_current(self):
        """
        Read the rated motor current setting from the motor controller.

        Returns:
        int: The maximum motor current in milliamps.

        Notes:
        - Reads from index 0x203B, subindex 0x00 in the object dictionary.
        - The value is returned as an unsigned 32-bit integer.
        """
        statusWord = self.od_read(index=0x203B, subindex=0x01)
        return self.convert_bytes(value=statusWord, dataSize=32)

    def write_rated_motor_current(self, currentValue: int = 6000):
        """
        Set the rated motor current using an Object Dictionary (OD) write.

        Parameters:
        currentValue (int): The rated current value in milliamps. Default is 6000.
            - The value should be within the motor's current handling capacity.

        Returns:
        None

        Notes:
        - Writes to index 0x203B, subindex 0x00 in the object dictionary.
        - Exceeding the motor's rated current may cause overheating or damage.
        - The value is written as an unsigned integer.
        """
        self.od_write(index=0x203B, subindex=0x01, value=currentValue, signed=False)

    def read_field_forming_current(self):
        """
        Read the field forming current of the motor.

        This current generates the magnetic field necessary for motor operation. It does not contribute to torque
        but is required for proper motor functionality.

        Returns:
        int: The field forming current value in mA.

        Notes:
        - Reads from index 0x2039, subindex 0x01 in the object dictionary.
        - The returned value is converted from bytes with a data size of 32 bits and signed format.
        """
        statusWord = self.od_read(index=0x2039, subindex=0x01)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=True)

    def read_torque_forming_current(self):
        """
        Read the torque-forming current of the motor.

        This current directly produces torque to drive the motor. When the load increases (e.g., due to a seizing valve),
        this value will rise to compensate.

        Returns:
        int: The torque-forming current value in mA.

        Notes:
        - Reads from index 0x2039, subindex 0x02 in the object dictionary.
        - The returned value is converted from bytes with a data size of 32 bits and signed format.
        """
        statusWord = self.od_read(index=0x2039, subindex=0x02)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=True)

    def read_actual_current(self):
        """
        Read the effective total current scaled to a motor phase.

        This value is particularly useful for monitoring how much current the motor is drawing overall.
        In closed-loop control, it accounts for the sign of the torque-forming current (Iq).

        Returns:
        int: The overall current draw in mA.

        Notes:
        - Reads from index 0x2039, subindex 0x05 in the object dictionary.
        - An increase in this value indicates that the motor is working harder overall.
        - The returned value is converted from bytes with a data size of 32 bits and signed format.
        """
        statusWord = self.od_read(index=0x2039, subindex=0x05)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=True)

    def move_with_torque_current_avg(
        self,
        pdiCmd: str,
        targetPosition: int = 5000,
        maxSpeed: int = 200,
        filterBelow: int = None,
        bypassError: bool = False,
    ) -> dict:
        """
        Execute a move operation while monitoring and averaging torque current.

        Parameters:
        pdiCmd (str): The PDI command to execute (e.g., 'ProfilePosAbs').
        targetPosition (int): The target position in encoder counts. Default is 5000.
        maxSpeed (int): The maximum speed for the movement. Default is 200.
        filterBelow (int, optional): Removes values below this threshold from the current dataset before averaging. Default is None.
        bypassError (bool): If True, allows the move to continue without raising an error when the timer expires.

        Returns:
        dict: A dictionary containing:
            - "average" (int): The average torque current measured during the move.
            - "data" (list): The filtered set of torque current measurements.

        Notes:
        - Inverts torque current readings for negative target positions to maintain consistency in measurement.
        - Uses `_write_move_command` to initiate the move.
        - Monitors position completion with `monitor_position_reached()`.
        - Logs torque current readings during movement.
        - Uses `_timer_is_done()` to determine if the move exceeds the allowed time.
        - Filters the dataset using `_filter_data()` before computing the average.
        """
        currentData = []

        # Determine if movement is negative to adjust current readings
        isNegative = True if targetPosition < 0 else False

        # Execute the move command
        self._write_move_command(pdiCmd=pdiCmd, targetPosition=targetPosition, maxSpeed=maxSpeed)
        self._start_timer()

        # Monitor until position is reached
        while not self.monitor_position_reached():
            time.sleep(0.0001)

            # Capture torque current values, adjusting for negative moves
            if isNegative:
                currentData.append(-1 * (self.read_torque_forming_current()))
            else:
                currentData.append(self.read_torque_forming_current())

            # Handle timeout conditions
            if bypassError:
                if self._timer_is_done():
                    break
            else:
                if self._timer_is_done():
                    raise RuntimeError(f"Motor failed to reach position in {self.timerDuration} seconds")

        # Filter and compute average torque current
        filteredDataSet = self._filter_data(below=True, threshold=filterBelow, dataSet=currentData)
        if len(filteredDataSet) <= 0:
            avgCurrent = 0
        else:
            avgCurrent = sum(filteredDataSet) / len(filteredDataSet)
            avgCurrent = round(avgCurrent)

        return {"average": avgCurrent, "data": filteredDataSet}

    def read_max_motor_voltage(self):
        """
        Read the maximum motor voltage setting from the motor controller.

        Returns:
        int: The maximum motor voltage in millivolts.

        Notes:
        - Reads from index 0x321E, subindex 0x00 in the object dictionary.
        - The value is returned as an unsigned 32-bit integer.
        """
        statusWord = self.od_read(index=0x321E, subindex=0x00)
        return self.convert_bytes(value=statusWord, dataSize=32, byteOrder="little", signed=True)

    def write_max_motor_voltage(self, voltageValue: int = 4000):
        """
        Set the maximum motor voltage using an Object Dictionary (OD) write.

        Parameters:
        voltageValue (int): The maximum voltage value in millivolts. Default is 4000.
            - The value should be within the motor's voltage handling capacity.

        Returns:
        None

        Notes:
        - Writes to index 0x321E, subindex 0x00 in the object dictionary.
        - Exceeding the motor's rated voltage may cause overheating or damage.
        - The value is written as an unsigned integer.
        - Values <= 1000 are used as percentage of supplied voltage, so 995 would 99.5% of the supplied voltage
        - Values > 1000 are used mV readings, so 12000 would be 12V
        """
        self.od_write(index=0x321E, subindex=0x00, value=voltageValue, signed=False)

    def configure_analog_current(self):
        """
        Configure the analog inputs for current measurement.

        This function sets the offset, upper limit, and ADC resolution for both Analog Input 1 and Analog Input 2.

        Returns:
        None

        Notes:
        - Writes to the following object dictionary indices and subindices:
            - Index 0x3321: Offset (subindex 0x01 for Analog 1, subindex 0x02 for Analog 2).
            - Index 0x3322: Upper limit current in microamps (subindex 0x01 for Analog 1, subindex 0x02 for Analog 2).
            - Index 0x3323: ADC resolution (subindex 0x01 for Analog 1, subindex 0x02 for Analog 2).
        - The upper limit is set to **20000 µA** (20mA).
        - The ADC resolution is set to **1023**, assuming a 10-bit ADC.
        - All values are written as signed integers.
        """
        # Write the offset
        self.od_write(index=0x3321, subindex=0x01, value=0, signed=True)
        # Write the upper limit current in microamps
        self.od_write(index=0x3322, subindex=0x01, value=20000, signed=True)
        # Write the ADC resolution value
        self.od_write(index=0x3323, subindex=0x01, value=1023, signed=True)

        # Write the offset for Analog Input 2
        self.od_write(index=0x3321, subindex=0x02, value=0, signed=True)
        # Write the upper limit current in microamps for Analog Input 2
        self.od_write(index=0x3322, subindex=0x02, value=20000, signed=True)
        # Write the ADC resolution value for Analog Input 2
        self.od_write(index=0x3323, subindex=0x02, value=1023, signed=True)

    def read_analog_1_mode(self) -> str:
        """
        Read the operating mode of Analog Input 1.

        Returns:
        str: "current" if Analog Input 1 is in current mode, "voltage" if in voltage mode.

        Notes:
        - Reads from index 0x3221, subindex 0x00 in the object dictionary.
        - Checks bit position 0 of the returned data to determine the mode.
        - If the bit is set (1), the mode is "current"; otherwise, it is "voltage".
        """
        statusWord = self.od_read(index=0x3221, subindex=0x00)
        isCurrent = self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=0,
            expectedValue=1,
        )

        return "current" if isCurrent else "voltage"

    def write_analog_1_mode(self, mode: str = "current"):
        """
        Set the operating mode for Analog Input 1.

        Parameters:
        mode (str): The desired mode for Analog Input 1. Acceptable values are "current" or "voltage". Default is "current".

        Returns:
        None

        Raises:
        ValueError: If the provided mode is not "current" or "voltage".

        Notes:
        - Reads the current mode of Analog Input 2 using `read_analog_2_mode()`.
        - Determines the appropriate setting based on the combination of Analog Input 1 and Analog Input 2 modes.
        - Writes the mode configuration to index 0x3221, subindex 0x00 in the object dictionary.
        - Uses an encoded integer value to represent the mode settings:
            - 3: Both inputs in current mode.
            - 2: Analog 1 in voltage mode, Analog 2 in current mode.
            - 1: Analog 1 in current mode, Analog 2 in voltage mode.
            - 0: Both inputs in voltage mode.
        """
        if mode.lower() not in ["current", "voltage"]:
            raise ValueError("Mode must be 'current' or 'voltage'")

        mode2 = self.read_analog_2_mode()

        if mode.lower() == "current" and mode2.lower() == "current":
            setValue = 3
        elif mode.lower() == "voltage" and mode2.lower() == "current":
            setValue = 2
        elif mode.lower() == "current" and mode2.lower() == "voltage":
            setValue = 1
        elif mode.lower() == "voltage" and mode2.lower() == "voltage":
            setValue = 0

        self.od_write(index=0x3221, subindex=0x00, value=setValue, signed=True)

    def read_analog_1_input(self) -> int:
        """
        Read the value of Analog Input 1 from the motor controller.

        Returns:
        int: The analog input value, interpreted as a signed 32-bit integer.

        Notes:
        - Reads from index 0x3320, subindex 0x01 in the object dictionary.
        - The value is converted from bytes using a 32-bit signed format.
        - This input can be used for monitoring external sensor data or control signals.
        """
        statusWord = self.od_read(index=0x3320, subindex=0x01)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=True)

    def read_analog_2_mode(self) -> str:
        """
        Read the operating mode of Analog Input 2.

        Returns:
        str: "current" if Analog Input 2 is in current mode, "voltage" if in voltage mode.

        Notes:
        - Reads from index 0x3221, subindex 0x00 in the object dictionary.
        - Checks bit position 1 of the returned data to determine the mode.
        - If the bit is set (1), the mode is "current"; otherwise, it is "voltage".
        """
        statusWord = self.od_read(index=0x3221, subindex=0x00)
        isCurrent = self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=1,
            expectedValue=1,
        )

        return "current" if isCurrent else "voltage"

    def write_analog_2_mode(self, mode: str = "current"):
        """
        Set the operating mode for Analog Input 2.

        Parameters:
        mode (str): The desired mode for Analog Input 2. Acceptable values are "current" or "voltage". Default is "current".

        Returns:
        None

        Raises:
        ValueError: If the provided mode is not "current" or "voltage".

        Notes:
        - Reads the current mode of Analog Input 1 using `read_analog_2_mode()`.
        - Determines the appropriate setting based on the combination of Analog Input 1 and Analog Input 2 modes.
        - Writes the mode configuration to index 0x3221, subindex 0x00 in the object dictionary.
        - Uses an encoded integer value to represent the mode settings:
            - 3: Both inputs in current mode.
            - 2: Analog 1 in voltage mode, Analog 2 in current mode.
            - 1: Analog 1 in current mode, Analog 2 in voltage mode.
            - 0: Both inputs in voltage mode.
        """
        if mode.lower() not in ["current", "voltage"]:
            raise ValueError("Mode must be 'current' or 'voltage'")

        mode1 = self.read_analog_1_mode()

        if mode.lower() == "current" and mode1.lower() == "current":
            setValue = 3
        elif mode.lower() == "voltage" and mode1.lower() == "current":
            setValue = 1
        elif mode.lower() == "current" and mode1.lower() == "voltage":
            setValue = 2
        elif mode.lower() == "voltage" and mode1.lower() == "voltage":
            setValue = 0

        self.od_write(index=0x3221, subindex=0x00, value=setValue, signed=True)

    def read_analog_2_input(self) -> int:
        """
        Read the value of Analog Input 2 from the motor controller.

        Returns:
        int: The analog input value, interpreted as a signed 32-bit integer.

        Notes:
        - Reads from index 0x3320, subindex 0x02 in the object dictionary.
        - The value is converted from bytes using a 32-bit signed format.
        - This input can be used for monitoring external sensor data or control signals.
        """
        statusWord = self.od_read(index=0x3320, subindex=0x02)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=True)

    def read_digital_output(self, outputIndex: int) -> bool:
        """
        Read the state of a digital output from the motor controller.

        Parameters:
        outputIndex (int): The index of the digital output to read (valid values: 1 to 5).

        Returns:
        bool: True if the digital output is high, False if it is low.

        Raises:
        ValueError: If `outputIndex` is not between 1 and 5.

        Notes:
        - Reads from index 0x60FE, subindex 0x01 in the object dictionary.
        - Uses bitwise checking to determine if the specified output is high or low.
        - The bit position is determined by `outputIndex - 1` for correct mapping.
        """
        if outputIndex not in [1, 2, 3, 4, 5]:
            raise ValueError("outputIndex must be between 1 and 5")

        statusWord = self.od_read(index=0x60FE, subindex=0x01)

        # Return False if the output is low, True if the output is high
        return self.check_bit(
            decimalValue=statusWord[6],
            bitPosition=outputIndex - 1,  # Adjust index for zero-based bit position
            expectedValue=1,
        )

    def write_digital_output(self, outputIndex: int, outputValue: int):
        """
        Set the state of a digital output on the motor controller.

        Parameters:
        outputIndex (int): The index of the digital output to modify (valid values: 1 to 5).
        outputValue (int): The desired state of the output (0 for low, 1 for high).

        Returns:
        None

        Raises:
        ValueError: If `outputIndex` is not between 1 and 5.
        ValueError: If `outputValue` is not 0 or 1.

        Notes:
        - Reads the current digital output status from index 0x60FE, subindex 0x01.
        - Modifies the specified output bit using `_modify_bit`.
        - Writes the modified status back to the object dictionary.
        - Uses little-endian byte order for conversion.
        """
        if outputIndex not in [1, 2, 3, 4, 5]:
            raise ValueError("outputIndex must be between 1 and 5")
        if outputValue not in [0, 1]:
            raise ValueError("outputValue must be 0 or 1")

        statusWord = self.od_read(index=0x60FE, subindex=0x01)

        # Modify the specified output bit
        modifiedByte = self._modify_bit(bitIndex=outputIndex - 1, value=outputValue, byteToModify=statusWord[6])
        statusWord[6] = modifiedByte

        # Convert the modified byte array to an integer
        modifiedValue = int.from_bytes(statusWord[4:8], byteorder="little", signed=False)

        # Write the updated value back to the object dictionary
        self.od_write(index=0x60FE, subindex=0x01, value=modifiedValue)

    def enable_current_reduction(self, idleTimeout: int = 500, currRedPercent: int = 90):
        """
        Enable current reduction on the motor controller, which involves multiple steps (see notes).
        When them motor is at a stand still, reduce the current in order to reduce heat build up and power loss.
        This option is only available to motors in open loop mode.

        Parameters:
        idleTimeout (int): The number of Milliseconds the motor must stand still before current reduction activates.
        currRedPercent (int): Percentage of current that will be reduced, i.e. 90 will result in a 90% reduction in allowed current from the rated current value.

        Returns:
        None

        Notes:
        - In object 3202h (Motor Drive Submode Select), set bit 3 (CurRed) to "1".
        - In object 2036h (open-loop current reduction idle time), the time in milliseconds is specified that the motor must be at a standstill (set value is checked) before current reduction is activated.
        - In object 2037h (open-loop current reduction value/factor), the root mean square is specified to which the rated current is to be reduced if current reduction is activated in open loop and the motor is at a standstill.
        """
        if currRedPercent > 100 or currRedPercent < 0:
            raise ValueError(f"currRedPercent must be between 0 and 100, given value: {currRedPercent}")
        else:
            currRedPercent = -abs(currRedPercent)
        statusWord = self.od_read(index=0x3202, subindex=0x00)
        isOpenLoop = self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=0,
            expectedValue=0,
        )
        if not isOpenLoop:  # Move to open loop mode if we are not in that mode
            self.write_open_loop_mode()
        # Modify the specified output bit
        modifiedByte = self._modify_bit(bitIndex=3, value=1, byteToModify=statusWord[4])
        statusWord[4] = modifiedByte
        # Convert the modified byte array to an integer
        modifiedValue = int.from_bytes(statusWord[4:8], byteorder="little", signed=False)
        # Write the current reduction bit to enable
        self.od_write(index=0x3202, subindex=0x00, value=modifiedValue, signed=False)
        # Write the current reduction idle time
        self.od_write(index=0x2036, subindex=0x00, value=idleTimeout, signed=False)
        # Wite the current reduction factor
        self.od_write(index=0x2037, subindex=0x00, value=currRedPercent, signed=True)

    def disable_current_reduction(self):
        """
        Disable the automatic current reduction feature on the motor controller.

        Returns:
        None

        Notes:
        - Reads the control word from index `0x3202`, subindex `0x00`.
        - Modifies bit 3 to disable current reduction.
        - Writes the updated value back to the object dictionary.
        - Uses `_modify_bit()` to manipulate the bit safely.
        """
        statusWord = self.od_read(index=0x3202, subindex=0x00)

        # Modify the specified output bit (bit 3) to disable current reduction
        modifiedByte = self._modify_bit(bitIndex=3, value=0, byteToModify=statusWord[4])
        statusWord[4] = modifiedByte

        # Convert the modified byte array to an integer
        modifiedValue = int.from_bytes(statusWord[4:8], byteorder="little", signed=False)

        # Write the updated value back to disable current reduction
        self.od_write(index=0x3202, subindex=0x00, value=modifiedValue, signed=False)

    def read_current_reduction_idle_time(self) -> int:
        """
        Read the idle time before current reduction activates.

        Returns:
        int: The idle time value in milliseconds.

        Notes:
        - Reads the idle time for current reduction from index `0x2036`, subindex `0x00`.
        - Converts the retrieved byte data into a 32-bit unsigned integer.
        - This value determines how long the motor remains idle before reducing current to save energy.
        """
        statusWord = self.od_read(index=0x2036, subindex=0x00)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=False)

    def read_current_reduction_value(self) -> int:
        """
        Read the current reduction value.

        Returns:
        int: The current reduction percentage.

        Notes:
        - Reads the current reduction setting from index `0x2037`, subindex `0x00`.
        - Converts the retrieved byte data into a 32-bit signed integer.
        - This value represents the percentage of current reduction applied when the motor is idle.
        """
        statusWord = self.od_read(index=0x2037, subindex=0x00)
        return self.convert_bytes(value=statusWord, dataSize=32, signed=True)

    def read_current_reduction_status(self) -> bool:
        """
        Check if current reduction is enabled.

        Returns:
        bool: True if current reduction is enabled, False otherwise.

        Notes:
        - Reads the control word from index `0x3202`, subindex `0x00`.
        - Checks bit position `3` to determine if current reduction is active.
        - Uses `check_bit()` to extract and evaluate the specific bit.
        """
        statusWord = self.od_read(index=0x3202, subindex=0x00)
        return self.check_bit(
            decimalValue=statusWord[4],
            bitPosition=3,
            expectedValue=1,
        )

    def auto_setup(self):
        """
        Initiate the auto setup process on the motor controller.

        Returns:
        None

        Notes:
        - Sends the "Auto Setup" command via PDI-Cmd (2291h:04h).
        - Uses the `pdiCmd` mapping to set the appropriate command value.
        - Introduces a short delay (0.02s) after sending the command.
        - This function is currently incomplete and may require additional implementation.
        """
        writeData = bytearray(8)

        # Step 1: Set Auto Setup command in PDI-Cmd (2291h:04h)
        writeData[7] = self.pdiCmd["Auto Setup"]  # Set the PDI command

        # Send data to the motor controller
        self.eeipClient.output_assembly.iodata = writeData
        while not self.auto_setup_complete():
            time.sleep(0.01)
        return True

    def auto_setup_complete(self):
        """
        Check if the auto setup process has completed successfully.

        Returns:
        bool: True if the auto setup process is complete, False otherwise.

        Notes:
        - Calls `gather_pdi_status` to update the current PDI status.
        - Checks if the "PdiStatusAutosetupDone" bit is set in the PDI status.
        """
        self.gather_pdi_status()
        return self.check_bit(
            decimalValue=self.pdiStatus[1],
            bitPosition=self._pdiStatusMapping["PdiStatusAutosetupDone"],
            expectedValue=1,
        )

    def check_status_error(self):
        """
        Check if an error occurred while executing a command.

        Returns:
        dict: A dictionary containing:
            - "errorPresent" (bool): True if an error is detected, False otherwise.
            - "errorCode" (int or None): The error code if an error is present, otherwise None.

        Notes:
        - Calls `gather_pdi_status` to update the current PDI status.
        - Checks if the "PdiStatusError" bit is set in the PDI status.
        - Error codes can be read from PDIReturnValue (2292h:02h).
        """
        statusWord = self.gather_pdi_status()

        # Check if error bit is set
        errorBitSet = self.check_bit(
            decimalValue=self.pdiStatus[0],
            bitPosition=self._pdiStatusMapping["PdiStatusError"],
            expectedValue=1,
        )

        if errorBitSet:
            return {"errorPresent": True, "errorCode": self.convert_bytes(value=statusWord, dataSize=16, signed=False)}
        else:
            return {"errorPresent": False, "errorCode": None}

    def reset_fault(self):
        """
        Reset the fault condition on the motor controller.

        Returns:
        None

        Notes:
        - Toggles the PDI command to ensure the fault reset is recognized.
        - Uses `pdiCmd["Clear Error"]` to issue the reset command.
        - Implements a ToggleCmd mechanism to properly signal the reset action.
        """
        self.toggle = not self.toggle
        ioData = bytearray(8)  # Initialize the data array

        # Set the PDI command for clearing errors with ToggleCmd
        if self.toggle:
            ioData[7] = self.pdiCmd["Clear Error"]
        else:
            ioData[7] = self.pdiCmd["Clear Error"] + 128  # Set the PDI command with ToggleCmd bit

    def convert_bytes(self, value: bytearray, startReg: int = 4, dataSize: int = 32, signed: bool = False, byteOrder: str = "little"):
        """
        Convert a byte sequence to an integer, interpreting only the relevant bytes.

        Parameters:
        value (bytearray): Bytearray representing the register data.
        startReg (int): The starting register (byte index) to read from. Default is 4.
        dataSize (int): The size of the data in bits (16 or 32). Default is 32.
        signed (bool): Whether the value should be interpreted as a signed integer. Default is False.

        Returns:
        int: The interpreted integer value.

        Notes:
        - Reads 2 bytes for 16-bit values and 4 bytes for 32-bit values.
        - Uses little-endian byte order for conversion.
        - Ensures that only the specified byte range is interpreted.
        """
        # Determine the number of bytes to read based on data size
        if dataSize == 16:
            endReg = startReg + 2  # Only read 2 bytes for 16-bit values
        elif dataSize == 32:
            endReg = startReg + 8  # Read 4 bytes for 32-bit values
        # Convert the specified byte range to an integer
        return int.from_bytes(value[startReg:endReg], byteorder=byteOrder, signed=signed)

    def od_write(self, index: int, subindex: int, value: int, signed: bool = False, pdiCmd: str = None):
        """
        Write data to the Object Dictionary (OD) with ToggleCmd.

        Parameters:
        index (int): The index to write to in the object dictionary.
        subindex (int): The subindex to write to in the object dictionary.
        value (int): The value to write.
        signed (bool): Whether the value should be interpreted as signed. Default is False.
        pdiCmd (str, optional): A specific PDI command to use instead of the default OD-Write command.

        Returns:
        None

        Notes:
        - Writes to PDI-SetValue1 (2291h:01h), PDI-SetValue2 (2291h:02h), and PDI-SetValue3 (2291h:03h).
        - Uses ToggleCmd to ensure the command is recognized.
        - If `pdiCmd` is provided, it will override the default OD-Write command.
        - The value is written in little-endian byte order.
        """
        self.toggle = not self.toggle
        writeData = bytearray(8)

        # Step 1: Set value in PDI-SetValue1 (2291h:01h)
        writeData[0:4] = value.to_bytes(4, byteorder="little", signed=signed)

        # Step 2: Set index in PDI-SetValue2 (2291h:02h)
        writeData[4:6] = index.to_bytes(2, byteorder="little", signed=signed)

        # Step 3: Set subindex in PDI-SetValue3 (2291h:03h)
        writeData[6] = subindex

        # Step 4: Set OD-Write command in PDI-Cmd (2291h:04h)
        command = self.pdiCmd.get(pdiCmd, self.pdiCmd["OD-Write"])  # Use provided pdiCmd or default OD-Write
        writeData[7] = command if self.toggle else command + 128

        # Send data
        self.eeipClient.output_assembly.iodata = writeData
        time.sleep(0.02)

    def od_read(self, index: int, subindex: int, signed: bool = False) -> int:
        """
        Read data from the Object Dictionary (OD) using the PDI interface.

        Parameters:
        index (int): The index to read from in the object dictionary.
        subindex (int): The subindex to read from in the object dictionary.
        signed (bool): Whether the value should be interpreted as signed. Default is False.

        Returns:
        int: The value read from the object dictionary.

        Notes:
        - Writes the index and subindex to PDI-SetValue2 (2291h:02h) and PDI-SetValue3 (2291h:03h).
        - Sends the OD-Read command using PDI-Cmd (2291h:04h).
        - Uses ToggleCmd to ensure the command is recognized.
        - Introduces a short delay (0.02s) to ensure the response is ready.
        - Retrieves the result from PDI-ReturnValue (2292h:02h).
        """
        self.toggle = not self.toggle
        readData = bytearray(8)

        # Step 1: Set index in PDI-SetValue2 (2291h:02h)
        readData[4:6] = index.to_bytes(2, byteorder="little", signed=signed)

        # Step 2: Set subindex in PDI-SetValue3 (2291h:03h)
        readData[6] = subindex

        # Step 3: Set OD-Read command in PDI-Cmd (2291h:04h)
        command = self.pdiCmd["OD-Read"]
        readData[7] = command if self.toggle else command + 128

        # Send data to initiate the read process
        self.eeipClient.output_assembly.iodata = readData

        # Short delay to ensure the response is ready
        time.sleep(0.02)

        # Retrieve the result from PDI-ReturnValue (2292h:02h)
        response = self.eeipClient.input_assembly.iodata

        return response

    def _write_move_command(
        self,
        pdiCmd: str,
        targetPosition: int = 5000,
        maxSpeed: int = 200,
    ):
        """
        Write a movement command to the motor controller.

        Parameters:
        pdiCmd (str): The PDI command to execute (e.g., "ProfilePosAbs", "ProfilePosRel").
        targetPosition (int): The target position in encoder counts. Default is 5000.
        maxSpeed (int): The maximum speed for the movement. Default is 200.

        Returns:
        None

        Notes:
        - Writes the target position and maximum speed to the motor controller.
        - Uses ToggleCmd to ensure the command is recognized.
        - The position value is written as a signed 32-bit integer.
        - The speed value is written as a signed 16-bit integer.
        - Introduces a short delay (0.02s) after writing to ensure the command is processed.
        """
        self.toggle = not self.toggle
        targetPosition = int(targetPosition)  # Cast the target position as int
        positionData = bytearray(8)  # Initialize the data array
        positionData[0:4] = targetPosition.to_bytes(4, byteorder="little", signed=True)  # Convert pos value to bytes
        positionData[4:6] = maxSpeed.to_bytes(2, byteorder="little", signed=True)  # Convert speed value to bytes
        if self.toggle:
            positionData[7] = self.pdiCmd[pdiCmd]  # Set the PDI command based on the passed-in string
        else:
            positionData[7] = self.pdiCmd[pdiCmd] + 128  # Set the PDI command with ToggleCmd bit

        # Send data to the motor controller
        self.eeipClient.output_assembly.iodata = positionData
        time.sleep(0.02)  # Allow time for the command to be processed

    def gather_pdi_status(self):
        """
        Gather the current PDI status from the input assembly.

        Returns:
        None

        Notes:
        - Retrieves the latest PDI status from the motor controller.
        - Updates the `pdiStatus` attribute with the input assembly data.
        """
        self.pdiStatus = self.eeipClient.input_assembly.iodata

    def check_bit(self, decimalValue: int, bitPosition: int, expectedValue: int) -> bool:
        """
        Check if a specific bit in a decimal value matches the expected value.

        Parameters:
        decimalValue (int): The decimal value representing a byte (0-255).
        bitPosition (int): The bit position to check (0-7).
        expectedValue (int): The expected value of the bit (0 or 1).

        Returns:
        bool: True if the bit matches the expected value, False otherwise.

        Notes:
        - Validates that `decimalValue` is within the range of a byte (0-255).
        - Ensures `bitPosition` is between 0 and 7.
        - Confirms `expectedValue` is either 0 or 1.
        - Uses bitwise shifting to extract and compare the target bit.
        """
        # Validate inputs
        if not (0 <= decimalValue <= 255):
            raise ValueError("decimalValue must be between 0 and 255.")
        if not (0 <= bitPosition <= 7):
            raise ValueError("bitPosition must be between 0 and 7.")
        if expectedValue not in (0, 1):
            raise ValueError("expectedValue must be 0 or 1.")

        # Extract the bit at the specified position
        bitValue = (decimalValue >> bitPosition) & 1

        # Compare the extracted bit with the expected value
        return bitValue == expectedValue

    def monitor_position_reached(self) -> bool:
        """
        Monitor whether the target position has been reached.

        Returns:
        bool: True if the target position is reached, False otherwise.

        Notes:
        - Calls `gather_pdi_status` to update the current PDI status.
        - Checks if the "PdiStatusTargetReached" bit is set in the PDI status.
        - Uses `check_bit` to determine if the target position has been successfully reached.
        """
        self.gather_pdi_status()
        return self.check_bit(
            decimalValue=self.pdiStatus[0],
            bitPosition=self._pdiStatusMapping["PdiStatusTargetReached"],
            expectedValue=1,
        )

    def _filter_data(self, below: bool = True, threshold: int = None, dataSet: list = []) -> list:
        """
        Filter integers out of a list based on a threshold.

        This function is used to clean up ambient values in current monitoring by removing values
        that are either below or above a specified threshold.

        Parameters:
        below (bool): If True, filters out values below the threshold. If False, filters out values above the threshold.
        threshold (int, optional): The threshold value to filter against. If None, no filtering is applied.
        dataSet (list): The list of integer values to be filtered.

        Returns:
        list: A filtered list of values.

        Notes:
        - The threshold is non-inclusive (values equal to the threshold are kept).
        - If `threshold` is None, the original dataset is returned unmodified.
        - Default `dataSet` should not be defined as a mutable list in the function signature (use `None` instead).
        """
        # Avoid mutable default argument issue
        if dataSet is None:
            dataSet = []

        returnList = []
        if threshold is None:
            return dataSet

        if below:
            returnList = [dataPoint for dataPoint in dataSet if dataPoint >= threshold]
        else:
            returnList = [dataPoint for dataPoint in dataSet if dataPoint <= threshold]

        return returnList

    def _modify_bit(self, bitIndex: int, value: int, byteToModify: int) -> int:
        """
        Modify a specific bit in a byte.

        Parameters:
        bitIndex (int): The position of the bit to modify (0-7).
        value (int): The new bit value (0 or 1).
        byteToModify (int): The byte in which the bit should be modified.

        Returns:
        int: The modified byte value.

        Notes:
        - If `value` is 1, the specified bit is set to 1.
        - If `value` is 0, the specified bit is cleared to 0.
        - Uses bitwise operations to modify only the specified bit.
        """
        if value == 1:
            new_value = byteToModify | (1 << bitIndex)  # Set bit to 1
        else:
            new_value = byteToModify & ~(1 << bitIndex)  # Clear bit to 0
        return new_value  # Return the modified decimal value

    def _start_timer(self):
        """
        Start the failure timer to track movement duration.

        Returns:
        None

        Notes:
        - Sets `failureTimer` to the current high-precision time using `time.perf_counter()`.
        - This timer is used in `_timer_is_done()` to determine if a movement operation has exceeded the allowed duration.
        """
        self.failureTimer = time.perf_counter()

    def _timer_is_done(self) -> bool:
        """
        Check if the failure timer has expired.

        Returns:
        bool: True if the timer duration has elapsed, False otherwise.

        Notes:
        - Uses `time.perf_counter()` to measure elapsed time since `failureTimer` was started.
        - Compares the elapsed time against `timerDuration` to determine if the timer has expired.
        - This function is used to enforce movement timeouts in motor operations.
        """
        return (time.perf_counter() - self.failureTimer) > self.timerDuration

    def set_failure_timer_duration(self, duration: float):
        """
        Set the failure timer duration for monitoring motor movement.

        Parameters:
        duration (float): The duration in seconds before a movement operation is considered failed.

        Returns:
        None

        Notes:
        - This value is used by `_start_timer()` and `_timer_is_done()` to track movement timeout conditions.
        """
        self.timerDuration = duration

import time
import socket
from eip.client import EIPBaseClient


class NanotecC5E11ExplicitController:
    def __init__(self, deviceIpAddress: str):
        """
        Explicit EtherNet/IP controller for NanoTec C5-E-11 using Plug & Drive Interface.

        Parameters:
        deviceIpAddress (str): IP address of the motor controller.
        """
        self.deviceIpAddress = deviceIpAddress
        self.eeipClient: EIPBaseClient = EIPBaseClient()
        self.sessionHandle = self.eeipClient.register_session(self.deviceIpAddress)
        self.toggle = False
        self.timerDuration = 5
        self.failureTimer = time.perf_counter()
        self._pdiCmd = {
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

    ##########################
    ## Public Class Methods ##
    ##########################

    ####################
    ## Public Getters ##
    ####################
    def get_od(self, index: int, subindex: int, valueType: str = "UNSIGNED32", decode: bool = True) -> bytes | int:
        """
        Send a GetOD Entry (0x32) request using EIP encapsulation to read a value from the object dictionary.

        Parameters:
        index (int): The 16-bit object dictionary index (e.g., 0x2014).
        subindex (int): The 8-bit subindex within the object (e.g., 0x00).
        valueType (str): The data type to decode the response as. Must be one of:
            'UNSIGNED32', 'UNSIGNED16', 'UNSIGNED8',
            'INTEGER32', 'INTEGER16', 'INTEGER8'. Default is 'UNSIGNED32'.
        decode (bool): If True, the returned response will be decoded to an int based on `valueType`.
                    If False, the raw bytes will be returned as a list.

        Returns:
        bytes | int: The raw or decoded value read from the object dictionary.

        Raises:
        ValueError: If `valueType` is not among the accepted types.
        Exception: If the device response is too short or contains a CIP error.

        Notes:
        - Constructs a Class 0x64 / Instance 0x01 CIP path to access OD entries.
        - Uses a custom `_build_rr_data_packet()` to form the CIP RR data segment.
        - Uses `_build_encapsulation()` to wrap the CIP request in an EIP header.
        - If decode is enabled, `_decode_od_response()` is used to interpret the response bytes.
        - The session handle is registered automatically if not already established.
        """
        if valueType.upper() not in ["UNSIGNED32", "UNSIGNED16", "UNSIGNED8", "INTEGER32", "INTEGER16", "INTEGER8"]:
            raise ValueError("valueType must be one of the following: UNSIGNED32, UNSIGNED16, UNSIGNED8, INTEGER32, INTEGER16, INTEGER8")
        if self.eeipClient.connnection_config.session_handle == 0:
            self.eeipClient.connnection_config.session_handle = self.eeipClient.register_session(
                self.deviceIpAddress, self.eeipClient.tcp_port
            )
        # CIP Path to class 0x64, instance 0x01
        path = bytes([0x20, 0x64, 0x24, 0x01])
        data = index.to_bytes(2, "little") + subindex.to_bytes(1, "little")

        # Build CIP RRData
        rrData = self._build_rr_data_packet(path, data)

        # Build full encapsulation packet
        fullPacket = self._build_encapsulation(rrData)

        self.eeipClient.tcp_client_socket.send(fullPacket)

        # Receive and validate response
        response = self._recv_eip_response()
        if not response or len(response) < 44:
            raise Exception("FAILED: Response too short or missing")

        if len(response) > 42 and response[42] != 0x00:
            raise Exception(f"CIP Error: General Status {response[42]:02X}")
        if decode:
            return self._decode_od_response(response[44:], valueType.upper())
        else:
            return list(response[44:])

    def get_pole_pair(self) -> int:
        """
        Retrieve the pole pair count from the motor controller.

        Returns:
        int: The number of pole pairs configured in the motor.

        Notes:
        - Reads from object dictionary index `0x2030`, subindex `0x00`.
        - Internally uses `get_od()` to retrieve and decode the value.
        - This setting is essential for accurate motor control and should match the motor's physical configuration.
        """
        return self.get_od(index=0x2030, subindex=0x00)

    def get_is_open_loop(self) -> bool:
        """
        Determine if the motor controller is operating in open-loop mode.

        Returns:
        bool: True if open-loop mode is active, False if in closed-loop mode.

        Notes:
        - Reads from object dictionary index `0x3202`, subindex `0x00` using `get_od()` with `decode=False` to access raw bytes.
        - Checks bit 0 of the response to determine the loop mode.
        - Uses `_check_bit()` to verify if the bit matches the expected value of 0 (open-loop).
        - This setting is important for applications that depend on feedback control.
        """
        status = self.get_od(index=0x3202, subindex=0x00, decode=False)
        return self._check_bit(status[0], 0, 0)

    def get_is_closed_loop(self) -> bool:
        """
        Determine if the motor controller is operating in closed-loop mode.

        Returns:
        bool: True if closed-loop mode is active, False otherwise.

        Notes:
        - Reads from object dictionary index `0x3202`, subindex `0x00` using `get_od()` with `decode=False` to retrieve raw bytes.
        - Uses `_check_bit()` to check if bit 0 is set to 1, indicating closed-loop mode.
        - Closed-loop mode enables feedback control and higher precision operation.
        """
        status = self.get_od(index=0x3202, subindex=0x00, decode=False)
        return self._check_bit(status[0], 0, 1)

    def get_current_reduction_settings(self) -> dict:
        """
        Retrieve the current reduction configuration from the motor controller.

        Returns:
        dict: A dictionary containing:
            - "Current Reduction Enabled" (bool): Whether current reduction is enabled.
            - "Idle Timeout" (int): The idle time (in ms) before current reduction activates.
            - "Reduction Percent" (int): The percentage of current reduction applied when idle.

        Notes:
        - Reads the idle timeout from index `0x2036`, subindex `0x00` as UNSIGNED32.
        - Reads the reduction percentage from index `0x2037`, subindex `0x00` as INTEGER32.
        - Reads the motor drive mode from index `0x3202`, subindex `0x00` as raw bytes.
        - Uses `_check_bit()` on bit 3 to determine whether current reduction is enabled.
        - Provides a comprehensive snapshot of the current reduction configuration for diagnostics or tuning.
        """
        idleTime = self.get_od(index=0x2036, subindex=0x00, valueType="unsigned32")
        reductionValue = self.get_od(index=0x2037, subindex=0x00, valueType="integer32")
        motorDriveMode = self.get_od(index=0x3202, subindex=0x00, valueType="unsigned32", decode=False)
        enabled = self._check_bit(motorDriveMode[0], 3, 1)

        return {"Current Reduction Enabled": enabled, "Idle Timeout": idleTime, "Reduction Percent": reductionValue}

    def get_analog_config(self):
        """
        Retrieve the configuration parameters for Analog Input 1 and Analog Input 2.

        Returns:
        dict: A dictionary containing:
            - "Analog 1 Offset" (int): Offset for Analog Input 1.
            - "Analog 1 Upper Limit" (int): Maximum current in microamps for Analog Input 1.
            - "Analog 1 ADC Resolution" (int): ADC resolution for Analog Input 1.
            - "Analog 2 Offset" (int): Offset for Analog Input 2.
            - "Analog 2 Upper Limit" (int): Maximum current in microamps for Analog Input 2.
            - "Analog 2 ADC Resolution" (int): ADC resolution for Analog Input 2.

        Notes:
        - Reads configuration values using the `get_od()` method from the following OD indexes:
            - 0x3321: Offset
            - 0x3322: Upper current limit in µA
            - 0x3323: ADC resolution
        - Subindex `0x01` is used for Analog Input 1, and `0x02` for Analog Input 2.
        - All values are read as 16-bit signed integers.
        """
        # Read Offset for Analog Input 1
        a1Offset = self.get_od(index=0x3321, subindex=0x01, valueType="integer16")
        # Read upper limit current in microamps
        a1UpperLimit = self.get_od(index=0x3322, subindex=0x01, valueType="integer16")
        # Read ADC resolution value
        a1Resolution = self.get_od(index=0x3323, subindex=0x01, valueType="integer16")
        # Read Offset for Analog Input 2
        a2Offset = self.get_od(index=0x3321, subindex=0x02, valueType="integer16")
        # Read upper limit current in microamps
        a2UpperLimit = self.get_od(index=0x3322, subindex=0x02, valueType="integer16")
        # Read ADC resolution value
        a2Resolution = self.get_od(index=0x3323, subindex=0x02, valueType="integer16")
        return {
            "Analog 1 Offset": a1Offset,
            "Analog 1 Upper Limit": a1UpperLimit,
            "Analog 1 ADC Resolution": a1Resolution,
            "Analog 2 Offset": a2Offset,
            "Analog 2 Upper Limit": a2UpperLimit,
            "Analog 2 ADC Resolution": a2Resolution,
        }

    def get_analog_1_mode(self) -> str:
        """
        Determine the operating mode of Analog Input 1.

        Returns:
        str: "current" if Analog Input 1 is configured for current mode, "voltage" if configured for voltage mode.

        Notes:
        - Reads from object dictionary index `0x3221`, subindex `0x00` as a 32-bit integer (decoded as raw bytes).
        - Uses `_check_bit()` to inspect bit 0 of the response:
            - Bit 0 = 1 → current mode.
            - Bit 0 = 0 → voltage mode.
        - This mode defines how the analog input signal is interpreted by the controller.
        """
        status = self.get_od(index=0x3221, subindex=0x00, valueType="integer32", decode=False)
        isCurrent = self._check_bit(status[0], 0, 1)
        return "current" if isCurrent else "voltage"

    def get_analog_2_mode(self) -> str:
        """
        Determine the operating mode of Analog Input 2.

        Returns:
        str: "current" if Analog Input 2 is configured for current mode, "voltage" if configured for voltage mode.

        Notes:
        - Reads from object dictionary index `0x3221`, subindex `0x00` as a 32-bit integer (decoded as raw bytes).
        - Uses `_check_bit()` to inspect bit 1 of the response:
            - Bit 1 = 1 → current mode.
            - Bit 1 = 0 → voltage mode.
        - This mode defines how the analog input signal is interpreted by the controller for Analog Input 2.
        """
        status = self.get_od(index=0x3221, subindex=0x00, valueType="integer32", decode=False)
        isCurrent = self._check_bit(status[0], 1, 1)
        return "current" if isCurrent else "voltage"

    def get_analog_1_input(self):
        """
        Read the current value from Analog Input 1.

        Returns:
        int: The signed 32-bit value read from Analog Input 1, typically in microamps or millivolts depending on mode.

        Notes:
        - Reads from object dictionary index `0x3320`, subindex `0x01`.
        - Uses `get_od()` with `valueType="integer32"` to decode the result.
        - The interpretation of this value depends on the configured analog input mode (current or voltage).
        """
        return self.get_od(index=0x3320, subindex=0x01, valueType="integer32")

    def get_analog_2_input(self):
        """
        Read the current value from Analog Input 2.

        Returns:
        int: The signed 32-bit value read from Analog Input 2, typically in microamps or millivolts depending on mode.

        Notes:
        - Reads from object dictionary index `0x3320`, subindex `0x02`.
        - Uses `get_od()` with `valueType="integer32"` to decode the result.
        - The interpretation of this value depends on the configured analog input mode (current or voltage).
        """
        return self.get_od(index=0x3320, subindex=0x02, valueType="integer32")

    def get_digital_output(self, outputIndex: int) -> bool:
        """
        Read the state of a digital output line.

        Parameters:
        outputIndex (int): The digital output index to read (valid range: 1–5).

        Returns:
        bool: True if the specified digital output is active (set to 1), False otherwise.

        Raises:
        ValueError: If the `outputIndex` is not between 1 and 5.

        Notes:
        - Reads from object dictionary index `0x60FE`, subindex `0x01` as a 32-bit unsigned integer.
        - Uses `_check_bit()` to inspect the bit corresponding to `outputIndex - 1` within the third byte of the response.
        - Digital outputs are zero-indexed internally but exposed as 1-based for clarity.
        """
        if outputIndex not in [1, 2, 3, 4, 5]:
            raise ValueError("outputIndex must be between 1 and 5")
        status = self.get_od(index=0x60FE, subindex=0x01, valueType="unsigned32", decode=False)
        return self._check_bit(decimalValue=status[2], bitPosition=outputIndex - 1, expectedValue=1)

    def get_torque_forming_current(self):
        """
        Read the torque-forming current from the motor controller.

        Returns:
        int: The torque-forming current in milliamps (mA).

        Notes:
        - Reads from object dictionary index `0x2039`, subindex `0x02`.
        - Uses `get_od()` with `valueType="integer32"` to decode the signed 32-bit result.
        - This current directly contributes to generating torque in the motor.
        - The value increases when more torque is needed, such as under load or resistance.
        """
        return self.get_od(index=0x2039, subindex=0x02, valueType="integer32", decode=True)

    def get_max_voltage(self):
        """
        Read the maximum allowed motor voltage from the controller.

        Returns:
        int: The maximum motor voltage in millivolts (mV).

        Notes:
        - Reads from object dictionary index `0x321E`, subindex `0x00`.
        - Uses `get_od()` with `valueType="unsigned32"` to decode the 32-bit unsigned result.
        - This value represents the upper voltage limit configured for motor protection.
        - It helps prevent overvoltage conditions that could damage the motor or drive circuitry.
        """
        return self.get_od(index=0x321E, subindex=0x00, valueType="unsigned32", decode=True)

    def get_max_current(self):
        """
        Read the maximum allowed motor current from the controller.

        Returns:
        int: The maximum motor current in milliamps (mA).

        Notes:
        - Reads from object dictionary index `0x2031`, subindex `0x00`.
        - Uses `get_od()` with `valueType="unsigned32"` to decode the 32-bit unsigned result.
        - This value defines the upper limit of current the motor is allowed to draw.
        - It helps protect the motor and drive hardware from overcurrent damage.
        """
        return self.get_od(index=0x2031, subindex=0x00, valueType="unsigned32", decode=True)

    def get_accleration(self):
        """
        Read the configured acceleration value from the motor controller.

        Returns:
        int: The acceleration value in units defined by the drive (RPM/s).

        Notes:
        - Reads from object dictionary index `0x6083`, subindex `0x00`.
        - Uses `get_od()` with `valueType="unsigned32"` to decode the 32-bit unsigned result.
        - This value determines how quickly the motor accelerates to its target speed.
        - It should be set considering mechanical constraints and load requirements.
        """
        return self.get_od(index=0x6083, subindex=0x00, valueType="unsigned32", decode=True)

    def get_deceleration(self):
        """
        Read the configured deceleration value from the motor controller.

        Returns:
        int: The deceleration value in units defined by the drive (RPM/s).

        Notes:
        - Reads from object dictionary index `0x6084`, subindex `0x00`.
        - Uses `get_od()` with `valueType="unsigned32"` to decode the 32-bit unsigned result.
        - This value determines how quickly the motor slows down to a stop.
        - Proper tuning helps prevent overshoot and ensures smooth braking behavior.
        """
        return self.get_od(index=0x6084, subindex=0x00, valueType="unsigned32", decode=True)

    ####################
    ## Public Setters ##
    ####################
    def set_od(self, index: int, subindex: int, value: int, valueType: str = "UNSIGNED32") -> bool:
        """
        Write a value to the object dictionary (OD) using a SetOD Entry (0x33) EtherNet/IP encapsulated request.

        Parameters:
        index (int): The 16-bit object dictionary index (e.g., 0x2031).
        subindex (int): The 8-bit subindex within the object (e.g., 0x00).
        value (int): The value to write to the specified OD entry.
        valueType (str): The data type of the value to write. Supported types:
            "UNSIGNED32", "UNSIGNED16", "UNSIGNED8",
            "INTEGER32", "INTEGER16", "INTEGER8",
            "COMMAND" (raw byte).

        Returns:
        bool: True if the write operation was successful, otherwise an exception is raised.

        Notes:
        - Automatically registers a session if one has not been established.
        - Constructs a CIP path targeting Class 0x64, Instance 0x01.
        - Encodes the value according to the specified `valueType` using little-endian byte order.
        - Builds the CIP SetOD RRData payload and wraps it in an EtherNet/IP encapsulation header.
        - Sends the encapsulated request via TCP and checks for a valid response.
        - If the General Status byte in the response (offset 42) is non-zero, an exception is raised.
        """
        if self.eeipClient.connnection_config.session_handle == 0:
            self.eeipClient.connnection_config.session_handle = self.eeipClient.register_session(
                self.deviceIpAddress, self.eeipClient.tcp_port
            )

        # Build the CIP path
        path = bytes([0x20, 0x64, 0x24, 0x01])
        pathSize = len(path) // 2

        # Convert the value to bytes depending on type
        valueType = valueType.upper()
        if valueType.upper() == "UNSIGNED32":
            valueBytes = value.to_bytes(4, "little", signed=False)
        elif valueType.upper() == "INTEGER32":
            valueBytes = value.to_bytes(4, "little", signed=True)
        elif valueType.upper() == "UNSIGNED16":
            valueBytes = value.to_bytes(2, "little", signed=False)
        elif valueType.upper() == "INTEGER16":
            valueBytes = value.to_bytes(2, "little", signed=True)
        elif valueType.upper() == "UNSIGNED8":
            valueBytes = value.to_bytes(1, "little", signed=False)
        elif valueType.upper() == "INTEGER8":
            valueBytes = value.to_bytes(1, "little", signed=True)
        elif valueType.upper() == "COMMAND":
            valueBytes = value
        else:
            raise ValueError(f"Unsupported value type: {valueType}")
        # Build SetOD RRData
        rrData = bytearray()
        rrData.append(0x33)  # Service: SetOD Entry
        rrData.append(pathSize)  # Path size
        rrData.extend(path)  # Path
        rrData.extend(index.to_bytes(2, "little"))
        rrData.extend(subindex.to_bytes(1, "little"))
        if valueType.upper() == "COMMAND":
            rrData.append(valueBytes)
        else:
            rrData.extend(valueBytes)  # Actual value to write

        # Build and send encapsulation
        packet = self._build_encapsulation(rrData)
        self.eeipClient.tcp_client_socket.send(packet)

        # Receive and check response
        response = self._recv_eip_response()
        if not response or len(response) < 44:
            raise Exception("FAILED: Response too short or missing")
        if response[42] != 0x00:
            raise Exception(f"SetOD failed, General Status = {response[42]:02X}")
        return True

    def set_move(
        self,
        moveType: str = "relative",
        targetPosition: int = 5000,
        maxSpeed: int = 200,
        bypassError: bool = False,
    ):
        """
        Issue a motion command to the motor controller using either relative or absolute positioning.

        Parameters:
        moveType (str): Type of move to perform. Must be "relative" or "absolute". Default is "relative".
        targetPosition (int): The position to move to, in encoder counts. Default is 5000.
        maxSpeed (int): Maximum movement speed. Default is 200.
        bypassError (bool): If True, do not raise an error on timeout. Default is False.

        Returns:
        bool: True if the motion command was issued and either completed or bypassed the error timeout.

        Notes:
        - Calls `_set_relative_move()` or `_set_absolute_move()` depending on `moveType`.
        - Starts a timer immediately after sending the command to track execution duration.
        - Waits in a loop for `_get_target_reached()` to return True or for timeout.
        - If `bypassError` is False and the timeout expires, raises a `RuntimeError`.
        - Uses a short delay (5 ms) to ensure the controller registers the motion command.
        """
        if moveType.lower() not in ["relative", "absolute"]:
            raise ValueError("moveType must be 'relative' or 'absolute'")
        if moveType.lower() == "relative":
            self._set_relative_move(targetPosition=targetPosition, maxSpeed=maxSpeed)
        else:
            self._set_absolute_move(targetPosition=targetPosition, maxSpeed=maxSpeed)
        self._start_timer()
        time.sleep(0.005)  # Minimum found time to have controller register commands
        while not self._get_target_reached():
            time.sleep(0.001)
            if bypassError:
                if self._timer_is_done():
                    break
                else:
                    if self._timer_is_done():
                        raise RuntimeError(f"Motor failed to reach position in {self.timerDuration} seconds")
        return True

    def set_move_torque_current_avg(
        self,
        moveType: str = "relative",
        targetPosition: int = 5000,
        maxSpeed: int = 200,
        filterBelow: int = None,
        bypassError: bool = False,
    ):
        """
        Perform a motor move and calculate the average torque-forming current during motion.

        Parameters:
        moveType (str): Type of move to perform. Must be "relative" or "absolute". Default is "relative".
        targetPosition (int): The target position in encoder counts. Default is 5000.
        maxSpeed (int): Maximum movement speed. Default is 200.
        filterBelow (int): Filter out current values below this threshold before averaging. Default is None.
        bypassError (bool): If True, bypass runtime error if the target is not reached in time. Default is False.

        Returns:
        dict: A dictionary with the following keys:
            - "average" (int): The rounded average of filtered torque-forming current values.
            - "data" (list): The list of filtered torque current readings collected during motion.

        Notes:
        - Calls `_set_relative_move()` or `_set_absolute_move()` based on `moveType`.
        - Monitors `_get_target_reached()` and collects torque current readings during movement.
        - Inverts current values for positive-direction moves to normalize signs.
        - Applies `_filter_data()` if a `filterBelow` threshold is provided.
        - Returns 0 as average if no data remains after filtering.
        - Raises a `RuntimeError` on timeout unless `bypassError` is True.
        """
        currentData = []
        isNegative = True if targetPosition > 0 else False
        if moveType.lower() not in ["relative", "absolute"]:
            raise ValueError("moveType must be 'relative' or 'absolute'")
        if moveType.lower() == "relative":
            self._set_relative_move(targetPosition=targetPosition, maxSpeed=maxSpeed)
        else:
            self._set_absolute_move(targetPosition=targetPosition, maxSpeed=maxSpeed)
        self._start_timer()
        time.sleep(0.005)  # Minimum found time to have controller register commands
        while not self._get_target_reached():
            # Capture torque current values, adjusting for negative moves
            if isNegative:
                currentData.append(-1 * (self.get_torque_forming_current()))
            else:
                currentData.append(self.get_torque_forming_current())
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

    def set_pole_pair(self, stepAngle: float = 1.8):
        """
        Set the pole pair count based on the motor's step angle.

        Parameters:
        stepAngle (float): The motor's step angle in degrees. Valid values are 1.8 or 0.9. Default is 1.8.

        Returns:
        bool: True if the pole pair value was successfully written to the object dictionary.

        Raises:
        ValueError: If an unsupported step angle is provided.

        Notes:
        - Writes to object dictionary index `0x2030`, subindex `0x00`.
        - For a step angle of 1.8°, sets the pole pair count to 50.
        - For a step angle of 0.9°, sets the pole pair count to 100.
        - This setting must match the physical characteristics of the motor.
        """
        if stepAngle in [1.8]:
            return self.set_od(index=0x2030, subindex=0x00, value=50)
        elif stepAngle in [0.9]:
            return self.set_od(index=0x2030, subindex=0x00, value=100)
        else:
            raise ValueError(f"Step Angle {stepAngle} is not a valid value")

    def set_open_loop(self):
        """
        Configure the motor controller to operate in open-loop mode.

        Returns:
        bool: True if the controller is already in open-loop mode or successfully switched.

        Notes:
        - Reads from object dictionary index `0x3202`, subindex `0x00` to get the current motor mode state.
        - Checks bit 0 to determine if open-loop mode is already active.
        - If not active, modifies bit 0 to 0 using `_modify_bit()` to enable open-loop mode.
        - Writes the modified value back using `set_od()` with `valueType="unsigned32"`.
        - Open-loop mode disables feedback-based control, which may reduce accuracy but can simplify operation.
        """
        status = self.get_od(index=0x3202, subindex=0x00, decode=False)
        if self.get_is_open_loop():
            return True
        else:
            status[0] = self._modify_bit(bitIndex=0, value=0, byteToModify=status[0])
            modifiedValue = int.from_bytes(status, byteorder="little", signed=False)
            self.set_od(index=0x3202, subindex=0x00, value=modifiedValue, valueType="unsigned32")
            return True

    def set_closed_loop(self):
        """
        Configure the motor controller to operate in closed-loop mode.

        Returns:
        bool: True if the controller is already in closed-loop mode or successfully switched.

        Notes:
        - Reads from object dictionary index `0x3202`, subindex `0x00` to get the current motor mode state.
        - Checks bit 0 to determine if closed-loop mode is already active.
        - If not active, modifies bit 0 to 1 using `_modify_bit()` to enable closed-loop mode.
        - Writes the modified value back using `set_od()` with `valueType="unsigned32"`.
        - Closed-loop mode enables feedback control for precise and adaptive motor performance.
        """
        status = self.get_od(index=0x3202, subindex=0x00, decode=False)
        if self.get_is_closed_loop():
            return True
        else:
            status[0] = self._modify_bit(bitIndex=0, value=1, byteToModify=status[0])
            modifiedValue = int.from_bytes(status, byteorder="little", signed=False)
            self.set_od(index=0x3202, subindex=0x00, value=modifiedValue, valueType="unsigned32")
            return True

    def set_enable_current_reduction(self, idleTimeout: int = 500, currReductionPercent: int = 90):
        """
        Enable automatic current reduction when the motor is idle.

        Parameters:
        idleTimeout (int): Idle time in milliseconds before current reduction activates. Default is 500 ms.
        currReductionPercent (int): Current reduction percentage (0–100). Default is 90.

        Returns:
        bool: True if the configuration was successfully applied.

        Raises:
        ValueError: If `currReductionPercent` is not in the range 0 to 100.

        Notes:
        - Automatically converts the current reduction percent to a negative signed integer (required by the controller).
        - Ensures the controller is in open-loop mode, as current reduction is only supported in that mode.
        - Enables current reduction by setting bit 3 of the motor drive mode (index `0x3202`).
        - Configures:
            - `0x2036:00` → Idle timeout (UNSIGNED32)
            - `0x2037:00` → Current reduction value (INTEGER32)
        - Uses `_modify_bit()` to safely enable the relevant control bit.
        """
        if currReductionPercent > 100 or currReductionPercent < 0:
            raise ValueError(f"currRedPercent must be between 0 and 100, given value: {currReductionPercent}")
        else:
            currReductionPercent = -abs(currReductionPercent)
        if not self.get_is_open_loop():
            self.set_open_loop()
        motorDriveModeStatus = self.get_od(index=0x3202, subindex=0x00, valueType="unsigned32", decode=False)
        motorDriveModeStatus[0] = self._modify_bit(bitIndex=3, value=1, byteToModify=motorDriveModeStatus[0])
        modifiedValue = int.from_bytes(motorDriveModeStatus, byteorder="little", signed=False)
        self.set_od(index=0x3202, subindex=0x00, value=modifiedValue, valueType="unsigned32")
        self.set_od(index=0x2036, subindex=0x00, value=idleTimeout, valueType="unsigned32")
        self.set_od(index=0x2037, subindex=0x00, value=currReductionPercent, valueType="integer32")
        return True

    def set_disable_current_reduction(self):
        """
        Disable the automatic current reduction feature on the motor controller.

        Returns:
        bool: True if the current reduction feature was successfully disabled.

        Notes:
        - Reads from object dictionary index `0x3202`, subindex `0x00` to access the motor drive mode settings.
        - Clears bit 3 to disable current reduction using `_modify_bit()`.
        - Writes the updated value back to the same OD entry with `valueType="unsigned32"`.
        - This prevents the controller from lowering current after an idle timeout, ensuring full torque is always available.
        """
        motorDriveModeStatus = self.get_od(index=0x3202, subindex=0x00, valueType="unsigned32", decode=False)
        motorDriveModeStatus[0] = self._modify_bit(bitIndex=3, value=0, byteToModify=motorDriveModeStatus[0])
        modifiedValue = int.from_bytes(motorDriveModeStatus, byteorder="little", signed=False)
        self.set_od(index=0x3202, subindex=0x00, value=modifiedValue, valueType="unsigned32")
        return True

    def set_auto_setup(self):
        """
        Initiate the auto setup routine on the motor controller.

        Returns:
        bool: True if auto setup was already complete or successfully executed.

        Notes:
        - Checks whether auto setup is already completed using `_get_auto_setup_complete()`.
        - If not completed, it:
            - Writes `0` to `0x2291:01` (PDI SetValue1) as a placeholder.
            - Writes `0` to `0x2291:02` (PDI SetValue2) as a placeholder.
            - Sends the "Auto Setup" command by writing the appropriate PDI command to `0x2291:04`.
        - Waits in a loop until `_get_auto_setup_complete()` returns True, indicating the process is done.
        - `time.sleep(0.005)` is added after issuing the command to allow the controller to register the change.
        """
        if self._get_auto_setup_complete():
            return True
        else:
            self.set_od(0x2291, 0x01, 0, "integer32")
            self.set_od(0x2291, 0x02, 0, "integer16")
            self.set_od(0x2291, 0x04, self._pdiCmd["Auto Setup"], "command")
            time.sleep(0.005)
            while not self._get_auto_setup_complete():
                time.sleep(0.001)
            return True

    def set_analog_config(self):
        """
        Configure the analog input channels (Analog 1 and Analog 2) for current measurement mode.

        Returns:
        None

        Notes:
        - Writes the following configuration for both analog inputs:
            - Offset: `0` (index `0x3321`)
            - Upper limit current: `20000` µA (index `0x3322`)
            - ADC resolution: `1023` (index `0x3323`)
        - Analog Input 1 is configured using subindex `0x01`, and Analog Input 2 with subindex `0x02`.
        - Uses signed 16-bit values (`valueType="integer16"`) for all parameters.
        - This configuration is typically used for 4–20 mA current loops or other current-driven sensors.
        """
        # Write Offset for Analog Input 1
        self.set_od(index=0x3321, subindex=0x01, value=0, valueType="integer16")
        # Write upper limit current in microamps
        self.set_od(index=0x3322, subindex=0x01, value=20000, valueType="integer16")
        # Write ADC resolution value
        self.set_od(index=0x3323, subindex=0x01, value=1023, valueType="integer16")
        # Write Offset for Analog Input 2
        self.set_od(index=0x3321, subindex=0x02, value=0, valueType="integer16")
        # Write upper limit current in microamps
        self.set_od(index=0x3322, subindex=0x02, value=20000, valueType="integer16")
        # Write ADC resolution value
        self.set_od(index=0x3323, subindex=0x02, value=1023, valueType="integer16")

    def set_analog_1_mode(self, mode: str = "current") -> True:
        """
        Set the input mode for Analog Input 1 to either "current" or "voltage".

        Parameters:
        mode (str): The desired mode for Analog Input 1. Must be either "current" or "voltage". Default is "current".

        Returns:
        bool: True if the mode was successfully set.

        Raises:
        ValueError: If the input `mode` is not "current" or "voltage".

        Notes:
        - The configuration of Analog Input 1 depends on the current mode of Analog Input 2.
        - The combined mode of Analog 1 and Analog 2 is encoded into a single integer value written to index `0x3221`, subindex `0x00`:
            - Voltage/Voltage → 0
            - Current/Voltage → 1
            - Voltage/Current → 2
            - Current/Current → 3
        - Uses `get_analog_2_mode()` to preserve the current mode of Analog Input 2.
        """
        if mode.lower() not in ["current", "voltage"]:
            raise ValueError("Mode must be 'current' or 'voltage'")
        analog2Mode = self.get_analog_2_mode()
        if mode.lower() == "current" and analog2Mode.lower() == "current":
            setValue = 3
        elif mode.lower() == "voltage" and analog2Mode.lower() == "current":
            setValue = 2
        elif mode.lower() == "current" and analog2Mode.lower() == "voltage":
            setValue = 1
        elif mode.lower() == "voltage" and analog2Mode.lower() == "voltage":
            setValue = 0
        self.set_od(index=0x3221, subindex=0x00, value=setValue, valueType="integer32")

    def set_analog_2_mode(self, mode: str = "current") -> True:
        """
        Set the input mode for Analog Input 2 to either "current" or "voltage".

        Parameters:
        mode (str): The desired mode for Analog Input 2. Must be either "current" or "voltage". Default is "current".

        Returns:
        bool: True if the mode was successfully set.

        Raises:
        ValueError: If the input `mode` is not "current" or "voltage".

        Notes:
        - The configuration of Analog Input 2 depends on the current mode of Analog Input 1.
        - The combined mode of Analog 1 and Analog 2 is encoded into a single integer value written to index `0x3221`, subindex `0x00`:
            - Voltage/Voltage → 0
            - Voltage/Current → 1
            - Current/Voltage → 2
            - Current/Current → 3
        - Uses `get_analog_1_mode()` to preserve the current mode of Analog Input 1.
        """
        if mode.lower() not in ["current", "voltage"]:
            raise ValueError("Mode must be 'current' or 'voltage'")
        analog1Mode = self.get_analog_1_mode()
        if mode.lower() == "current" and analog1Mode.lower() == "current":
            setValue = 3
        elif mode.lower() == "voltage" and analog1Mode.lower() == "current":
            setValue = 1
        elif mode.lower() == "current" and analog1Mode.lower() == "voltage":
            setValue = 2
        elif mode.lower() == "voltage" and analog1Mode.lower() == "voltage":
            setValue = 0
        self.set_od(index=0x3221, subindex=0x00, value=setValue, valueType="integer32")

    def set_digital_output(self, outputIndex: int, outputValue: int):
        """
        Set the state of a digital output line on the motor controller.

        Parameters:
        outputIndex (int): The output channel to modify (valid range: 1–5).
        outputValue (int): The desired output state; 0 for low (off), 1 for high (on).

        Returns:
        None

        Raises:
        ValueError: If `outputIndex` is not in the range 1–5.
        ValueError: If `outputValue` is not 0 or 1.

        Notes:
        - Reads the current digital output status from object dictionary index `0x60FE`, subindex `0x01`.
        - Modifies the bit corresponding to `outputIndex - 1` using `_modify_bit()` to set or clear the output.
        - Re-encodes the modified byte array back to a 32-bit unsigned integer.
        - Writes the updated value back to the same OD location using `set_od()`.
        - Digital outputs can be used to control external relays, actuators, or status indicators.
        """
        if outputIndex not in [1, 2, 3, 4, 5]:
            raise ValueError("outputIndex must be between 1 and 5")
        if outputValue not in [0, 1]:
            raise ValueError("outputValue must be 0 or 1")
        status = self.get_od(index=0x60FE, subindex=0x01, valueType="unsigned32", decode=False)
        status[2] = self._modify_bit(outputIndex - 1, outputValue, status[2])
        status = int.from_bytes(status, byteorder="little", signed=False)
        self.set_od(index=0x60FE, subindex=0x01, value=status, valueType="unsigned32")

    def set_max_voltage(self, voltageValue: int = 4000):
        """
        Set the maximum motor voltage allowed by the controller.

        Parameters:
        voltageValue (int): The voltage limit in millivolts (mV). Default is 4000.

        Returns:
        None

        Notes:
        - Writes the value to object dictionary index `0x321E`, subindex `0x00`.
        - The value must reflect the voltage rating of the motor and the application's requirements.
        - Exceeding the motor's rated voltage may result in overheating or permanent damage.
        - Uses `valueType="unsigned32"` to encode the 32-bit value.
        """
        self.set_od(index=0x321E, subindex=0x00, value=voltageValue, valueType="unsigned32")

    def set_max_current(self, currentValue: int = 2000):
        """
        Set the maximum motor current allowed by the controller.

        Parameters:
        currentValue (int): The current limit in milliamps (mA). Default is 2000.

        Returns:
        None

        Notes:
        - Writes to object dictionary index `0x2031`, subindex `0x00`.
        - Uses `valueType="unsigned32"` to encode the 32-bit value.
        - This limit protects the motor and controller from overcurrent damage.
        - Ensure the value is within the safe operating range for your motor.
        """
        self.set_od(index=0x2031, subindex=0x00, value=currentValue, valueType="unsigned32")

    def set_acceleration(self, accelValue: int = 2000):
        """
        Set the acceleration rate for motor motion profiles.

        Parameters:
        accelValue (int): The acceleration value in units defined by the drive (e.g., steps/s² or RPM/s). Default is 2000.

        Returns:
        None

        Notes:
        - Writes to object dictionary index `0x6083`, subindex `0x00`.
        - Uses `valueType="unsigned32"` to encode the 32-bit value.
        - This setting controls how quickly the motor ramps up to its target speed.
        - Set according to your system's mechanical tolerances and desired responsiveness.
        """
        self.set_od(index=0x6083, subindex=0x00, value=accelValue, valueType="unsigned32")

    def set_deceleration(self, decelValue: int = 2000):
        """
        Set the deceleration rate for motor motion profiles.

        Parameters:
        decelValue (int): The deceleration value in units defined by the drive (e.g., steps/s² or RPM/s). Default is 2000.

        Returns:
        None

        Notes:
        - Writes to object dictionary index `0x6084`, subindex `0x00`.
        - Uses `valueType="unsigned32"` to encode the 32-bit value.
        - This setting controls how quickly the motor slows down to a stop.
        - Proper tuning can prevent mechanical stress and overshooting in motion applications.
        """
        self.set_od(index=0x6084, subindex=0x00, value=decelValue, valueType="unsigned32")

    ###########################
    ## Private Class Methods ##
    ###########################

    #####################
    ## Private Getters ##
    #####################
    def _get_auto_setup_complete(self):
        """
        Check if the auto setup routine has completed successfully.

        Returns:
        bool: True if the auto setup completion bit is set, False otherwise.

        Notes:
        - Reads from object dictionary index `0x2292`, subindex `0x01` to obtain the PDI status response.
        - Uses the second byte of the response (`result[1]`) to inspect status bits 8–15.
        - Checks the bit associated with `"PdiStatusAutosetupDone"` from `_pdiStatusMapping`.
        - Uses `_check_bit()` to determine if the relevant status bit is set to 1.
        - Typically used to verify that `set_auto_setup()` has finished before proceeding.
        """
        result = self.get_od(index=0x2292, subindex=0x01, valueType="integer16", decode=False)
        secondByte = result[1]  # Entries 8-15
        return self._check_bit(secondByte, self._pdiStatusMapping["PdiStatusAutosetupDone"], 1)

    def _get_target_reached(self):
        """
        Check if the motor has reached its target position.

        Returns:
        bool: True if the target reached bit is set, False otherwise.

        Notes:
        - Reads from object dictionary index `0x2292`, subindex `0x01` to obtain the PDI status response.
        - Inspects the first byte of the response (`result[0]`), which contains status bits 0–7.
        - Uses `_check_bit()` to verify if the `"PdiStatusTargetReached"` bit is set.
        - This status bit indicates that the motor has reached the commanded position within the configured tolerance.
        """
        result = self.get_od(index=0x2292, subindex=0x01, valueType="integer16", decode=False)
        firstByte = result[0]  # Entries 0-7
        return self._check_bit(firstByte, self._pdiStatusMapping["PdiStatusTargetReached"], 1)

    #####################s
    ## Private Setters ##
    #####################
    def _set_relative_move(self, targetPosition: int = 5000, maxSpeed: int = 200):
        """
        Issue a relative motion command to move the motor by a specified number of steps.

        Parameters:
        targetPosition (int): The relative position (in encoder counts) to move from the current position. Default is 5000.
        maxSpeed (int): The maximum speed for the move. Default is 200.

        Returns:
        None

        Notes:
        - Writes `targetPosition` to `0x2291:01` (PDI SetValue1) as a signed 32-bit value.
        - Writes `maxSpeed` to `0x2291:02` (PDI SetValue2) as a signed 16-bit value.
        - Sends the "Profile Position Relative" command (code 21) via `0x2291:04` (PDI-Cmd).
        - Alternates the toggle bit (adds 128) each time to ensure the controller processes sequential commands.
        - This function supports incremental movement based on the motor’s current position.
        """
        targetPosition = int(targetPosition)  # Cast the target position as int
        maxSpeed = int(maxSpeed)
        self.set_od(0x2291, 0x01, targetPosition, "integer32")
        self.set_od(0x2291, 0x02, maxSpeed, "integer16")
        if self.toggle:
            self.set_od(0x2291, 0x04, self._pdiCmd["ProfilePosRel"] + 128, "command")
            self.toggle = not self.toggle
        else:
            self.set_od(0x2291, 0x04, self._pdiCmd["ProfilePosRel"], "command")
            self.toggle = not self.toggle

    def _set_absolute_move(self, targetPosition: int = 5000, maxSpeed: int = 200):
        """
        Issue an absolute motion command to move the motor to a specific target position.

        Parameters:
        targetPosition (int): The absolute position (in encoder counts) to move to. Default is 5000.
        maxSpeed (int): The maximum speed for the move. Default is 200.

        Returns:
        None

        Notes:
        - Writes `targetPosition` to `0x2291:01` (PDI SetValue1) as a signed 32-bit value.
        - Writes `maxSpeed` to `0x2291:02` (PDI SetValue2) as a signed 16-bit value.
        - Sends the "Profile Position Absolute" command (code 20) via `0x2291:04` (PDI-Cmd).
        - Alternates the toggle bit (adds 128) each time to ensure the controller accepts sequential commands.
        - Absolute positioning targets a specific point on the encoder scale, regardless of current position.
        """
        targetPosition = int(targetPosition)  # Cast the target position as int
        maxSpeed = int(maxSpeed)
        self.set_od(0x2291, 0x01, targetPosition, "integer32")
        self.set_od(0x2291, 0x02, maxSpeed, "integer16")
        if self.toggle:
            self.set_od(0x2291, 0x04, self._pdiCmd["ProfilePosAbs"] + 128, "command")
            self.toggle = not self.toggle
        else:
            self.set_od(0x2291, 0x04, self._pdiCmd["ProfilePosAbs"], "command")
            self.toggle = not self.toggle

    #####################
    ## Private Helpers ##
    #####################
    def _modify_bit(self, bitIndex: int, value: int, byteToModify: int) -> int:
        """
        Modify a specific bit in a byte.

        Parameters:
        bitIndex (int): The position of the bit to modify (0–7).
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

    def _check_bit(self, decimalValue: int, bitPosition: int, expectedValue: int) -> bool:
        """
        Check if a specific bit in a decimal value matches the expected value.

        Parameters:
        decimalValue (int): The decimal value representing a byte (0–255).
        bitPosition (int): The bit position to check (0–7).
        expectedValue (int): The expected value of the bit (0 or 1).

        Returns:
        bool: True if the bit matches the expected value, False otherwise.

        Notes:
        - Validates that `decimalValue` is within the range of a byte (0–255).
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

    def _decode_od_response(self, payload: bytes, valueType: str):
        """
        Decode the payload from a GetOD Entry response based on the specified value type.

        Parameters:
        payload (bytes): The raw data bytes returned from the OD read (excluding headers).
        valueType (str): The expected data type for interpreting the payload.
                        Valid options include:
                        - "UNSIGNED32", "UNSIGNED16", "UNSIGNED8"
                        - "INTEGER32", "INTEGER16", "INTEGER8"

        Returns:
        int: The interpreted integer value based on the provided type.

        Raises:
        ValueError: If the payload length does not match the expected size for the specified type.

        Notes:
        - Uses `int.from_bytes()` for conversion with little-endian byte order.
        - Supports both signed and unsigned formats for 8, 16, and 32-bit integers.
        - Does not perform validation on the `valueType` string casing; the caller must pass it in uppercase.
        - Should be used after stripping EtherNet/IP and CIP headers from the full response.
        """
        if valueType == "UNSIGNED32":
            if len(payload) != 4:
                raise ValueError("Expected 4 bytes for unsigned32")
            return int.from_bytes(payload, byteorder="little", signed=False)
        elif valueType == "UNSIGNED16":
            if len(payload) != 2:
                raise ValueError("Expected 2 bytes for unsigned16")
            return int.from_bytes(payload, byteorder="little", signed=False)
        elif valueType == "UNSIGNED8":
            if len(payload) != 1:
                raise ValueError("Expected 1 bytes for unsigned8")
            return int.from_bytes(payload, byteorder="little", signed=False)
        elif valueType == "INTEGER32":
            if len(payload) != 4:
                raise ValueError("Expected 4 bytes for int32")
            return int.from_bytes(payload, byteorder="little", signed=True)
        elif valueType == "INTEGER16":
            if len(payload) != 2:
                raise ValueError("Expected 2 bytes for int16")
            return int.from_bytes(payload, byteorder="little", signed=True)
        elif valueType == "INTEGER8":
            if len(payload) != 1:
                raise ValueError("Expected 1 bytes for int8")
            return int.from_bytes(payload, byteorder="little", signed=True)

    def _build_rr_data_packet(self, path, data) -> bytes:
        """
        Construct a CIP RRData packet for a GetOD Entry request.

        Parameters:
        path (bytes): The encoded CIP path to the target class and instance (e.g., b'\x20\x64\x24\x01').
        data (bytes): The payload data, typically containing the object index and subindex.

        Returns:
        bytes: A complete RRData byte array ready for encapsulation in an EtherNet/IP request.

        Notes:
        - Sets the service code to `0x32` for a GetOD Entry request.
        - `pathSize` is computed as the number of 16-bit words in the `path`.
        - The RRData format follows:
            [Service][Path Size][Path][Data]
        - This method is typically used internally by `get_od()` to build the data portion of an encapsulation.
        """
        pathSize = len(path) // 2
        # Build CIP RRData
        rrData = bytearray()
        rrData.append(0x32)  # Service: GetOD Entry
        rrData.append(pathSize)
        rrData.extend(path)
        rrData.extend(data)

        return rrData

    def _recv_eip_response(self, timeoutSeconds=2) -> bytes:
        """
        Receive a response from the EtherNet/IP device over TCP.

        Parameters:
        timeoutSeconds (int): Timeout duration in seconds for the socket receive operation. Default is 2 seconds.

        Returns:
        bytes: The raw byte response received from the EtherNet/IP device.

        Notes:
        - Sets a timeout on the socket using `settimeout()` to avoid indefinite blocking.
        - Attempts to read up to 1024 bytes from the TCP socket.
        - If no response is received within the timeout, prints a failure message.
        - Intended to be used after sending an encapsulated request such as GetOD or SetOD.
        - Consider adding error handling or logging for production use instead of `print()`.
        """
        self.eeipClient.tcp_client_socket.settimeout(timeoutSeconds)  # Add timeout for debugging
        try:
            response = self.eeipClient.tcp_client_socket.recv(1024)
            return response
        except socket.timeout:
            print("FAILED: EIP response timed out")

    def _build_encapsulation(self, rrData: bytes) -> bytes:
        """
        Build a complete EtherNet/IP SEND_RRDATA encapsulated packet from the given CIP RRData payload.

        Parameters:
        rrData (bytes): The CIP RRData payload, typically built using `_build_rr_data_packet()`.

        Returns:
        bytes: A complete EtherNet/IP encapsulated packet ready to be sent over TCP.

        Notes:
        - Uses command code `0x6F` for SEND_RRDATA.
        - Includes a 24-byte encapsulation header:
            - Command (2 bytes), Length (2 bytes), Session Handle (4 bytes),
            - Status (4 bytes), Sender Context (8 bytes), Options (4 bytes)
        - Appends interface handle and timeout (6 bytes) and a CPF (Common Packet Format) segment.
        - CPF includes:
            - Item Count = 2
            - Null Address Item (4 bytes)
            - Data Item Type = 0x00B2 (Unconnected Data)
            - Length of `rrData` (2 bytes) + actual `rrData`
        - The session handle is retrieved from `self.eeipClient.connnection_config.session_handle`.
        """
        session = self.eeipClient.connnection_config.session_handle

        # Common Packet Format
        cpf = bytearray()
        cpf += b"\x02\x00"  # Item Count = 2
        cpf += b"\x00\x00\x00\x00"  # Null Address Item
        cpf += b"\xb2\x00"  # Data Item Type = Unconnected Data
        cpf += len(rrData).to_bytes(2, "little")
        cpf += rrData

        # Interface Handle and Timeout
        headerExtra = b"\x00\x00\x00\x00" + b"\x00\x00"  # Interface Handle, Timeout

        # Encapsulation Header
        header = bytearray()
        header += (0x6F).to_bytes(2, "little")  # SEND_RRDATA
        header += len(headerExtra + cpf).to_bytes(2, "little")  # Length
        header += session.to_bytes(4, "little")  # Session handle
        header += b"\x00" * 4  # Status
        header += b"\x00" * 8  # Sender Context
        header += b"\x00" * 4  # Options

        return header + headerExtra + cpf

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

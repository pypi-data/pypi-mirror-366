from enum import IntEnum
import threading
from typing import Any, List
from pydantic import BaseModel, Field, root_validator


class ConnectionType(IntEnum):
    NULL = (0,)
    MULTICAST = (1,)
    POINT_TO_POINT = 2


class Priority(IntEnum):
    LOW = (0,)
    HIGH = (1,)
    SCHEDULED = 2
    URGENT = 3


class RealTimeFormat(IntEnum):
    MODELESS = (0,)
    ZEROLENGTH = (1,)
    HEARTBEAT = 2
    HEADER32BIT = 3


class ConnectionParameters(BaseModel):
    session_handle: int = 0
    multicast_address: int = 0
    connection_serial_number: int = 0
    connection_closed: bool = False
    received_data: Any = Field(default_factory=bytearray, exclude=True)
    lock_receive_data: Any = Field(default_factory=threading.Lock, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def validate_custom_types(cls, values):
        # Ensure custom types are initialized correctly
        if "received_data" not in values:
            values["received_data"] = bytearray()
        if "lock_receive_data" not in values:
            values["lock_receive_data"] = threading.Lock()
        return values


class OutputAssembly(BaseModel):
    """
    o_t: Originator to Target
    The Originator is the device that initiates the communication (usually a controller, PLC, or in this case, the computer/edge device)
    The Target is the device that responds to the communication (typically an I/O device, sensor, or actuator)
    """

    realtime_format: RealTimeFormat = RealTimeFormat.HEADER32BIT
    connection_type: ConnectionType = ConnectionType.POINT_TO_POINT
    output_rpi: int = 0x7A120  # 500ms
    output_size: int = 505
    variable_length: bool = False
    priority: Priority = Priority.SCHEDULED
    owner_redundant: bool = False
    output_assembly: int = 0x64
    iodata: List[int] = Field(default_factory=lambda: [0] * 256)
    connection_id: int = 0


class InputAssembly(BaseModel):
    """
    t_o: Target to Originator
    The Originator is the device that initiates the communication (usually a controller, PLC, or in this case, the computer/edge device)
    The Target is the device that responds to the communication (typically an I/O device, sensor, or actuator)
    """

    realtime_format: RealTimeFormat = RealTimeFormat.MODELESS
    connection_type: ConnectionType = ConnectionType.POINT_TO_POINT
    input_rpi: int = 0x7A120  # 500ms
    input_size: int = 505
    variable_length: bool = False
    priority: Priority = Priority.SCHEDULED
    owner_redundant: bool = False
    input_assembly: int = 0x65
    iodata: List[int] = Field(default_factory=lambda: [0] * 256)
    connection_id: int = 0

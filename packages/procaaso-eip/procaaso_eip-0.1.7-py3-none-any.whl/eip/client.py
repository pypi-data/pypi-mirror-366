import datetime
import random
import threading
import socket
import struct
import traceback
import time
from eip import cip
from eip.encapsulation import (
    CommandsEnum,
    CommonPacketFormat,
    Encapsulation,
    SocketAddress,
)
from eip.models import (
    ConnectionParameters,
    ConnectionType,
    InputAssembly,
    OutputAssembly,
    RealTimeFormat,
)
import logging

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


class EIPBaseClient:
    def __init__(self, originator_udp_port=0x08AE, lock_udp_port=False):
        self.connnection_config = ConnectionParameters()
        self.output_assembly = OutputAssembly()
        self.input_assembly = InputAssembly()

        # TCP
        self.tcp_client_socket = None
        self.tcp_port = 0xAF12

        # UDP
        self.originator_udp_port = originator_udp_port
        self.lock_udp_port = lock_udp_port
        self.target_udp_port = 0x08AE
        self.send_udp_enable = False
        self.udp_client_received_close = False

        # Configuration Assembly
        self.configuration_assembly_instance_id = 0x64

        # Miscellaneous parameters
        self.assembly_object_class = 0x04
        self.last_received_implicit_message = 0
        self.sequence_count = 0
        self.sequence = 0
        self.write_count = 0
        self.cutoff_sequence = -1

    def update_assembly_info(self, connection_dict):
        self.output_assembly = OutputAssembly.parse_obj(connection_dict)
        self.input_assembly = InputAssembly.parse_obj(connection_dict)
        try:
            self.configuration_assembly_instance_id = int(
                connection_dict["configuration_assembly"]
            )
        except KeyError:
            log.debug("No Configuration assembly instance provided")

    def parse_identity_object(self, data, length=19):
        try:
            # Extract the last 'length' bytes of the identity object
            identity_data = data[-length:]

            # Parse each field, converting bytes to the appropriate format
            # Vendor ID (2 bytes)
            vendor_id = int.from_bytes(identity_data[0:2], byteorder="little")

            # Device Type (2 bytes)
            device_type = int.from_bytes(identity_data[2:4], byteorder="little")

            # Product Code (2 bytes)
            product_code = int.from_bytes(identity_data[4:6], byteorder="little")

            # Revision Major (1 byte), Revision Minor (1 byte)
            revision_major = identity_data[6]
            revision_minor = identity_data[7]

            # Status Word (2 bytes)
            status_word = int.from_bytes(identity_data[8:10], byteorder="little")

            # Serial Number (4 bytes)
            serial_number = int.from_bytes(identity_data[10:14], byteorder="little")

            # Product Name Length (1 byte)
            product_name_length = identity_data[14]

            # Product Name (variable length, based on product_name_length)
            product_name = identity_data[15 : 15 + product_name_length].decode("utf-8")

            # Parse the remaining bytes if necessary

            # Output parsed data
            return {
                "vendor_id": vendor_id,
                "device_type": device_type,
                "product_code": product_code,
                "revision": f"{revision_major}.{revision_minor}",
                "status_word": status_word,
                "serial_number": serial_number,
                "product_name": product_name,
            }

        except Exception as e:
            log.debug(f"Error parsing identity object: {e}")
            return None

    def list_identity(self, ip="195.168.1.255", port=44818, timeout=1):
        """
        List and identify potential targets. This command shall be sent as broadcast message using UDP.
        :return: List containing the received information from all devices
        """
        send_data = bytearray(24)
        send_data[0] = 0x63  # Command for "ListIdentity"

        # Create a UDP socket
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.settimeout(timeout)  # Set a timeout for receiving responses

        devices = []

        try:
            # Broadcast the list identity request
            client.sendto(send_data, (ip, port))

            # Listen for responses
            while True:
                try:
                    data, addr = client.recvfrom(1024)  # Buffer size is 1024 bytes

                    # Parse the response data (simplified, needs actual parsing based on CIP spec)
                    device_info = {
                        "ip": addr[0],
                        "data": self.parse_identity_object(data),
                        # You can add more parsing of the `data` to extract useful information
                    }
                    devices.append(device_info)
                except socket.timeout:
                    log.debug("No more responses received.")
                    break

        except Exception as e:
            log.debug(f"Error during ListIdentity broadcast: {e}")

        finally:
            client.close()

        return devices

    def register_session(self, address, port=0xAF12):
        """
        Sends a RegisterSession command to target to initiate session
        :param address IP-Address of the target device
        :param port Port of the target device (Should be 0xAF12)
        :return: Session Handle
        """
        self.udp_client_received_close = False
        if self.connnection_config.session_handle != 0:
            return self.connnection_config.session_handle
        encapsulation = Encapsulation()
        encapsulation.command = CommandsEnum.REGISTER_SESSION
        encapsulation.length = 4
        encapsulation.command_specific_data.extend(
            [1, 0, 0, 0]
        )  # Protocol Version 1, Session option 0
        self.ip_address = address
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.tcp_client_socket:
            self.tcp_client_socket.settimeout(5)
            self.tcp_client_socket.connect((address, port))
            self.thread = threading.Thread(target=self.listen)
            self.thread.start()
            self.tcp_client_socket.send(bytearray(encapsulation.to_bytes()))
            MAX_WAIT_SECONDS = 5
            start_time = time.time()
            try:
                while not self.connnection_config.received_data:                                    
                    if time.time() - start_time > MAX_WAIT_SECONDS:
                        raise TimeoutError("Timed out waiting for session registration response")
                    time.sleep(0.1)  # Prevent CPU spinning
            except Exception:
                raise Exception("Read Timeout" + traceback.format_exc())
            self.connnection_config.session_handle = (
                self.connnection_config.received_data[4]
                | (self.connnection_config.received_data[5] << 8)
                | (self.connnection_config.received_data[6] << 16)
                | (self.connnection_config.received_data[7] << 24)
            )
        return self.connnection_config.session_handle

    def unregister_session(self):
        """
        Sends an UnRegisterSession command to a target to terminate session
        """
        encapsulation = Encapsulation()
        encapsulation.command = CommandsEnum.UNREGISTER_SESSION
        encapsulation.length = 0
        encapsulation.session_handle = self.connnection_config.session_handle
        try:
            self.tcp_client_socket.send(bytearray(encapsulation.to_bytes()))
        except Exception as e:
            log.debug(e)
        if self.tcp_client_socket:
            self.stop_listening = True
            self.tcp_client_socket.shutdown(socket.SHUT_RDWR)
            self.tcp_client_socket.close()
        self.connnection_config.session_handle = 0

    def create_encapsulation_packet(
        self, session_handle=None, command=CommandsEnum.SEND_RRDATA, length=0
    ):
        encapsulation = Encapsulation()
        encapsulation.session_handle = (
            session_handle
            if session_handle is not None
            else self.connnection_config.session_handle
        )
        encapsulation.command = command
        encapsulation.length = length
        encapsulation.command_specific_data.extend(
            [0, 0, 0, 0, 8, 0]
        )  # Interface Handle CIP and Timeout
        return encapsulation

    def create_common_packet_format(self, requested_path, service_code):
        common_packet_format = CommonPacketFormat()
        common_packet_format.data_length = 2 + len(requested_path)
        common_packet_format.data.append(service_code)
        common_packet_format.data.append(int(len(requested_path) / 2) & 0xFF)
        common_packet_format.data.extend(requested_path)
        return common_packet_format

    def get_attribute_single(self, class_id, instance_id, attribute_id):
        """
        Implementation of Common Service "Get_Attribute_Single" - Service Code: 0x0E
        Returns the contents of the specified attribute.
        :param class_id Class id of requested Attribute
        :param instance_id Instance of Requested Attributes (0 for class Attributes)
        :param attribute_id Requested attribute
        :return: Requested Attribute value
        """
        requested_path = self.get_epath(class_id, instance_id, attribute_id)
        if self.connnection_config.session_handle == 0:
            self.connnection_config.session_handle = self.register_session(
                self.ip_address, self.tcp_port
            )
        service_code = (
            int(cip.CIPCommonServices.GET_ATTRIBUTE_SINGLE)
            if attribute_id is not None
            else int(cip.CIPCommonServices.GET_ATTRIBUTES_ALL)
        )
        encapsulation = self.create_encapsulation_packet(
            length=18 + len(requested_path)
        )
        common_packet_format = self.create_common_packet_format(
            requested_path, service_code
        )
        data_to_write = encapsulation.to_bytes() + common_packet_format.to_bytes()
        self.connnection_config.received_data = bytearray()
        self.tcp_client_socket.send(bytearray(data_to_write))
        try:
            while not self.connnection_config.received_data:
                pass
        except Exception:
            raise Exception("Read Timeout")
        if (
            len(self.connnection_config.received_data) > 41
            and self.connnection_config.received_data[42] != 0
        ):
            raise cip.CIPException(
                cip.get_status_code(self.connnection_config.received_data[42])
            )
        return list(self.connnection_config.received_data[44:])

    def get_attributes_all(self, class_id, instance_id):
        """
        Implementation of Common Service "Get_Attributes_All" - Service Code: 0x01
        Returns the contents of the instance or class attributes defined in the object definition.
        :param class_id Class id of requested Attributes
        :param instance_id Instance of Requested Attributes (0 for class Attributes)
        :return: Requested Attributes
        """
        return self.get_attribute_single(class_id, instance_id, None)

    def set_attribute_single(self, class_id, instance_id, attribute_id, value):
        """
        Implementation of Common Service "Set_Attribute_Single" - Service Code: 0x10
        Modifies an attribute value
        :param class_id Class id of requested Attribute to write
        :param instance_id Instance of Requested Attribute to write (0 for class Attributes)
        :param attribute_id Attribute to write
        :param value value(s) to write in the requested attribute
        """
        requested_path = self.get_epath(class_id, instance_id, attribute_id)
        if self.connnection_config.session_handle == 0:
            self.connnection_config.session_handle = self.register_session(
                self.ip_address, self.tcp_port
            )
        encapsulation = self.create_encapsulation_packet(
            length=18 + len(requested_path) + len(value)
        )
        common_packet_format = self.create_common_packet_format(
            requested_path, int(cip.CIPCommonServices.SET_ATTRIBUTE_SINGLE)
        )
        common_packet_format.data.extend(value)
        common_packet_format.data_length = len(common_packet_format.data)
        data_to_write = encapsulation.to_bytes() + common_packet_format.to_bytes()
        self.connnection_config.received_data = bytearray()
        self.tcp_client_socket.settimeout(8)
        self.tcp_client_socket.send(bytearray(data_to_write))
        try:
            while not self.connnection_config.received_data:
                pass
        except Exception:
            raise Exception("Read Timeout")
        if (
            len(self.connnection_config.received_data) > 41
            and self.connnection_config.received_data[42] != 0
        ):
            raise cip.CIPException(
                cip.get_status_code(self.connnection_config.received_data[42])
            )
        return list(self.connnection_config.received_data[44:])

    def __create_common_packet_format_forward_open(
        self, large_forward_open, length_offset, o_t_header_offset, t_o_header_offset
    ):
        common_packet_format = CommonPacketFormat()
        common_packet_format.data_length = 41 + length_offset
        if large_forward_open:
            common_packet_format.data_length += 4

        service_code = 0x5B if large_forward_open else 0x54
        common_packet_format.data.append(service_code)
        common_packet_format.data.append(2)
        common_packet_format.data.extend([0x20, 6, 0x24, 1, 0x03, 0xFA])

        self.output_assembly.connection_id = random.randint(1, 0xFFFE)
        self.input_assembly.connection_id = random.randint(1, 0xFFFE)
        self.connnection_config.connection_serial_number = random.randint(1, 0xFFFE)
        log.debug(
            f"Connection info: {self.output_assembly.connection_id} {self.input_assembly.connection_id} {self.connnection_config.connection_serial_number}"
        )

        common_packet_format.data.extend(
            [
                self.output_assembly.connection_id & 0xFF,
                (self.output_assembly.connection_id & 0xFF00) >> 8,
                (self.output_assembly.connection_id & 0xFF0000) >> 16,
                (self.output_assembly.connection_id & 0xFF000000) >> 24,
                self.input_assembly.connection_id & 0xFF,
                (self.input_assembly.connection_id & 0xFF00) >> 8,
                (self.input_assembly.connection_id & 0xFF0000) >> 16,
                (self.input_assembly.connection_id & 0xFF000000) >> 24,
                self.connnection_config.connection_serial_number & 0xFF,
                (self.connnection_config.connection_serial_number & 0xFF00) >> 8,
                0xFF,
                0,
                0xFF,
                0xFF,
                0xFF,
                0xFF,
                3,
                0,
                0,
                0,
                self.output_assembly.output_rpi & 0xFF,
                (self.output_assembly.output_rpi & 0xFF00) >> 8,
                (self.output_assembly.output_rpi & 0xFF0000) >> 16,
                (self.output_assembly.output_rpi & 0xFF000000) >> 24,
            ]
        )

        connection_size = self.output_assembly.output_size + o_t_header_offset
        network_connection_parameters = (
            (connection_size & 0x1FF)
            | (self.output_assembly.variable_length << 9)
            | ((self.output_assembly.priority & 0x03) << 10)
            | ((self.output_assembly.connection_type & 0x03) << 13)
            | (self.output_assembly.owner_redundant << 15)
        )
        if large_forward_open:
            network_connection_parameters = (
                (connection_size & 0xFFFF)
                | (self.output_assembly.variable_length << 25)
                | ((self.output_assembly.priority & 0x03) << 26)
                | ((self.output_assembly.connection_type & 0x03) << 29)
                | (self.output_assembly.owner_redundant << 31)
            )

        common_packet_format.data.append(network_connection_parameters & 0xFF)
        common_packet_format.data.append((network_connection_parameters & 0xFF00) >> 8)
        if large_forward_open:
            common_packet_format.data.append(
                (network_connection_parameters & 0xFF0000) >> 16
            )
            common_packet_format.data.append(
                (network_connection_parameters & 0xFF000000) >> 24
            )

        common_packet_format.data.extend(
            [
                self.input_assembly.input_rpi & 0xFF,
                (self.input_assembly.input_rpi & 0xFF00) >> 8,
                (self.input_assembly.input_rpi & 0xFF0000) >> 16,
                (self.input_assembly.input_rpi & 0xFF000000) >> 24,
            ]
        )

        connection_size = self.input_assembly.input_size + t_o_header_offset
        network_connection_parameters = (
            (connection_size & 0x1FF)
            | (self.input_assembly.variable_length << 9)
            | ((self.input_assembly.priority & 0x03) << 10)
            | ((self.input_assembly.connection_type & 0x03) << 13)
            | (self.input_assembly.owner_redundant << 15)
        )
        if large_forward_open:
            network_connection_parameters = (
                (connection_size & 0xFFFF)
                | (self.input_assembly.variable_length << 25)
                | ((self.input_assembly.priority & 0x03) << 26)
                | ((self.input_assembly.connection_type & 0x03) << 29)
                | (self.input_assembly.owner_redundant << 31)
            )

        common_packet_format.data.append(network_connection_parameters & 0xFF)
        common_packet_format.data.append((network_connection_parameters & 0xFF00) >> 8)
        if large_forward_open:
            common_packet_format.data.append(
                (network_connection_parameters & 0xFF0000) >> 16
            )
            common_packet_format.data.append(
                (network_connection_parameters & 0xFF000000) >> 24
            )

        common_packet_format.data.extend(
            [
                0x01,
                0x02
                + (
                    0
                    if self.output_assembly.connection_type == ConnectionType.NULL
                    else 1
                )
                + (
                    0
                    if self.input_assembly.connection_type == ConnectionType.NULL
                    else 1
                ),
                0x20,
                self.assembly_object_class,
                0x24,
                self.configuration_assembly_instance_id,
            ]
        )
        if self.output_assembly.connection_type != ConnectionType.NULL:
            common_packet_format.data.extend(
                [0x2C, self.output_assembly.output_assembly]
            )
        if self.input_assembly.connection_type != ConnectionType.NULL:
            common_packet_format.data.extend([0x2C, self.input_assembly.input_assembly])

        common_packet_format.socketaddr_info_o_t = SocketAddress()
        common_packet_format.socketaddr_info_o_t.sin_port = self.originator_udp_port
        common_packet_format.socketaddr_info_o_t.sin_family = 2

        if self.output_assembly.connection_type == ConnectionType.MULTICAST:
            multicast_response_address = self.get_multicast_address(
                self.ip2int(self.ip_address)
            )
            common_packet_format.socketaddr_info_o_t.sin_address = (
                multicast_response_address
            )
            self.connnection_config.multicast_address = (
                common_packet_format.socketaddr_info_o_t.sin_address
            )
        else:
            common_packet_format.socketaddr_info_o_t.sin_address = 0

        return common_packet_format

    def tcp_forward_open_command(self, large_forward_open=False):
        o_t_header_offset = (
            6
            if self.output_assembly.realtime_format == RealTimeFormat.HEADER32BIT
            else (
                0
                if self.output_assembly.realtime_format == RealTimeFormat.HEARTBEAT
                else 2
            )
        )
        t_o_header_offset = (
            6
            if self.input_assembly.realtime_format == RealTimeFormat.HEADER32BIT
            else (
                0
                if self.input_assembly.realtime_format == RealTimeFormat.HEARTBEAT
                else 2
            )
        )
        length_offset = (
            5
            + (0 if self.input_assembly.connection_type == ConnectionType.NULL else 2)
            + (0 if self.output_assembly.connection_type == ConnectionType.NULL else 2)
        )
        encapsulation = self.create_encapsulation_packet(
            length=41 + length_offset + (4 if large_forward_open else 0)
        )
        common_packet_format = self.__create_common_packet_format_forward_open(
            large_forward_open, length_offset, o_t_header_offset, t_o_header_offset
        )
        encapsulation.length = len(common_packet_format.to_bytes()) + 6
        data_to_write = encapsulation.to_bytes() + common_packet_format.to_bytes()
        self.connnection_config.received_data = bytearray()
        self.tcp_client_socket.send(bytearray(data_to_write))

    def forward_open(self, large_forward_open=False, start_threads=True):
        """
        The Forward Open Service (Service Code 0x54 and Large_Forward_Open service (Service Code 0x5B) are used to establish a Connection with a Target Device.
        The maximum data size for Forward open is 511 bytes, and 65535 for large forward open
        Two independent Threads are opened to send and receive data via UDP (Implicit Messaging)
        :param large_forward_open: Use Service code 0x58 (Large_Forward_Open) if true, otherwise 0x54 (Forward_Open)
        """
        self._open_udp_socket()
        self.tcp_forward_open_command(large_forward_open=large_forward_open)
        if float(self.input_assembly.input_rpi) / 1000000.0 >= 0.2:
            self.cutoff_sequence = 32
        try:
            while not self.connnection_config.received_data:
                pass
        except Exception:
            raise Exception("Read Timeout")
        if (
            len(self.connnection_config.received_data) > 41
            and self.connnection_config.received_data[42] != 0
        ):
            raise cip.CIPException(
                cip.get_status_code(self.connnection_config.received_data[42])
            )
        self._handle_socket_info()
        self._start_udp_threads(start_threads)

    def _handle_socket_info(self):
        item_count = self.connnection_config.received_data[30] + (
            self.connnection_config.received_data[31] << 8
        )
        length_unconnected_data_item = self.connnection_config.received_data[38] + (
            self.connnection_config.received_data[39] << 8
        )
        self.output_assembly.connection_id = (
            self.connnection_config.received_data[44]
            + (self.connnection_config.received_data[45] << 8)
            + (self.connnection_config.received_data[46] << 16)
            + (self.connnection_config.received_data[47] << 24)
        )
        self.input_assembly.connection_id = (
            self.connnection_config.received_data[48]
            + (self.connnection_config.received_data[49] << 8)
            + (self.connnection_config.received_data[50] << 16)
            + (self.connnection_config.received_data[51] << 24)
        )
        self._parse_socket_info(item_count, length_unconnected_data_item)

    def _parse_socket_info(self, item_count, length_unconnected_data_item):
        number_of_current_item = 0
        while item_count > 2:
            type_id = self.connnection_config.received_data[
                40 + length_unconnected_data_item + 20 * number_of_current_item
            ] + (
                self.connnection_config.received_data[
                    40 + length_unconnected_data_item + 21 * number_of_current_item
                ]
                << 8
            )
            if type_id == 0x8001:
                socket_info_item = SocketAddress()
                socket_info_item.sin_address = (
                    self.connnection_config.received_data[
                        40
                        + length_unconnected_data_item
                        + 11
                        + 20 * number_of_current_item
                    ]
                    + (
                        self.connnection_config.received_data[
                            40
                            + length_unconnected_data_item
                            + 10
                            + 20 * number_of_current_item
                        ]
                        << 8
                    )
                    + (
                        self.connnection_config.received_data[
                            40
                            + length_unconnected_data_item
                            + 9
                            + 20 * number_of_current_item
                        ]
                        << 16
                    )
                    + (
                        self.connnection_config.received_data[
                            40
                            + length_unconnected_data_item
                            + 8
                            + 20 * number_of_current_item
                        ]
                        << 24
                    )
                )
                socket_info_item.sin_port = self.connnection_config.received_data[
                    40 + length_unconnected_data_item + 7 + 20 * number_of_current_item
                ] + (
                    self.connnection_config.received_data[
                        40
                        + length_unconnected_data_item
                        + 6
                        + 20 * number_of_current_item
                    ]
                    << 8
                )
                if self.input_assembly.connection_type == ConnectionType.MULTICAST:
                    self.connnection_config.multicast_address = (
                        socket_info_item.sin_address
                    )
                if not self.lock_udp_port:
                    self.target_udp_port = socket_info_item.sin_port
            number_of_current_item += 1
            item_count -= 1

    def _open_udp_socket(self):
        self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_server_socket.bind(("", self.originator_udp_port))
        if self.input_assembly.connection_type == ConnectionType.MULTICAST:
            mc_address = self.int2ip(self.connnection_config.multicast_address)
            group = socket.inet_aton(mc_address)
            mreq = struct.pack("=4sL", group, socket.INADDR_ANY)
            self.udp_server_socket.setsockopt(
                socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq
            )

    def _start_udp_threads(self, start_threads):
        if start_threads:
            self.udp_recv_thread = threading.Thread(target=self.udp_listen)
            self.udp_recv_thread.daemon = True
            self.udp_recv_thread.start()

    def forward_close(self, shutdown=True):
        """
        Closes a connection (Service code 0x4E)
        """
        self.stop_listening_udp = True
        time.sleep(1)
        length_offset = (
            5
            + (0 if self.input_assembly.connection_type == ConnectionType.NULL else 2)
            + (0 if self.output_assembly.connection_type == ConnectionType.NULL else 2)
        )
        encapsulation = self.create_encapsulation_packet(length=16 + 17 + length_offset)
        common_packet_format = CommonPacketFormat()
        common_packet_format.item_count = 0x02
        common_packet_format.address_item = 0
        common_packet_format.address_length = 0
        common_packet_format.data_item = 0xB2
        common_packet_format.data_length = 17 + length_offset
        common_packet_format.data.extend([0x4E, 2, 0x20, 6, 0x24, 1, 0x03, 0xFA])
        common_packet_format.data.extend(
            [
                self.connnection_config.connection_serial_number & 0xFF,
                (self.connnection_config.connection_serial_number & 0xFF00) >> 8,
            ]
        )
        common_packet_format.data.extend([0xFF, 0, 0xFF, 0xFF, 0xFF, 0xFF])
        common_packet_format.data.append(
            2
            + (0 if self.output_assembly.connection_type == ConnectionType.NULL else 1)
            + (0 if self.input_assembly.connection_type == ConnectionType.NULL else 1)
        )
        common_packet_format.data.append(0)
        common_packet_format.data.extend(
            [
                0x20,
                self.assembly_object_class,
                0x24,
                self.configuration_assembly_instance_id,
            ]
        )
        if self.output_assembly.connection_type != ConnectionType.NULL:
            common_packet_format.data.extend(
                [0x2C, self.output_assembly.output_assembly]
            )
        if self.input_assembly.connection_type != ConnectionType.NULL:
            common_packet_format.data.extend([0x2C, self.input_assembly.input_assembly])
        try:
            data_to_write = encapsulation.to_bytes() + common_packet_format.to_bytes()
            self.connnection_config.received_data = bytearray()
            self.tcp_client_socket.send(bytearray(data_to_write))
        except Exception as e:
            log.debug(
                f"Handle exception to allow to close the connection if closed from the target before: {e}"
            )
        if (
            len(self.connnection_config.received_data) > 41
            and self.connnection_config.received_data[42] != 0
        ):
            raise cip.CIPException(
                cip.get_status_code(self.connnection_config.received_data[42])
            )
        if shutdown:
            self._shutdown_udp_server()

    def _shutdown_udp_server(self):
        try:
            self.udp_server_socket.close()
        except Exception as e:
            log.debug(f"Error closing UDP server socket: {e}")

    def udp_listen(self):
        self.stop_listening_udp = False
        self.received_data_udp = bytearray()
        self.udp_server_socket.settimeout(
            (self.input_assembly.input_rpi) / 1000000.0 * 2
        )
        try:
            while not self.stop_listening_udp:
                if self.udp_client_received_close:
                    pass
                    # if not self.tcp_client_socket._closed:
                    #     self.unregister_session()
                    # else:
                    #     self.register_session(self.ip_address)
                    #     self.tcp_forward_open_command()
                else:
                    self._receive_udp_message()
                    try:
                        self._send_udp()
                    except Exception:
                        log.debug("Failed UDP Write")
                time.sleep(0.001)
        finally:
            # self.udp_server_socket.close()
            log.debug("UDP server socket closed")

    def _receive_udp_message(self):
        try:
            bytes_address_pair = self.udp_server_socket.recvfrom(564)
            message = bytes_address_pair[0]
            self.received_data_udp = message
            if len(self.received_data_udp) > 20:
                self._handle_udp_message()
        except socket.timeout:
            log.debug("No data received within the timeout period")
            self.udp_client_received_close = True
        except Exception as e:
            log.debug(f"Error while receiving data: {e}")
            if self.connnection_config.lock_receive_data.locked():
                self.connnection_config.lock_receive_data.release()
            self.received_data_udp = bytearray()

    def _handle_udp_message(self):
        connection_id = (
            self.received_data_udp[6]
            + (self.received_data_udp[7] << 8)
            + (self.received_data_udp[8] << 16)
            + (self.received_data_udp[9] << 24)
        )
        sequence_count = (
            self.received_data_udp[10]
            + (self.received_data_udp[11] << 8)
            + (self.received_data_udp[12] << 16)
            + (self.received_data_udp[13] << 24)
        )
        if (
            connection_id == self.input_assembly.connection_id
            or self.connnection_config.connection_closed
        ):
            header_offset = (
                4
                if self.input_assembly.realtime_format == RealTimeFormat.HEADER32BIT
                else 0
            )
            self.connnection_config.lock_receive_data.acquire()
            self.input_assembly.iodata = list(
                self.received_data_udp[20 + header_offset :]
            )
            self.connnection_config.lock_receive_data.release()
            self.last_received_implicit_message = datetime.datetime.now(datetime.UTC)
            self.sequence_count = sequence_count

    def _reopen_connection(self):
        log.debug("Closing and reopening connection")
        self.connnection_config.connection_closed = True
        self.forward_close(shutdown=False)
        time.sleep(0.01)
        self.tcp_forward_open_command()
        self.sequence_count = 0  # Reset sequence count after re-opening

    def _send_udp(self):

        try:
            message = list()

            # -------------------Item Count
            message.append(2)
            message.append(0)
            # -------------------Item Count

            # -------------------Type ID
            message.append(0x02)
            message.append(0x80)
            # -------------------Type ID

            # -------------------Length
            message.append(0x08)
            message.append(0x00)
            # -------------------Length

            # -------------------Connection ID
            message.append(self.output_assembly.connection_id & 0xFF)
            message.append((self.output_assembly.connection_id & 0xFF00) >> 8)
            message.append((self.output_assembly.connection_id & 0xFF0000) >> 16)
            message.append((self.output_assembly.connection_id & 0xFF000000) >> 24)
            # -------------------Connection ID

            # -------------------sequence count
            self.write_count += 1
            message.append(self.write_count & 0xFF)
            message.append((self.write_count & 0xFF00) >> 8)
            message.append((self.write_count & 0xFF0000) >> 16)
            message.append((self.write_count & 0xFF000000) >> 24)
            # -------------------sequence count

            # -------------------Type ID
            message.append(0xB1)
            message.append(0x00)
            # -------------------Type ID

            header_offset = 0
            if self.output_assembly.realtime_format == RealTimeFormat.HEADER32BIT:
                header_offset = 4
            o_t_length = self.output_assembly.output_size + header_offset + 2

            # -------------------Length
            message.append(o_t_length & 0xFF)
            message.append((o_t_length & 0xFF00) >> 8)
            # -------------------Length

            # -------------------Sequence count
            self.sequence += 1
            if self.output_assembly.realtime_format != RealTimeFormat.HEARTBEAT:
                message.append(self.sequence & 0xFF)
                message.append((self.sequence & 0xFF00) >> 8)
            # -------------------Sequence count

            if self.output_assembly.realtime_format == RealTimeFormat.HEADER32BIT:
                message.append(1)
                message.append(0)
                message.append(0)
                message.append(0)
            # -------------------write data
            # self.o_t_iodata[0] = self.o_t_iodata[0] + 1
            for i in range(0, self.output_assembly.output_size):
                message.append(self.output_assembly.iodata[i])
            # -------------------write data

            self.udp_server_socket.sendto(
                bytearray(message), (self.ip_address, self.target_udp_port)
            )
        except Exception as e:
            log.debug(e)

    def listen(self):
        self.stop_listening = False
        self.connnection_config.received_data = bytearray()
        try:
            while not self.stop_listening:
                if not self.connnection_config.received_data and self.tcp_client_socket:
                    try:
                        self.connnection_config.received_data = (
                            self.tcp_client_socket.recv(255)
                        )
                    except (ConnectionAbortedError, OSError) as e:
                        log.debug(f"Socket error: {e}")
                        break
                time.sleep(0.001)
        except socket.timeout:
            self.connnection_config.received_data = bytearray()
        finally:
            if self.tcp_client_socket:
                self.tcp_client_socket.close()

    def get_epath(self, class_id, instance_id, attribute_id):
        """
        Get the Encrypted Request Path
        :param class_id: Requested Class ID
        :param instance_id: Requested Instance ID
        :param attribute_id: Requested Attribute ID - if "0" the attribute will be ignored
        :return: Encrypted Request Path
        """
        path = []
        if class_id < 0xFF:
            path.extend([0x20, class_id & 0xFF])
        else:
            path.extend([0x21, 0, class_id & 0x00FF, (class_id & 0xFF00) >> 8])
        if instance_id < 0xFF:
            path.extend([0x24, instance_id & 0xFF])
        else:
            path.extend([0x25, 0, instance_id & 0x00FF, (instance_id & 0xFF00) >> 8])
        if attribute_id is not None:
            if attribute_id < 0xFF:
                path.extend([0x30, attribute_id & 0xFF])
            else:
                path.extend(
                    [0x31, 0, attribute_id & 0x00FF, (attribute_id & 0xFF00) >> 8]
                )
        return path

    def ip2int(self, addr):
        return struct.unpack("!I", socket.inet_aton(addr))[0]

    def int2ip(self, addr):
        return socket.inet_ntoa(struct.pack("!I", addr))

    def get_multicast_address(self, device_ip_address):
        cip_mcast_base_addr = 0xEFC00100
        cip_host_mask = 0x3FF
        netmask = 0
        if device_ip_address <= 0x7FFFFFFF:  # Class A Network
            netmask = 0xFF000000
        elif device_ip_address <= 0xBFFFFFFF:  # Class B Network
            netmask = 0xFFFF0000
        elif device_ip_address <= 0xDFFFFFFF:  # Class C Network
            netmask = 0xFFFFFF00
        host_id = device_ip_address & ~netmask
        mcast_index = (host_id - 1) & cip_host_mask
        return cip_mcast_base_addr + mcast_index * 32


class EthernetIPClient(EIPBaseClient):
    def __init__(self):
        super().__init__()

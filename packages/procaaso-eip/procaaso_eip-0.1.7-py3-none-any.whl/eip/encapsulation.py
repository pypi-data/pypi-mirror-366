from enum import IntEnum

class StatusEnum(IntEnum):
    '''
    Table 2-3.3 Error Codes
    '''
    SUCCESS = 0x0000
    INVALID_COMMAND = 0x0001
    INSUFFICIENT_MEMORY = 0x0002
    INCORRECT_DATA = 0x0003
    INVALID_SESSION_HANDLE = 0x0064
    INVALID_LENGTH = 0x0065
    UNSUPPORTED_ENCAPSULATION_PROTOCOL = 0x0069

class CommandsEnum(IntEnum):
    '''
    Table 2-3.2 Encapsulation Commands
    '''
    NOP = 0x0000
    LIST_SERVICES = 0x0004
    LIST_IDENTITY = 0x0063
    LIST_INTERFACES = 0x0064
    REGISTER_SESSION = 0x0065
    UNREGISTER_SESSION = 0x0066
    SEND_RRDATA = 0x006F
    SENDUNITDATA = 0x0070
    INDICATE_STATUS = 0x0072
    CANCEL = 0x0073

class SocketAddress:
    '''
    Socket Address (see section 2-6.3.2)
    '''
    def __init__(self):
        self.sin_family = 0
        self.sin_port = 0
        self.sin_address = 0
        self.sin_zero = [0] * 8

class Encapsulation:
    def __init__(self):
        self.sender_context = [0] * 8
        self.command_specific_data = []
        self.session_handle = 0
        self.options = 0
        self.status = StatusEnum.SUCCESS
        self.command = 0
        self.length = 0

    def to_bytes(self):
        returnvalue = []
        returnvalue.append(self.command & 0x00FF)
        returnvalue.append((self.command & 0xFF00) >> 8)
        returnvalue.append(self.length & 0x00FF)
        returnvalue.append((self.length & 0xFF00) >> 8)
        returnvalue.append(self.session_handle & 0xFF)
        returnvalue.append((self.session_handle & 0xFF00) >> 8)
        returnvalue.append((self.session_handle & 0xFF0000) >> 16)
        returnvalue.append((self.session_handle & 0xFF000000) >> 24)
        returnvalue.append(self.status & 0xFF)
        returnvalue.append((self.status & 0xFF00) >> 8)
        returnvalue.append((self.status & 0xFF0000) >> 16)
        returnvalue.append((self.status & 0xFF000000) >> 24)
        returnvalue.extend(self.sender_context)
        returnvalue.append(self.options & 0xFF)
        returnvalue.append((self.options & 0xFF00) >> 8)
        returnvalue.append((self.options & 0xFF0000) >> 16)
        returnvalue.append((self.options & 0xFF000000) >> 24)
        for data in self.command_specific_data:
            returnvalue.append(data & 0xFF)
        return returnvalue

    class CIPIdentityItem:
        '''
        Table 2-4.4 CIP Identity Item
        '''
        def __init__(self):
            self.item_type_code = 0
            self.item_length = 0
            self.encapsulation_protocol_version = 0
            self.socket_address = SocketAddress()
            self.vendor_id = 0
            self.device_type = 0
            self.product_code = 0
            self.revision = [0, 0]
            self.status = 0
            self.serial_number = 0
            self.product_name_length = 0
            self.product_name = ""
            self.state = 0

        def get_cip_identity_item(self, starting_byte, receive_data):
            starting_byte += 1
            self.item_type_code = receive_data[0 + starting_byte] | (receive_data[1 + starting_byte] << 8)
            self.item_length = receive_data[2 + starting_byte] | (receive_data[3 + starting_byte] << 8)
            self.encapsulation_protocol_version = receive_data[4 + starting_byte] | (receive_data[5 + starting_byte] << 8)
            self.socket_address.sin_family = receive_data[7 + starting_byte] | (receive_data[6 + starting_byte] << 8)
            self.socket_address.sin_port = receive_data[9 + starting_byte] | (receive_data[8 + starting_byte] << 8)
            self.socket_address.sin_address = receive_data[13 + starting_byte] | (receive_data[12 + starting_byte] << 8) | (receive_data[11 + starting_byte] << 16) | (receive_data[10 + starting_byte] << 24)
            self.vendor_id = receive_data[22 + starting_byte] | (receive_data[23 + starting_byte] << 8)
            self.device_type = receive_data[24 + starting_byte] | (receive_data[25 + starting_byte] << 8)
            self.product_code = receive_data[26 + starting_byte] | (receive_data[27 + starting_byte] << 8)
            self.revision[0] = receive_data[28 + starting_byte]
            self.revision[1] = receive_data[29 + starting_byte]
            self.status = receive_data[30 + starting_byte] | (receive_data[31 + starting_byte] << 8)
            self.serial_number = receive_data[32 + starting_byte] | (receive_data[33 + starting_byte] << 8) | (receive_data[34 + starting_byte] << 16) | (receive_data[35 + starting_byte] << 24)
            self.product_name_length = receive_data[36 + starting_byte]
            product_name = bytearray(self.product_name_length)
            for i in range(len(product_name)):
                product_name[i] = receive_data[37 + starting_byte + i]
            self.product_name = str(product_name, 'utf-8')
            self.state = receive_data[-1]

        def get_ip_address(self, address):
            return f"{(address >> 24) & 0xFF}.{(address >> 16) & 0xFF}.{(address >> 8) & 0xFF}.{address & 0xFF}"

class CommonPacketFormat:
    def __init__(self):
        self.item_count = 2
        self.address_item = 0x0000
        self.address_length = 0
        self.data_item = 0xB2  # 0xB2 = Unconnected Data Item
        self.data_length = 8
        self.data = []
        self.sockaddr_info_item_o_t = 0x8001  # 8000 for O->T and 8001 for T->O - Volume 2 Table 2-6.9
        self.sockaddr_info_length = 16
        self.socketaddr_info_o_t = None

    def to_bytes(self):
        if self.socketaddr_info_o_t is not None:
            self.item_count = 3
        returnvalue = []
        returnvalue.append(self.item_count & 0xFF)
        returnvalue.append((self.item_count & 0xFF00) >> 8)
        returnvalue.append(self.address_item & 0xFF)
        returnvalue.append((self.address_item & 0xFF00) >> 8)
        returnvalue.append(self.address_length & 0xFF)
        returnvalue.append((self.address_length & 0xFF00) >> 8)
        returnvalue.append(self.data_item & 0xFF)
        returnvalue.append((self.data_item & 0xFF00) >> 8)
        returnvalue.append(self.data_length & 0xFF)
        returnvalue.append((self.data_length & 0xFF00) >> 8)
        returnvalue.extend(self.data)
        if self.socketaddr_info_o_t is not None:
            self.socketaddr_info_o_t.sin_zero = [0] * 8
            returnvalue.append(self.sockaddr_info_item_o_t & 0xFF)
            returnvalue.append((self.sockaddr_info_item_o_t & 0xFF00) >> 8)
            returnvalue.append(self.sockaddr_info_length & 0xFF)
            returnvalue.append((self.sockaddr_info_length & 0xFF00) >> 8)

            returnvalue.append((self.socketaddr_info_o_t.sin_family & 0xFF00) >> 8)
            returnvalue.append(self.socketaddr_info_o_t.sin_family & 0xFF)

            returnvalue.append((self.socketaddr_info_o_t.sin_port & 0xFF00) >> 8)
            returnvalue.append(self.socketaddr_info_o_t.sin_port & 0xFF)

            returnvalue.append((self.socketaddr_info_o_t.sin_address & 0xFF00) >> 24)
            returnvalue.append((self.socketaddr_info_o_t.sin_address & 0xFF00) >> 16)
            returnvalue.append((self.socketaddr_info_o_t.sin_address & 0xFF00) >> 8)
            returnvalue.append(self.socketaddr_info_o_t.sin_address & 0xFF)

            returnvalue.extend(self.socketaddr_info_o_t.sin_zero)
        return returnvalue

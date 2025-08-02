

import socket


import time

import struct

from enum import Enum


from abc import ABC, abstractmethod

import python_zatobox.iotconfig_pb2 as protobuff_obj


class InputReg(ABC):
    id = 0
    attributes : list[str]
    units : list[str]



class InputRegMainMeter(InputReg):
    def __init__(self):
        self.power = 0.0
        self.energy_import = 0.0
        self.energy_export = 0.0
        self.power_1 = 0.0
        self.power_2 = 0.0
        self.power_3 = 0.0
        self.voltage_1 = 0.0
        self.voltage_2 = 0.0
        self.voltage_3 = 0.0
        self.voltage_U12 = 0.0
        self.voltage_U23 = 0.0
        self.voltage_U31 = 0.0
        self.current_1 = 0.0
        self.current_2 = 0.0
        self.current_3 = 0.0
        self.pf_1 = 0.0
        self.pf_2 = 0.0
        self.pf_3 = 0.0
        self.frequency = 0.0
        self.reserve1 = 0.0 
        self.reserve2 = 0.0 
        self.reserve3 = 0.0 
        self.reserve4 = 0.0 
        self.reserve5 = 0.0 
        self.reserve6 = 0.0 
        self.reserve7 = 0.0 
        self.reserve8 = 0.0 
        self.reserve9 = 0.0 
        self.reserve10 = 0.0 
        self.reserve11 = 0.0 
        self.attributes = [
            'power', 'energy_import', 'energy_export', 'power_1', 'power_2', 'power_3',
            'voltage_1', 'voltage_2', 'voltage_3', 'voltage_U12', 'voltage_U23', 'voltage_U31',
            'current_1', 'current_2', 'current_3', 'pf_1', 'pf_2', 'pf_3', 'frequency',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5', 'reserve6', 'reserve7', 
            'reserve8', 'reserve9', 'reserve10', 'reserve11', 
        ]
        self.units = [
            'W', 'kWh', 'kWh', 'W', 'W', 'W',
            'V', 'V', 'V', 'V', 'V', 'V',
            'A', 'A', 'A', '', '', '', 'Hz',
            '', '', '', '', '', '', '', 
            '', '', '', '', 
        ]
class InputRegGasMeter(InputReg):
    def __init__(self):
        self.energy = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0
        self.reserve28 = 0.0
        self.reserve29 = 0.0
        # Attribute list for InputRegGM
        self.attributes = [
            'energy',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27', 'reserve28', 'reserve29'
        ]

        self.units = [
            'm3',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', ''
        ]

class InputRegPV(InputReg):
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0
        self.reserve28 = 0.0
        # Attribute list for InputRegPV
        self.attributes = [
            'power', 'energy',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27', 'reserve28'
        ]
        self.units = [
            'W', 'kWh', 
            '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', ''
        ]

class InputRegBattery(InputReg):
    def __init__(self):
        self.power = 0.0
        self.energy_charge = 0.0
        self.energy_discharge = 0.0
        self.soc = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        # Attribute list for InputRegBA
        self.attributes = [
            'power', 'energy_charge', 'energy_discharge', 'soc',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26'
        ]
        self.units = [
            'W', 'kWh', 'kWh', '%', 
            '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', ''
        ]

class InputRegUsage(InputReg):
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0
        self.reserve28 = 0.0
        # Attribute list for InputRegUS
        self.attributes = [
            'power', 'energy',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27', 'reserve28'
        ]

        self.units = [
            'W', 'kWh', 
            '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', ''
        ]
class InputRegCharger(InputReg):
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.soc = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0

        # Attribute list for InputRegCH
        self.attributes = [
            'power', 'energy', 'soc',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27'
        ]
        self.units = [
            'W', 'kWh', '%', 
            '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', '', '',
            '', '', '', ''
        ]




class Vanubus:
    def __init__(self, host, port=3333) -> None:
        isipadress : bool = False
        try:
            socket.inet_aton(host)
            # legal
            isipadress = True
        except socket.error:
            # Not legal
            isipadress = False

        if (isipadress):
            self.ip_address = host
            self.port = port
        else:
            try:
                ip = socket.gethostbyname(host)
                print(f"{host} resolved to {ip}")
                self.ip_address = ip
            except socket.gaierror:
                print(f"Could not resolve {host}")
        
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.settimeout(3)  # 5 seconds timeout


    def setipadress(self, ipadress):
        self.ip_address = ipadress



    def getdata(self, sensorids = []) -> list[InputReg]:

        # Create tx_buffer of 64 bytes, initialized with zeros
        tx_buffer = bytearray(64)

        # Set id for request
        tx_buffer[0] = 1

        # Fill the buffer with client ids, starting at index 1
        for i in range(len(sensorids)):
            tx_buffer[i + 1] = sensorids[i]  # or clientdata[i].id if objects

        rxdata = self._send_message(tx_buffer, 64)
        if len(rxdata) > 0:
            return self._decode_rx_buffer(rxdata, 1, sensorids)
        else: 
            return []

    def request_all_info(self):
        # Create tx_buffer of 64 bytes, initialized with zeros
        id_request = bytearray(1)
        # Set id for request
        id_request[0] = 4

        # Create a CallBackMessage
        callback_message = protobuff_obj.CallBackMessage()
        callback_message.plantid = ""
        callback_message.callback = "" 
        callback_message.connectionid = ""

        # Create a FeedBack message
        feedback = protobuff_obj.FeedBack()
        feedback.all = True

        # Set the feedback field in the CallBackMessage
        callback_message.feedback.CopyFrom(feedback)

        # Serialize the message to bytes
        serialized_message = callback_message.SerializeToString()


        tx_buffer = id_request + serialized_message
        
        rxdata = self._send_message( tx_buffer, len(tx_buffer))


        if len(rxdata) == 0:
            #error getting message
            return None
        
        # Deserialize from a string
        feedbackmessage = protobuff_obj.FeedBackMessage()
        try:
            feedbackmessage.ParseFromString(rxdata)
            return feedbackmessage
        except Exception as e:
            print(f"AssertionError: {e}")

        return None
    
    def _send_message(self, tx_buffer:bytearray, len) -> bytes:        
        if (not(self._is_connected())):
            connected = self._connect()
            if (not(connected)):
                return []


        # Send the buffer minus the last byte (63 bytes)
        try:
            sent_bytes = self.tcp_socket.send(tx_buffer)
        except socket.error as e:
            print(f"Socket send error: {e}")


        try:
            data = self.tcp_socket.recv(1024)
            if data:
                return data
            time.sleep(1)
        except Exception as e:
            print(f"Error receiving data: {e}")

        return []

    def _decode_rx_buffer(self,  data : bytes, type, sensorids:list) -> list:
        hex_representation = data.hex()

        
        match type:
            case 1:
                sensors = []
                sensorsearch = True
                position = 0
                sensordataelength = (30*4 + 4)
                sensorlength = (len(data))/(sensordataelength)
                if (len(sensorids) != sensorlength):
                    return []
                
                for i in range(round(sensorlength)):

                    sensorbytes = data[sensordataelength*i:sensordataelength*(i+1)]
                    sensor = self._sensor_decode(sensorbytes, sensorids[i])
                    
                    sensors.append(sensor)
                return sensors
            case 2:
                return "two"


    
    def _sensor_decode(self, data: bytes, sensorid):
    
        # Decode the bytes using little-endian byte order
        decoded_value = int.from_bytes( data[0:4], byteorder='little')

        # SE_TYPE__sensor_type_unspecified = 0
        # SE_TYPE__mainmeter = 1
        # SE_TYPE__gasmeter = 2
        # SE_TYPE__pv = 3
        # SE_TYPE__battery = 4
        # SE_TYPE__usage = 5
        # SE_TYPE__charger = 6
        # SE_TYPE__forecast = 7 #not use here
        # SE_TYPE__marketprice = 8 #not use here
        input_reg = None
        match decoded_value:
            case 1:
                input_reg = InputRegMainMeter()
            case 2:
                input_reg = InputRegGasMeter()
            case 3:
                input_reg = InputRegPV()
            case 4:
                input_reg = InputRegBattery()
            case 5:
                input_reg = InputRegUsage()
            case 6:
                input_reg = InputRegCharger()


        input_reg.id = sensorid
        for i in range(30):

            # Decode the bytes using little-endian byte order
            decoded_value = int.from_bytes( data[(i+1)*4:(i+2)*4], byteorder='little')

            # Convert the integer value to a float
            float_value = struct.unpack('f', struct.pack('I', decoded_value))[0]
                        
            setattr(input_reg, input_reg.attributes[i], float_value)

        
        return input_reg

    def _is_connected(self) -> bool:
        try:
            # Check if socket is closed
            self.tcp_socket.getpeername()  # Raises error if not connected
        except socket.error:
            return False
        return True
    
    def _connect(self) -> bool:
        try:
            self.tcp_socket.connect((self.ip_address, self.port))
            print(f"Connected to {self.ip_address} on port {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
        
        return False


    def _close(self):
        print("Closing socket")
        self.tcp_socket.close()






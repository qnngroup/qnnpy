'''
Class [Instrument] provides a base interface for instrument connectivity, but should not be confused with an abstract class.
'''

# Import for Enumated value comparison
from enum import Enum
from functools import total_ordering
from xmlrpc.client import Boolean
from numpy import byte

# For serial communication
import serial


@total_ordering
class DeviceStatus(Enum):
    UNKNOWN = -1
    DISCONNECTED = 0
    CONNECTED = 1
    BUSY = 2

    # Enable comparison of Enum values.
    # Also see https://stackoverflow.com/questions/39268052/how-to-compare-enums-in-python/39268706.
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value

        return NotImplemented


class Instrument:
    # Device status tracker.
    status = DeviceStatus.UNKNOWN
    # Reference to the serial link.
    link = serial.Serial()
    # Transaction termination character.
    termination_character = b'\x0a'
    
    # Method __init__
    # Class constructor. Optional parameters termination_character is a byte representation of the
    # end of line character for serial communication. Typical values are:
    # b'\x0a' -> \n (new line)
    # b'\x0d' -> \r (carriage return)
    def __init__(self, termination_character : byte = b'\x0a', port : str = '' ) -> None:
        print("Opening port "+port)
        self.status = DeviceStatus.UNKNOWN
        self.link = serial.Serial()
        # Default the link timeout to # (s).
        self.link.timeout = 1
        # Automatically connect when a port is provided.
        if(port.startswith('COM')):
            self.connect(port)
        

    # Method connect.
    # Attempt to connect to the physical instrument using port 'COM#'.
    # Returns TRUE on success and FALSE on error.
    def connect(self, port: str) -> Boolean:
        if(self.status < DeviceStatus.CONNECTED):
            try:
                #self.link = self.link.open(port)
                self.link = serial.Serial(port, 9600)
                self.link.timeout = 1
                self.status = DeviceStatus.CONNECTED
                # TODO implement device logging.
                #self.Log("Monochromator CONNECTED to port " + port)
            except:
                # TODO implement device logging.
                #self.Log("Monochromator could not connect to port " + port)
                self.status = DeviceStatus.DISCONNECTED
                return False
            
            # Empty the read buffer.
            self.link.read()
            return True
        else:
            # TODO implement device logging.
            #self.Log("Instrument is already connected.")
            ...
    
    # Method disconnect.
    # Check for an existing connection and close the connection.
    # Returns TRUE on success or when no connection existed, and returns FALSE on failure. 
    def disconnect(self) -> Boolean:
        if(self.status == DeviceStatus.CONNECTED):
            self.link.close()
            return True
        elif(self.status == DeviceStatus.BUSY):
            # Not able to disconnect at this point.
            # TODO implement device logging.
            #self.Log("Device is busy, try again later")
            return False
        elif(self.status < DeviceStatus.CONNECTED):
            # TODO implement device logging.
            #self.Log("Monochromator is not connected.")
            return True
        else:
            self.link.close()
            self.status = DeviceStatus.DISCONNECTED
            # TODO implement device logging.
            #self.Log("Monochromator is successfully disconnected now.")
        return False

    # Method init.
    # Perform a default initialization routine for the device, provided by the command string.
    def init(self, command: str) -> Boolean:
        ...

    # Method write
    # Send a string command to the port. Do not wait for a response.
    def write(self, command: str = ''):
        if(self.status == DeviceStatus.CONNECTED):
            bCommand = bytes(command, 'utf-8') + self.termination_character
            self.link.write(bCommand)
        

    # Set the termination character
    def setTerminationCharacter(self, termination_char: byte) -> None:
        self.termination_character = termination_char
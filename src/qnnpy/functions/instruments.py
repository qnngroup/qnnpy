from functions import ice_get_temp
from typing import List

#######################################################################
#       Instrument Setup
#######################################################################
class Instruments:
    """
    Instruments general setup now supports using multiple of the same instrument.
    Currently duplicate instruments are created by naming the instrument in the
    yaml file as Source1, Source2... and are accessed using instruments(or whatever
    you named your Instruments variable).source1, instuments.source2... If you don't
    postfix your yaml instrument type with a number, it's assumed that only one
    of that instrument is used, and that instrument is accessed normally using
    inst.source (without number).

    """

    attenuator = None
    counter = None
    scope = None
    meter = None
    source = None
    awg = None
    VNA = None
    temp = None

    def __init__(self, properties: dict):
        self.attenuator = None
        self.counter = None
        self.scope = None
        self.meter = None
        self.source = None
        self.awg = None
        self.VNA = None
        self.temp = None
        self.instrument_list: List[str] = []
        self.instrument_dict: dict[str, object] = {}
        # Attenuator
        if properties.get("Attenuator"):
            self.attenuator_setup(properties)
        elif properties.get("Attenuator1"):
            for i in range(
                1, 100
            ):  # if you're using 100 or more attenuators then maybe don't use 100 attenuators? idk man
                if properties.get(f"Attenuator{i}"):
                    self.attenuator_setup(properties, i)
                else:
                    break

        # Counter
        if properties.get("Counter"):
            self.counter_setup(properties)
        elif properties.get("Counter1"):
            for i in range(1, 100):
                if properties.get(f"Counter{i}"):
                    self.counter_setup(properties, i)
                else:
                    break

        # Scope
        if properties.get("Scope"):
            self.scope_setup(properties)
        elif properties.get("Scope1"):
            for i in range(1, 100):
                if properties.get(f"Scope{i}"):
                    self.scope_setup(properties, i)
                else:
                    break

        # Meter
        if properties.get("Meter"):
            self.meter_setup(properties)
        elif properties.get("Meter1"):
            for i in range(1, 100):
                if properties.get(f"Meter{i}"):
                    self.meter_setup(properties, i)
                else:
                    break

        # Source
        if properties.get("Source"):
            self.source_setup(properties)
        elif properties.get("Source1"):
            for i in range(1, 100):
                if properties.get(f"Source{i}"):
                    self.source_setup(properties, i)
                else:
                    break

        # AWG
        if properties.get("AWG"):
            self.AWG_setup(properties)
        elif properties.get("AWG1"):
            for i in range(1, 100):
                if properties.get(f"AWG{i}"):
                    self.AWG_setup(properties, i)
                else:
                    break

        # VNA
        if properties.get("VNA"):
            self.VNA_setup(properties)
        elif properties.get("VNA1"):
            for i in range(1, 100):
                if properties.get(f"VNA{i}"):
                    self.VNA_setup(properties, i)
                else:
                    break

        # Temperature Controller
        if properties.get("Temperature"):
            self.temp_setup(properties)
        elif properties.get("Temperature1"):
            for i in range(1, 100):
                if properties.get(f"Temperature{i}"):
                    self.temp_setup(properties, i)
                else:
                    break
        else:
            properties["Temperature"] = {"initial temp": "None", "name": "None"}

        # SourceMeter
        if properties.get("Sourcemeter"):
            self.sourcemeter_setup(properties)
        elif properties.get("Sourcemeter1"):
            for i in range(1, 100):
                if properties.get(f"Sourcemeter{i}"):
                    self.sourcemeter_setup(properties, i)
                else:
                    break

    def attenuator_setup(self, properties: dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"Attenuator{appender}"
        self.instrument_list.append(inst_name)

        if properties[inst_name]["name"] == "JDSHA9":
            from qnnpy.instruments.jds_ha9 import JDSHA9

            attenuator_class = JDSHA9
        elif properties[inst_name]["name"] == "N7752A":
            from qnnpy.instruments.keysight_n7752a import N7752A

            attenuator_class = N7752A
        else:
            raise NameError("Invalid Attenuator. Attenuator name is not configured")

        try:
            attenuator = attenuator_class(properties[inst_name]["port"])
            attenuator.set_beam_block(True)
            self.instrument_dict[inst_name] = attenuator
            print(f"ATTENUATOR{appender}: connected")
        except Exception:
            print(f"ATTENUATOR{appender}: failed to connect")

        if instrument_num == 0:
            self.attenuator = attenuator
        if instrument_num == 1:
            self.attenuator1 = attenuator
        if instrument_num > 1:
            raise NotImplementedError("More than 2 attenuators not supported yet")

    def counter_setup(self, properties: dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"Counter{appender}"
        self.instrument_list.append(inst_name)

        if properties[f"Counter{appender}"]["name"] == "Agilent53131a":
            from qnnpy.instruments.agilent_53131a import Agilent53131a

            counter_class = Agilent53131a
        elif properties[f"Counter{appender}"]["name"] == "Keysight53230a":
            from qnnpy.instruments.keysight_53230a import Keysight53230a

            counter_class = Keysight53230a
        else:
            raise NameError(
                f"Invalid counter. Counter name {properties[inst_name]['name']} is not configured"
            )

        try:
            counter = counter_class(properties[inst_name]["port"])
            # without the reset command this section will evaluate connected
            # even though the GPIB could be wrong
            # similary story for the other insturments
            counter.reset()
            counter.basic_setup()
            self.instrument_dict[inst_name] = counter
            # self.counter.write(':EVEN:HYST:REL 100')
            print(f"COUNTER{appender}: connected")
        except Exception:
            print(f"COUNTER{appender}: failed to connect")
        if instrument_num == 0:
            self.counter = counter
        if instrument_num == 1:
            self.counter1 = counter
        if instrument_num > 1:
            raise NotImplementedError("More than 2 counters not supported yet")

    def scope_setup(self, properties: dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"Scope{appender}"
        self.instrument_list.append(inst_name)

        if properties[inst_name]["name"] == "LeCroy620Zi":
            from qnnpy.instruments.lecroy_620zi import LeCroy620Zi

            scopeClass = LeCroy620Zi
        elif properties[f"Scope{appender}"]["name"] == "KeysightDSOX":
            from qnnpy.instruments.keysight_dsox import KeysightDSOX

            scopeClass = KeysightDSOX
        else:
            raise NameError("Invalid Scope. Scope name is not configured")

        if properties[inst_name]["port"][0:3] == "USB":
            visa_address = properties[inst_name]["port"]
        else:
            visa_address = f"TCPIP::{properties[inst_name]['port']}::INSTR"

        try:
            scope = scopeClass(visa_address)
            print(f"SCOPE{appender}: connected")
        except Exception:
            print(f"SCOPE{appender}: failed to connect")

        if instrument_num == 0:
            self.scope = scope
            self.scope_channel = properties[inst_name]["channel"]
            self.instrument_dict[inst_name] = scope
        if instrument_num == 1:
            self.scope1 = scope
            self.scope1_channel = properties[inst_name]["channel"]
            self.instrument_dict[inst_name] = scope
        if instrument_num > 1:
            raise NotImplementedError("More than 2 scopes not supported yet")

    def meter_setup(self, properties: dict, instrument_num: int = 0):
        """
        Sets up a meter instrument based on the configuration in properties.

        Args:
            properties: A dictionary containing instrument configuration details.
            instrument_num: An integer specifying the instrument number (optional, defaults to 0).

        Raises:
            NameError: If an invalid meter name is encountered in the configuration.
        """

        appender = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"Meter{appender}"
        self.instrument_list.append(inst_name)

        # Instrument selection and import based on configuration
        meter_name = properties[inst_name]["name"]
        if meter_name == "Keithley2700":
            from qnnpy.instruments.keithley_2700 import Keithley2700

            meter_class = Keithley2700
        elif meter_name == "Keithley2400":
            from qnnpy.instruments.keithley_2400 import Keithley2400

            meter_class = Keithley2400
        elif meter_name == "Keithley2001":
            from qnnpy.instruments.keithley_2001 import Keithley2001

            meter_class = Keithley2001
        else:
            raise NameError(
                f'Invalid Meter. Meter name: "{meter_name}" is not configured'
            )

        # Instrument connection and initialization
        try:
            meter = meter_class(properties[inst_name]["port"])
            meter.reset()  # Assuming reset is a common function for all meters
            self.instrument_dict[inst_name] = meter
            print(f"METER{appender}: connected")
        except Exception as e:
            print(f"METER{appender}: failed to connect ({e})")

        # Assign meter object to class attributes based on instrument number
        if instrument_num == 0:
            self.meter = meter
        elif instrument_num == 1:
            self.meter1 = meter
        else:
            raise NotImplementedError("More than 2 meters not supported yet")

    def source_setup(self, properties: dict, instrument_num: int = 0):
        """
        Sets up a source instrument based on the configuration in properties.

        Args:
            properties: A dictionary containing instrument configuration details.
            instrument_num: An integer specifying the instrument number (optional, defaults to 0).

        Raises:
            NameError: If an invalid source name is encountered in the configuration.
        """

        appender = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"Source{appender}"
        self.instrument_list.append(inst_name)

        # Instrument selection and import based on configuration
        source_name = properties[inst_name]["name"]
        if source_name == "SIM928":
            from qnnpy.instruments.srs_sim928 import SIM928

            source_class = SIM928
        elif source_name == "YokogawaGS200":
            from qnnpy.instruments.yokogawa_gs200 import YokogawaGS200

            source_class = YokogawaGS200
        elif source_name == "Keithley2400":
            from qnnpy.instruments.keithley_2400 import Keithley2400

            source_class = Keithley2400
        else:
            raise NameError(
                f'Invalid Source. Source name: "{source_name}" is not configured'
            )

        # Instrument connection and initialization
        try:
            source = source_class(
                properties[inst_name]["port"],
                properties[inst_name].get("port_alt", None),  # Handle optional port_alt
            )
            source.reset()  # Assuming reset is a common function for all sources
            source.set_output(False)  # Assuming this is a common configuration step
            self.instrument_dict[inst_name] = source
            print(f"SOURCE{appender}: connected")
        except Exception as e:
            print(f"SOURCE{appender}: failed to connect ({e})")

        # Assign source object to class attributes based on instrument number
        if instrument_num == 0:
            self.source = source
        elif instrument_num == 1:
            self.source1 = source
        else:
            raise NotImplementedError("More than 2 sources not supported yet")

    def sourcemeter_setup(self, properties: dict, instrument_num: int = 0):
        """
        Sets up a sourcemeter instrument based on the configuration in properties.

        Args:
            properties: A dictionary containing instrument configuration details.
            instrument_num: An integer specifying the instrument number (optional, defaults to 0).

        Raises:
            NameError: If an invalid sourcemeter name is encountered in the configuration.
        """

        appender = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"Sourcemeter{appender}"
        self.instrument_list.append(inst_name)

        # Instrument selection and import based on configuration
        sourcemeter_name = properties[inst_name]["name"]
        if sourcemeter_name == "KeysightB2912a":
            from qnnpy.instruments.keysight_b2912a import KeysightB2912a

            sourcemeter_class = KeysightB2912a
        else:
            raise NameError(
                f'Invalid Sourcemeter. Sourcemeter name: "{sourcemeter_name}" is not configured'
            )

        # Instrument connection and initialization
        try:
            sourcemeter = sourcemeter_class(properties[inst_name]["port"])
            sourcemeter.reset()  # Assuming reset is a common function for all sourcemeters
            sourcemeter.set_output(
                False
            )  # Assuming this is a common configuration step
            self.instrument_dict[inst_name] = sourcemeter
            print(f"SOURCEMETER{appender}: connected")
        except Exception as e:
            print(f"SOURCEMETER{appender}: failed to connect ({e})")

        # Assign sourcemeter object to class attributes based on instrument number
        if instrument_num == 0:
            self.sourcemeter = sourcemeter
        elif instrument_num == 1:
            self.sourcemeter1 = sourcemeter
        else:
            raise NotImplementedError("More than 2 sourcemeters not supported yet")

    def AWG_setup(self, properties: dict, instrument_num: int = 0):
        """
        Sets up an AWG instrument based on the configuration in properties.

        Args:
            properties: A dictionary containing instrument configuration details.
            instrument_num: An integer specifying the instrument number (optional, defaults to 0).

        Raises:
            NameError: If an invalid AWG name is encountered in the configuration.
            NotImplementedError: If more than 2 AWGs are requested.
        """

        appender = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"AWG{appender}"
        self.instrument_list.append(inst_name)

        # Instrument selection and import based on configuration
        awg_name = properties[inst_name]["name"]
        if awg_name == "Agilent33250a":
            from qnnpy.instruments.agilent_33250a import Agilent33250a

            awg_class = Agilent33250a
        elif awg_name == "Agilent33600a":
            from qnnpy.instruments.agilent_33600a import Agilent33600a

            awg_class = Agilent33600a
        else:
            raise NameError(
                f"Invalid AWG. AWG name: {properties[inst_name]['name']} is not configured"
            )

        # Instrument connection and initialization
        try:
            awg = awg_class(properties[inst_name]["port"])
            awg.beep()  # Assuming beep is a common function for all AWGs
            print(f"AWG{appender}: connected")
            self.instrument_dict[inst_name] = awg
            if instrument_num == 0:
                self.awg = awg
            elif instrument_num == 1:
                self.awg1 = awg
            else:
                raise NotImplementedError("More than 2 AWGs not supported yet")
        except Exception as e:
            print(f"AWG{appender}: failed to connect ({e})")

    # VNA
    def VNA_setup(self, properties: dict, instrument_num: int = 0):
        """
        Sets up a VNA instrument based on the configuration in properties.

        Args:
            properties: A dictionary containing instrument configuration details.
            instrument_num: An integer specifying the instrument number (optional, defaults to 0).

        Raises:
            NameError: If an invalid VNA name is encountered in the configuration.
        """

        appender = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"VNA{appender}"
        self.instrument_list.append(inst_name)

        # Instrument selection and import based on configuration
        vna_name = properties[inst_name]["name"]
        if vna_name == "KeysightN5224a":
            from qnnpy.instruments.keysight_n5224a import KeysightN5224a

            vna_class = KeysightN5224a
        else:
            raise NameError(
                f"Invalid VNA. VNA name: {properties[inst_name]['name']} is not configured"
            )

        # Instrument connection and initialization
        try:
            vna = vna_class(properties[inst_name]["port"])
            # Assuming reset is a common function for all VNAs, uncomment if needed
            # vna.reset()
            self.instrument_dict[inst_name] = vna
            print(f"VNA{appender}: connected")
        except Exception as e:
            print(f"VNA{appender}: failed to connect ({e})")

        if instrument_num == 0:
            self.VNA = vna
        if instrument_num > 0:
            raise NotImplementedError("More than 1 VNA not supported yet")

    # Temperature Controller
    def temp_setup(self, properties: dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num == 0:
            appender = ""
        inst_name = f"Temperature{appender}"
        self.instrument_list.append(inst_name)

        if properties[inst_name]["name"] == "Lakeshore336":
            from qnnpy.instruments.lakeshore336 import Lakeshore336

            temp_class = Lakeshore336
        elif properties[inst_name]["name"] == "Cryocon34":
            from qnnpy.instruments.cryocon34 import Cryocon34

            temp_class = Cryocon34
        elif properties[inst_name]["name"] == "ICE":
            temp_class = None
        elif properties[inst_name]["name"] == "DEWAR":
            temp_class = None
        else:
            raise NameError(
                'Invalid Temperature Controller. TEMP name: "%s" is not configured'
                % properties[inst_name]["name"]
            )

        if temp_class is not None:
            try:
                temp = temp_class(properties[inst_name]["port"])
                temp.channel = properties[inst_name]["channel"]
                properties[inst_name]["initial temp"] = temp.read_temp(
                    temp.channel
                )  # Assuming read_temp is a common function for all temperature controllers
                self.instrument_dict[inst_name] = temp
                print(
                    "TEMPERATURE"
                    + appender
                    + ": connected | "
                    + str(properties[inst_name]["initial temp"])
                )
            except Exception as e:
                properties[inst_name]["initial temp"] = 0
                print(f"TEMPERATURE{appender} failed to connect with message ({e})")
        else:
            if properties[inst_name]["name"] == "ICE":
                temp = None
                try:
                    properties["Temperature" + appender]["initial temp"] = ice_get_temp(
                        select=1
                    )
                    print(
                        "TEMPERATURE"
                        + appender
                        + ": connected T="
                        + str(ice_get_temp(select=1))
                    )
                except Exception:
                    properties["Temperature" + appender]["initial temp"] = 0
                    print("TEMPERATURE" + appender + ": failed to connect")
            if properties[inst_name]["name"] == "DEWAR":
                temp = None
                try:
                    properties["Temperature" + appender]["initial temp"] = 4.2
                    print("TEMPERATURE" + appender + ": ~connected~ 4.2K")
                except Exception:
                    properties["Temperature" + appender]["initial temp"] = 0
                    print("TEMPERATURE" + appender + ": failed to connect")

        if instrument_num == 0:
            self.temp = temp
        if instrument_num > 0:
            raise NotImplementedError(
                "More than 1 temperature controller not supported yet"
            )
        
from abc import ABCMeta
        
class Instrument(object):
    '''
    This implements several generic functions that should always be available
    in instruments
    '''
    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)
    
class AWG(metaclass=ABCMeta):
    '''
    This defines an interface of functions that must be implemented in
    any Source subclasses. Failure to implement will result in a TypeError
    on instatiation
    '''
    def __init__(self, port):
        pass 
    
    def reset(self):
        pass
    
class Source(metaclass=ABCMeta):
    '''
    This defines an interface of functions that must be implemented in
    any Source subclasses. Failure to implement will result in a TypeError
    on instatiation
    '''
    def __init__(self, port, port_alt=None):
        pass 

    def reset(self):
        pass 

    def set_voltage(self, voltage=0.0):
        pass

    def set_output(self, output=False):
        pass

class SourceMeter(metaclass=ABCMeta):
    '''
    This defines an interface of functions that must be implemented in
    any Source subclasses. Failure to implement will result in a TypeError
    on instatiation
    '''
    def __init__(self, port):
        pass 

    def reset(self):
        pass
import array as arr
import logging
import re
import struct
from collections import abc, defaultdict
from functools import partial
from io import BytesIO
from time import localtime, sleep
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple, Union, cast

import numpy as np
from pyvisa.errors import VisaIOError
from qcodes import VisaInstrument
from qcodes import validators as vals

# conditionally import lomentum for support of lomentum type sequences
try:
    from lomentum.tools import get_element_channel_ids, is_subsequence

    USE_LOMENTUM = True
except ImportError:
    USE_LOMENTUM = False

log = logging.getLogger(__name__)


class _MarkerDescriptor(NamedTuple):
    marker: int
    channel: int


def parsestr(v: str) -> str:
    return v.strip().strip('"')


class BK4060_AWG(VisaInstrument):
    """
    This is the QCoDeS driver for the Tektronix AWG5014
    Arbitrary Waveform Generator.

    The driver makes some assumptions on the settings of the instrument:

        - The output channels are always in Amplitude/Offset mode
        - The output markers are always in High/Low mode
    """

    # BSMV_parameters=['C1:BSWV WVTP', 'FRQ', 'PERI', 'AMP', 'AMPVRMS', 'MAX_OUTPUT_AMP', 'OFST', 'HLEV', 'LLEV', 'PHSE', 'DUTY',
    #                 'STATE', 'TIME', 'DLAY', 'TRSR', 'EDGE', 'CARR,WVTP', 'CARR,FREQ', 'CARR,AMP', 'CARR,OFST', 'CARR,PHSE', 'CARR,DUTY']
    parameter_name_command: Dict[str, str] = {
        "waveform": "WVTP",
        "frequency": "FRQ",
        "period": "PERI",
        "amplitude": "AMP",
        "max_out_amp": "MAX_OUTPUT_AMP",
        "offset": "OFST",
        "phase": "PHSE",
        "high_level": "HLEV",
        "low_level": "LLEV",
        "duty_cycle": "DUTY",
        "state": "STATE",
        "cycle": "TIME",
        "bperiod": "PRD",
        "delay": "DLAY",
        "symmetry": "SYM",
        "trigger": "TRSR",
        "edge": "EDGE",
        "carrier_wave": "CARR,WVTP",
        "carrier_freq": "CARR,FREQ",
        "carrier_amp": "CARR,AMP",
        "carrier_offset": "CARR,OFST",
        "carrier_phase": "CARR,PHSE",
        "carrier_duty": "CARR,DUTY",
    }
    AWG_FILE_FORMAT_HEAD = {
        "SAMPLING_RATE": "d",  # d
        "REPETITION_RATE": "d",  # # NAME?
        "HOLD_REPETITION_RATE": "h",  # True | False
        "CLOCK_SOURCE": "h",  # Internal | External
        "REFERENCE_SOURCE": "h",  # Internal | External
        "EXTERNAL_REFERENCE_TYPE": "h",  # Fixed | Variable
        "REFERENCE_CLOCK_FREQUENCY_SELECTION": "h",
        "REFERENCE_MULTIPLIER_RATE": "h",  #
        "DIVIDER_RATE": "h",  # 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256
        "TRIGGER_SOURCE": "h",  # Internal | External
        "INTERNAL_TRIGGER_RATE": "d",  #
        "TRIGGER_INPUT_IMPEDANCE": "h",  # 50 ohm | 1 kohm
        "TRIGGER_INPUT_SLOPE": "h",  # Positive | Negative
        "TRIGGER_INPUT_POLARITY": "h",  # Positive | Negative
        "TRIGGER_INPUT_THRESHOLD": "d",  #
        "JUMP_TIMING": "h",  # Sync | Async
        "INTERLEAVE": "h",  # On |  This setting is stronger than .
        "ZEROING": "h",  # On | Off
        "COUPLING": "h",  # The Off | Pair | All setting is weaker than .
        "RUN_MODE": "h",  # Continuous | Triggered | Gated | Sequence
        "WAIT_VALUE": "h",  # First | Last
        "RUN_STATE": "h",  # On | Off
        "INTERLEAVE_ADJ_PHASE": "d",
        "INTERLEAVE_ADJ_AMPLITUDE": "d",
    }
    AWG_FILE_FORMAT_CHANNEL = {
        # Include NULL.(Output Waveform Name for Non-Sequence mode)
        "OUTPUT_WAVEFORM_NAME_N": "s",
        "CHANNEL_STATE_N": "h",  # On | Off
        "ANALOG_DIRECT_OUTPUT_N": "h",  # On | Off
        "ANALOG_FILTER_N": "h",  # Enum type.
        "ANALOG_METHOD_N": "h",  # Amplitude/Offset, High/Low
        # When the Input Method is High/Low, it is skipped.
        "ANALOG_AMPLITUDE_N": "d",
        # When the Input Method is High/Low, it is skipped.
        "ANALOG_OFFSET_N": "d",
        # When the Input Method is Amplitude/Offset, it is skipped.
        "ANALOG_HIGH_N": "d",
        # When the Input Method is Amplitude/Offset, it is skipped.
        "ANALOG_LOW_N": "d",
        "DIGITAL_METHOD_N": "h",  # Amplitude/Offset, High/Low
        # When the Input Method is High/Low, it is skipped.
        "DIGITAL_AMPLITUDE_N": "d",
        # When the Input Method is High/Low, it is skipped.
        "DIGITAL_OFFSET_N": "d",
        # When the Input Method is Amplitude/Offset, it is skipped.
        "DIGITAL_HIGH_N": "d",
        # When the Input Method is Amplitude/Offset, it is skipped.
        "DIGITAL_LOW_N": "d",
        "EXTERNAL_ADD_N": "h",  # AWG5000 only
        "PHASE_DELAY_INPUT_METHOD_N": "h",  # Phase/DelayInme/DelayInints
        "PHASE_N": "d",  # When the Input Method is not Phase, it is skipped.
        # When the Input Method is not DelayInTime, it is skipped.
        "DELAY_IN_TIME_N": "d",
        # When the Input Method is not DelayInPoint, it is skipped.
        "DELAY_IN_POINTS_N": "d",
        "CHANNEL_SKEW_N": "d",
        "DC_OUTPUT_LEVEL_N": "d",  # V
    }

    def __init__(
        self,
        name: str,
        address: str,
        timeout: int = 180,
        num_channels: int = 2,
        **kwargs: Any,
    ):
        # Sanity Check inputs
        # if name not in ['ch1', 'ch2', 'ch3']:
        #     raise ValueError("Invalid Channel: {}, expected 'ch1' or 'ch2' or 'ch3'"
        #                      .format(name))
        # if chan not in [1, 2, 3]:
        #     raise ValueError("Invalid Channel: {}, expected '1' or '2' or '3'"
        #                      .format(chan))
        """
        Initializes the BK4060.

        Args:
            name: name of the instrument
            address: GPIB or ethernet address as used by VISA
            timeout: visa timeout, in secs. long default (180)
                to accommodate large waveforms
            num_channels: number of channels on the device
            device_clear must be False or it will give error 1073807360,
            this awg cannot be cleared buffered SCPI comments.

        """
        super().__init__(name, address, timeout=timeout, device_clear=False, **kwargs)

        self._address = address
        self.num_channels = num_channels

        self._values: Dict[
            str, Dict[str, Dict[str, Union[np.ndarray, float, None]]]
        ] = {}
        self._values["files"] = {}

        self.add_function("reset", call_cmd="*RST")

        self.add_parameter(
            "clock_source",
            label="Clock source",
            get_cmd="ROSCillator?",
            set_cmd="ROSCillator, " + "{}",
            vals=vals.Enum("INT", "EXT"),
            get_parser=self.newlinestripper,
        )

        # # sequence parameter(s)
        # self.add_parameter('sequence_length',
        #                    label='Sequence length',
        #                    get_cmd='SEQuence:LENGth?',
        #                    set_cmd='SEQuence:LENGth ' + '{}',
        #                    get_parser=int,
        #                    vals=vals.Ints(0, 8000),
        #                    docstring=(
        #                        """
        #                        This command sets the sequence length.
        #                        Use this command to create an
        #                        uninitialized sequence. You can also
        #                        use the command to clear all sequence
        #                        elements in a single action by passing
        #                        0 as the parameter. However, this
        #                        action cannot be undone so exercise
        #                        necessary caution. Also note that
        #                        passing a value less than the
        #                        sequence’s current length will cause
        #                        some sequence elements to be deleted at
        #                        the end of the sequence. For example if
        #                        self.get_sq_length returns 200 and you
        #                        subsequently set sequence_length to 21,
        #                        all sequence elements except the first
        #                        20 will be deleted.
        #                        """)
        #                    )
        #
        # self.add_parameter('sequence_pos',
        #                    label='Sequence position',
        #                    get_cmd='AWGControl:SEQuencer:POSition?',
        #                    set_cmd='SEQuence:JUMP:IMMediate {}',
        #                    vals=vals.PermissiveInts(1),
        #                    set_parser=lambda x: int(round(x))
        #                    )

        # Channel parameters #

        for i in range(1, self.num_channels + 1):
            output_state_cmd = f"C{i}:OUTP"
            waveform_cmd = f"C{i}:BSWV WVTP"
            # amp_cmd = f'C{i}:BSWV AMP'
            # freq_cmd = f'C{i}:BSWV FRQ'
            # offset_cmd = f'C{i}:VOLTage:LEVel:IMMediate:OFFS'
            # directoutput_cmd = f'AWGControl:DOUTput{i}:STATE'
            # filter_cmd = f'OUTPut{i}:FILTer:FREQuency'
            # add_input_cmd = f'SOURce{i}:COMBine:FEED'
            # dc_out_cmd = f'AWGControl:DC{i}:VOLTage:OFFSet'

            # Set channel first to ensure sensible sorting of pars
            self.add_parameter(
                f"ch{i}_state",
                label=f"Output state channel {i}",
                get_cmd=f"C{i}:OUTP?",
                set_cmd=f"C{i}:OUTP" + " {:s}",
                # val_mapping=create_on_off_val_mapping(on_val=f'C{i}:OUTP ON,LOAD,HZ,PLRT,NOR\n', off_val=f"C{i}:OUTP OFF,LOAD,HZ,PLRT,NOR\n"),
            )

            self.add_parameter(
                f"ch{i}_amp",
                label=f"AWG Ch{i} Amplitude",
                unit="Vpp",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["amplitude"]
                + ", {:.6f}"
                + "V",
                vals=vals.Numbers(0.001, 10),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["amplitude"],
                ),
            )

            self.add_parameter(
                f"ch{i}_freq",
                label=f"AWG Ch{i} Frequency",
                unit="Hz",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["frequency"]
                + ", {:.6f}"
                + "HZ",
                vals=vals.Numbers(1e-6, 120e6),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["frequency"],
                ),
            )

            self.add_parameter(
                f"ch{i}_offset",
                label=f"AWG Ch{i} Offset",
                unit="V",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["offset"]
                + ", {:.6f}"
                + "V",
                vals=vals.Numbers(-10, 10),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["offset"],
                ),
            )

            self.add_parameter(
                f"ch{i}_high_level",
                label=f"AWG Ch{i} High Level",
                unit="V",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["high_level"]
                + ", {:.6f}"
                + "V",
                vals=vals.Numbers(-10, 10),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["high_level"],
                ),
            )

            self.add_parameter(
                f"ch{i}_low_level",
                label=f"AWG Ch{i} Low Level",
                unit="V",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["low_level"]
                + ", {:.6f}"
                + "V",
                vals=vals.Numbers(-10, 10),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["low_level"],
                ),
            )

            # self.add_parameter(f'ch{i}_period',
            #                    label=f'AWG Ch{i} Period',
            #                    unit='s',
            #                    get_cmd=f'C{i}:BSWV?',
            #                    get_parser=partial(self._get_BSWV_parser, key_extract = self.parameter_name_command['period'])
            #                    )

            self.add_parameter(
                f"ch{i}_waveform",
                label=f"AWG Ch{i} Waveform",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=waveform_cmd + ", {}",
                vals=vals.Strings(),
                get_parser=partial(self._get_BSWV_parser, key_extract=waveform_cmd),
            )

            self.add_parameter(
                f"ch{i}_phase",
                label=f"AWG Ch{i} Phase",
                unit="degree",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["phase"]
                + ", {:.3f}",
                vals=vals.Numbers(-360, 360),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["phase"],
                ),
            )

            self.add_parameter(
                f"ch{i}_duty",
                label=f"AWG Ch{i} Duty",
                unit="percent",
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["duty_cycle"]
                + ", {:.3f}",
                vals=vals.Numbers(1, 99),  # waveform_SQUARE, duty is 20-80%
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["duty_cycle"],
                ),
            )

            self.add_parameter(
                f"ch{i}_symmetry",
                label=f"AWG Ch{i} Symmetry",  # waveform_RAMP
                unit=None,
                get_cmd=f"C{i}:BSWV?",
                set_cmd=f"C{i}:BSWV "
                + self.parameter_name_command["symmetry"]
                + ", {:.3f}",
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["symmetry"],
                ),
            )
            # Burst Wave Command
            self.add_parameter(
                f"ch{i}_burst",
                label=f"Ch{i} Burst State",
                get_cmd=f"C{i}:BTWV?",
                set_cmd=f"C{i}:BTWV " + self.parameter_name_command["state"] + ", {:s}",
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=f"C{i}:BTWV " + self.parameter_name_command["state"],
                ),
            )

            self.add_parameter(
                f"ch{i}_burst_cycle",
                label=f"AWG Ch{i} Burst Cycle",
                get_cmd=f"C{i}:BTWV?",
                set_cmd=f"C{i}:BTWV "
                + self.parameter_name_command["cycle"]
                + ", {:.3f}",
                vals=vals.Numbers(1, 1e6),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["cycle"],
                ),
            )

            self.add_parameter(
                f"ch{i}_burst_period",
                label=f"AWG Ch{i} Burst Period",
                unit="seconds",
                get_cmd=f"C{i}:BTWV?",
                set_cmd=f"C{i}:BTWV "
                + self.parameter_name_command["bperiod"]
                + ", {:.3f}"
                + "S",
                vals=vals.Numbers(1e-9, 20),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["bperiod"],
                ),
            )

            self.add_parameter(
                f"ch{i}_trigger",
                label=f"Ch{i} Trigger",
                get_cmd=f"C{i}:BTWV?",
                set_cmd=f"C{i}:BTWV "
                + self.parameter_name_command["trigger"]
                + ", {:s}",
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["trigger"],
                ),
            )

            self.add_parameter(
                f"ch{i}_trigger_edge",
                label=f"Ch{i} Trigger EDGE",
                get_cmd=f"C{i}:BTWV?",
                set_cmd=f"C{i}:BTWV " + self.parameter_name_command["edge"] + ", {:s}",
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["edge"],
                ),
            )

            self.add_parameter(
                f"ch{i}_trigger_delay",
                label=f"AWG Ch{i} Trigger Delay",
                unit="seconds",
                get_cmd=f"C{i}:BTWV?",
                set_cmd=f"C{i}:BTWV "
                + self.parameter_name_command["delay"]
                + ", {:.3f}"
                + "S",
                vals=vals.Numbers(0, 500),
                get_parser=partial(
                    self._get_BSWV_parser,
                    key_extract=self.parameter_name_command["delay"],
                ),
            )

            # self.add_parameter(f'ch{i}_carrier_wave',
            #                     label=f'Ch{i} Carrier Wave',
            #                     get_cmd=f'C{i}:BTWV?',
            #                     set_cmd=f'C{i}:BTWV '+ self.parameter_name_command['carrier_wave'] + ', {:s}',
            #                     get_parser=partial(self._get_BSWV_parser, key_extract = self.parameter_name_command['carrier_wave'])
            #                     )

            # self.add_parameter(f'ch{i}_direct_output',
            #                    label=f'Direct output channel {i}',
            #                    get_cmd=directoutput_cmd + '?',
            #                    set_cmd=directoutput_cmd + ' {}',
            #                    vals=vals.Ints(0, 1))
            # self.add_parameter(f'ch{i}_add_input',
            #                    label='Add input channel {}',
            #                    get_cmd=add_input_cmd + '?',
            #                    set_cmd=add_input_cmd + ' {}',
            #                    vals=vals.Enum('"ESIG"', '"ESIGnal"', '""'),
            #                    get_parser=self.newlinestripper)
            # self.add_parameter(f'ch{i}_filter',
            #                    label=f'Low pass filter channel {i}',
            #                    unit='Hz',
            #                    get_cmd=filter_cmd + '?',
            #                    set_cmd=filter_cmd + ' {}',
            #                    vals=vals.Enum(20e6, 100e6,
            #                                   float('inf'),
            #                                   'INF', 'INFinity'),
            #                    get_parser=self._tek_outofrange_get_parser)
            # self.add_parameter(f'ch{i}_DC_out',
            #                    label=f'DC output level channel {i}',
            #                    unit='V',
            #                    get_cmd=dc_out_cmd + '?',
            #                    set_cmd=dc_out_cmd + ' {}',
            #                    vals=vals.Numbers(-3, 5),
            #                    get_parser=float)

        self.connect_message()

    # Convenience parser
    def newlinestripper(self, string: str) -> str:
        if string.endswith("\n"):
            return string[:-1]
        else:
            return string

    def _tek_outofrange_get_parser(self, string: str) -> float:
        val = float(string)
        # note that 9.9e37 is used as a generic out of range value
        # in tektronix instruments
        if val >= 9.9e37:
            val = float("INF")
        return val

    # def _get_BSWV_parser(self, response: str, **kwargs) -> str:
    #     '''
    #     Parameters
    #     ----------
    #     response : str
    #         string to be read from instrument.
    #         typical response:
    #     C1:BSWV WVTP,SINE,FRQ,1000HZ,PERI,0.001S,AMP,4V,AMPVRMS,1.414Vrms,MAX_OUTPUT_AMP,20V,OFST,0V,HLEV,2V,LLEV,-2V,PHSE,0
    #     Returns
    #     -------
    #     str
    #         DESCRIPTION.

    #     '''
    #     # print(response)    ###
    #     # print(key_extract)
    #     # response=response[0:len(response-2)]
    #     str_list=response.split(',')
    #     # str_list[-1]=
    #     # print(str_list)    ###
    #     # print(str_list[-1])
    #     temp=[]
    #     # print(len(str_list))

    #     for i in range(len(str_list)):
    #         if (i%2)==0:
    #             temp+=[str_list[i]+'='+str_list[i+1]]

    #     resp=dict(item.split('=') for item in temp)

    #     if kwargs['key_extract']:
    #         key_use=kwargs['key_extract']
    #     return_value=[]

    #     if key_use in resp.keys():
    #         return_value=resp[key_use]
    #         if(key_use == 'DUTY'):
    #             return_value = float(return_value)
    #     else:
    #         return_value='No Value'
    #         # print(key_use+' has no value because it is not associated with this waveform')
    #     return return_value

    def _get_BSWV_parser(self, response: str, **kwargs) -> str:
        """
        Parameters
        ----------
        response : str
            string to be read from instrument.
            typical response:
        C1:BSWV WVTP,SINE,FRQ,1000HZ,PERI,0.001S,AMP,4V,AMPVRMS,1.414Vrms,MAX_OUTPUT_AMP,20V,OFST,0V,HLEV,2V,LLEV,-2V,PHSE,0
        Returns
        -------
        str
            DESCRIPTION.

        """
        str_list = response.split(",")
        temp = []
        k1 = 0
        for i in range(0, len(str_list), 2):
            if str_list[i] == "CARR":
                k1 = -1
            else:
                str_list[i + k1] = str_list[i + k1].strip()
                str_list[i + k1 + 1] = str_list[i + k1 + 1].strip()
                temp += [str_list[i + k1] + "=" + str_list[i + k1 + 1]]

        resp = dict(item.split("=") for item in temp)
        if kwargs["key_extract"]:
            key_use = kwargs["key_extract"]
        return_value = []

        if key_use in resp.keys():
            return_value = resp[key_use]
        else:
            return_value = "Not Set"
            # print(key_use+' has no value because it is not associated with this waveform')
        return return_value

    # Functions
    def start(self) -> str:
        """Convenience function, identical to self.run()"""
        return self.run()

    def run(self) -> str:
        """
        This command initiates the output of a waveform or a sequence.
        This is equivalent to pressing Run/Stop button on the front panel.
        The instrument can be put in the run state only when output waveforms
        are assigned to channels.

        Returns:
            The output of self.get_state()
        """
        self.write("AWGControl:RUN")
        # return self.get_state()

    def stop(self) -> None:
        """This command stops the output of a waveform or a sequence."""
        self.write("AWGControl:STOP")

    def get_folder_contents(self, print_contents: bool = True) -> str:
        """
        This query returns the current contents and state of the mass storage
        media (on the AWG Windows machine).

        Args:
            print_contents: If True, the folder name and the query
                output are printed. Default: True.

        Returns:
            str: A comma-seperated string of the folder contents.
        """
        contents = self.ask("MMEMory:CATalog?")
        if print_contents:
            print("Current folder:", self.get_current_folder_name())
            print(
                contents.replace(',"$', "\n$").replace('","', "\n").replace(",", "\t")
            )
        return contents

    def get_current_folder_name(self) -> str:
        """
        This query returns the current directory of the file system on the
        arbitrary waveform generator. The current directory for the
        programmatic interface is different from the currently selected
        directory in the Windows Explorer on the instrument.

        Returns:
            A string with the full path of the current folder.
        """
        return self.ask("MMEMory:CDIRectory?")

    def set_current_folder_name(self, file_path: str) -> int:
        """
        Set the current directory of the file system on the arbitrary
        waveform generator. The current directory for the programmatic
        interface is different from the currently selected directory in the
        Windows Explorer on the instrument.

        Args:
            file_path: The full path.

        Returns:
            The number of bytes written to instrument
        """
        writecmd = 'MMEMory:CDIRectory "{}"'
        return self.visa_handle.write(writecmd.format(file_path))

    def change_folder(self, folder: str) -> int:
        """Duplicate of self.set_current_folder_name"""
        writecmd = r'MMEMory:CDIRectory "{}"'
        return self.visa_handle.write(writecmd.format(folder))

    def goto_root(self) -> None:
        """
        Set the current directory of the file system on the arbitrary
        waveform generator to C: (the 'root' location in Windows).
        """
        self.write('MMEMory:CDIRectory "c:\\.."')

    def create_and_goto_dir(self, folder: str) -> str:
        """
        Set the current directory of the file system on the arbitrary
        waveform generator. Creates the directory if if doesn't exist.
        Queries the resulting folder for its contents.

        Args:
            folder: The path of the directory to set as current.
                Note: this function expects only root level directories.

        Returns:
            A comma-seperated string of the folder contents.
        """

        dircheck = "%s, DIR" % folder
        if dircheck in self.get_folder_contents():
            self.change_folder(folder)
            log.debug("Directory already exists")
            log.warning(
                ("Directory already exists, " + "changed path to {}").format(folder)
            )
            log.info("Contents of folder is " + "{}".format(self.ask("MMEMory:cat?")))
        elif self.get_current_folder_name() == f'"\\{folder}"':
            log.info("Directory already set to " + f"{folder}")
        else:
            self.write('MMEMory:MDIRectory "%s"' % folder)
            self.write('MMEMory:CDIRectory "%s"' % folder)

        return self.get_folder_contents()

    def all_channels_on(self) -> None:
        """
        Set the state of all channels to be ON. Note: only channels with
        defined waveforms can be ON.
        """
        for i in range(1, self.num_channels + 1):
            self.set(f"ch{i}_state", 1)

    def all_channels_off(self) -> None:
        """Set the state of all channels to be OFF."""
        for i in range(1, self.num_channels + 1):
            self.set(f"ch{i}_state", 0)

    #####################
    # Sequences section #
    #####################

    def set_sqel_event_target_index(self, element_no: int, index: int) -> None:
        """
        This command sets the target index for
        the sequencer’s event jump operation. Note that this will take
        effect only when the event jump target type is set to
        INDEX.

        Args:
            element_no: The sequence element number
            index: The index to set the target to
        """
        self.write("SEQuence:" + f"ELEMent{element_no}:JTARGet:INDex {index}")

    def set_sqel_goto_target_index(
        self, element_no: int, goto_to_index_no: int
    ) -> None:
        """
        This command sets the target index for the GOTO command of the
        sequencer.  After generating the waveform specified in a
        sequence element, the sequencer jumps to the element specified
        as GOTO target. This is an unconditional jump. If GOTO target
        is not specified, the sequencer simply moves on to the next
        element. If the Loop Count is Infinite, the GOTO target which
        is specified in the element is not used. For this command to
        work, the goto state of the squencer must be ON and the
        sequence element must exist.
        Note that the first element of a sequence is taken to be 1 not 0.


        Args:
            element_no: The sequence element number
            goto_to_index_no: The target index number

        """
        self.write(
            "SEQuence:" + "ELEMent{}:GOTO:INDex {}".format(element_no, goto_to_index_no)
        )

    def set_sqel_goto_state(self, element_no: int, goto_state: int) -> None:
        """
        This command sets the GOTO state of the sequencer for the specified
        sequence element.

        Args:
            element_no: The sequence element number
            goto_state: The GOTO state of the sequencer. Must be either
                0 (OFF) or 1 (ON).
        """
        allowed_states = [0, 1]
        if goto_state not in allowed_states:
            log.warning(
                (
                    "{} not recognized as a valid goto" + " state. Setting to 0 (OFF)."
                ).format(goto_state)
            )
            goto_state = 0
        self.write(
            "SEQuence:ELEMent{}:GOTO:STATe {}".format(element_no, int(goto_state))
        )

    def set_sqel_loopcnt_to_inf(self, element_no: int, state: int = 1) -> None:
        """
        This command sets the infinite looping state for a sequence
        element. When an infinite loop is set on an element, the
        sequencer continuously executes that element. To break the
        infinite loop, issue self.stop()

        Args:
            element_no (int): The sequence element number
            state (int): The infinite loop state. Must be either 0 (OFF) or
                1 (ON).
        """
        allowed_states = [0, 1]
        if state not in allowed_states:
            log.warning(
                (
                    "{} not recognized as a valid loop" + "  state. Setting to 0 (OFF)."
                ).format(state)
            )
            state = 0

        self.write("SEQuence:ELEMent{}:LOOP:INFinite {}".format(element_no, int(state)))

    def get_sqel_loopcnt(self, element_no: int = 1) -> str:
        """
        This query returns the loop count (number of repetitions) of a
        sequence element. Loop count setting for an element is ignored
        if the infinite looping state is set to ON.

        Args:
            element_no: The sequence element number. Default: 1.
        """
        return self.ask(f"SEQuence:ELEMent{element_no}:LOOP:COUNt?")

    def set_sqel_loopcnt(self, loopcount: int, element_no: int = 1) -> None:
        """
        This command sets the loop count. Loop count setting for an
        element is ignored if the infinite looping state is set to ON.

        Args:
            loopcount: The number of times the sequence is being output.
                The maximal possible number is 65536, beyond that: infinity.
            element_no: The sequence element number. Default: 1.
        """
        self.write("SEQuence:ELEMent{}:LOOP:COUNt {}".format(element_no, loopcount))

    def set_sqel_waveform(
        self, waveform_name: str, channel: int, element_no: int = 1
    ) -> None:
        """
        This command sets the waveform for a sequence element on the specified
        channel.

        Args:
            waveform_name: Name of the waveform. Must be in the waveform
                list (either User Defined or Predefined).
            channel: The output channel (1-4)
            element_no: The sequence element number. Default: 1.
        """
        self.write(
            'SEQuence:ELEMent{}:WAVeform{} "{}"'.format(
                element_no, channel, waveform_name
            )
        )

    def get_sqel_waveform(self, channel: int, element_no: int = 1) -> str:
        """
        This query returns the waveform for a sequence element on the
        specified channel.

        Args:
            channel: The output channel (1-4)
            element_no: The sequence element number. Default: 1.

        Returns:
            The name of the waveform.
        """
        return self.ask("SEQuence:ELEMent{}:WAVeform{}?".format(element_no, channel))

    def set_sqel_event_jump_target_index(
        self, element_no: int, jtar_index_no: int
    ) -> None:
        """Duplicate of set_sqel_event_target_index"""
        self.write(
            "SEQuence:ELEMent{}:JTARget:INDex {}".format(element_no, jtar_index_no)
        )

    def set_sqel_event_jump_type(self, element_no: int, jtar_state: str) -> None:
        """
        This command sets the event jump target type for the jump for
        the specified sequence element.  Generate an event in one of
        the following ways:

        * By connecting an external cable to instrument rear panel
          for external event.
        * By pressing the Force Event button on the
          front panel.
        * By using self.force_event

        Args:
            element_no: The sequence element number
            jtar_state: The jump target type. Must be either 'INDEX',
                'NEXT', or 'OFF'.
        """
        self.write("SEQuence:ELEMent{}:JTARget:TYPE {}".format(element_no, jtar_state))

    def get_sq_mode(self) -> str:
        """
        This query returns the type of the arbitrary waveform
        generator's sequencer. The sequence is executed by the
        hardware sequencer whenever possible.

        Returns:
            str: Either 'HARD' or 'SOFT' indicating that the instrument is in\
              either hardware or software sequencer mode.
        """
        return self.ask("AWGControl:SEQuence:TYPE?")

    ######################
    # AWG file functions #
    ######################

    def _pack_record(
        self, name: str, value: Union[float, str, Sequence[Any], np.ndarray], dtype: str
    ) -> bytes:
        """
        packs awg_file record into a struct in the folowing way:
            struct.pack(fmtstring, namesize, datasize, name, data)
        where fmtstring = '<IIs"dtype"'

        The file record format is as follows:
        Record Name Size:        (32-bit unsigned integer)
        Record Data Size:        (32-bit unsigned integer)
        Record Name:             (ASCII) (Include NULL.)
        Record Data
        For details see "File and Record Format" in the AWG help

        < denotes little-endian encoding, I and other dtypes are format
        characters denoted in the documentation of the struct package

        Args:
            name: Name of the record (Example: 'MAGIC' or 'SAMPLING_RATE')
            value: The value of that record.
            dtype: String specifying the data type of the record.
                Allowed values: 'h', 'd', 's'.
        """
        if len(dtype) == 1:
            record_data = struct.pack("<" + dtype, value)
        else:
            if dtype[-1] == "s":
                assert isinstance(value, str)
                record_data = value.encode("ASCII")
            else:
                assert isinstance(value, (abc.Sequence, np.ndarray))
                if dtype[-1] == "H" and isinstance(value, np.ndarray):
                    # numpy conversion is fast
                    record_data = value.astype("<u2").tobytes()
                else:
                    # argument unpacking is slow
                    record_data = struct.pack("<" + dtype, *value)

        # the zero byte at the end the record name is the "(Include NULL.)"
        record_name = name.encode("ASCII") + b"\x00"
        record_name_size = len(record_name)
        record_data_size = len(record_data)
        size_struct = struct.pack("<II", record_name_size, record_data_size)
        packed_record = size_struct + record_name + record_data

        return packed_record

    def generate_sequence_cfg(self) -> Dict[str, float]:
        """
        This function is used to generate a config file, that is used when
        generating sequence files, from existing settings in the awg.
        Querying the AWG for these settings takes ~0.7 seconds
        """
        log.info("Generating sequence_cfg")

        AWG_sequence_cfg = {
            "SAMPLING_RATE": self.get("clock_freq"),
            "CLOCK_SOURCE": (
                1 if self.clock_source().startswith("INT") else 2
            ),  # Internal | External
            "REFERENCE_SOURCE": (
                1 if self.ref_source().startswith("INT") else 2
            ),  # Internal | External
            "EXTERNAL_REFERENCE_TYPE": 1,  # Fixed | Variable
            "REFERENCE_CLOCK_FREQUENCY_SELECTION": 1,
            # 10 MHz | 20 MHz | 100 MHz
            "TRIGGER_SOURCE": 1 if self.get("trigger_source").startswith("EXT") else 2,
            # External | Internal
            "TRIGGER_INPUT_IMPEDANCE": (
                1 if self.get("trigger_impedance") == 50.0 else 2
            ),  # 50 ohm | 1 kohm
            "TRIGGER_INPUT_SLOPE": (
                1 if self.get("trigger_slope").startswith("POS") else 2
            ),  # Positive | Negative
            "TRIGGER_INPUT_POLARITY": (
                1 if self.ask("TRIGger:" + "POLarity?").startswith("POS") else 2
            ),  # Positive | Negative
            "TRIGGER_INPUT_THRESHOLD": self.get("trigger_level"),  # V
            "JUMP_TIMING": (
                1 if self.get("event_jump_timing").startswith("SYNC") else 2
            ),  # Sync | Async
            "RUN_MODE": 4,  # Continuous | Triggered | Gated | Sequence
            "RUN_STATE": 0,  # On | Off
        }
        return AWG_sequence_cfg

    @staticmethod
    def parse_marker_channel_name(name: str) -> _MarkerDescriptor:
        """
        returns from the channel index and marker index from a marker
        descriptor string e.g. '1M1'->(1,1)
        """
        res = re.match(r"^(?P<channel>\d+)M(?P<marker>\d+)$", name)
        assert res is not None

        return _MarkerDescriptor(
            marker=int(res.group("marker")), channel=int(res.group("channel"))
        )

    def make_send_and_load_awg_file_from_forged_sequence(
        self,
        seq: Dict[Any, Any],
        filename: str = "customawgfile.awg",
        preservechannelsettings: bool = True,
    ) -> None:
        """
        Makes an awg file form a forged sequence as produced by
        broadbean.sequence.Sequence.forge. The forged sequence is a dictionary
        (see :attr:`fs_schmea <broadbean.sequence.fs_schmema>`) that does not
        need to be created by broadbean.

        Args:
            seq: the sequence dictionary
            filename: filename of the uploaded awg file.
                See :meth:`~make_send_and_load_awg_file`
            preservechannelsettings: see :meth:`~make_send_and_load_awg_file`

        """
        if not USE_LOMENTUM:
            raise RuntimeError(
                'The method "make_send_and_load_awg_file_from_forged_sequence" is '
                " only available with the `lomentum` module installed"
            )
        n_channels = 4
        self.available_waveform_channels: List[Union[str, int]] = list(
            range(1, n_channels + 1)
        )
        self.available_marker_channels: List[Union[str, int]] = [
            f"{c}M{m}" for c in self.available_waveform_channels for m in [1, 2]
        ]
        self.available_channels = (
            self.available_waveform_channels + self.available_marker_channels
        )

        waveforms = []
        m1s = []
        m2s = []
        # unfortunately the definitions of the sequence elements in terms of
        # channel and step in :meth:`make_and_send_awg_file` and the forged
        # sequence definition are transposed. Start by filling out after schema
        # and transpose at the end.
        # make...: [[wfm1ch1, wfm2ch1, ...], [wfm1ch2, wfm2ch2], ...]
        # dict efectively: {elementid: {channelid: wfm}}

        nreps = []
        trig_waits = []
        goto_states = []
        jump_tos = []

        # obtain list of channels defined in the first step
        if len(seq) < 1:
            # TODO: better error
            raise RuntimeError("Sequences need to have at least one element")

        # assume that the channels are the same on every element
        provided_channels = get_element_channel_ids(seq[0])
        used_waveform_channels = list(
            set(provided_channels).intersection(set(self.available_waveform_channels))
        )
        used_marker_channels = list(
            set(provided_channels).intersection(set(self.available_marker_channels))
        )
        associated_marker_channels = [
            self.parse_marker_channel_name(name).channel
            for name in used_marker_channels
        ]
        used_channels = list(
            set(used_waveform_channels).union(set(associated_marker_channels))
        )

        for i_elem, elem in enumerate(seq):
            # TODO: add support for subsequences
            assert not is_subsequence(elem)
            datadict = elem["data"]

            # Split up the dictionary into two, one for the markers the other
            # for the waveforms
            step_waveforms = {}
            step_markers: Tuple[Dict[int, Any], Dict[int, Any]]
            step_markers = defaultdict(None), defaultdict(None)
            for channel, data in datadict.items():
                if channel in self.available_marker_channels:
                    t = self.parse_marker_channel_name(channel)
                    step_markers[t.marker - 1][t.channel] = data
                elif channel in self.available_waveform_channels:
                    step_waveforms[channel] = data
                else:
                    raise RuntimeError(
                        f"The channel with name {channel} as defined in "
                        f"the element with no. {i_elem} is not an available "
                        f"marker channel or waveform channel.\n"
                        f"Available channels are: "
                        f"{self.available_marker_channels} and "
                        f"{self.available_waveform_channels}"
                    )

            # create empty trace as template for filling traces with markers
            # only and traces without markers
            n_samples = None
            waveform_keys = list(step_waveforms.keys())
            marker_keys = tuple(list(step_markers[i].keys()) for i in range(2))
            if len(waveform_keys) != 0:
                n_samples = len(step_waveforms[waveform_keys[0]])
            else:
                for i in range(2):
                    if len(marker_keys[i]) != 0:
                        n_samples = len(step_markers[i][marker_keys[i][0]])
                        break
            if n_samples is None:
                raise RuntimeError(
                    "It is not allowed to upload an element "
                    "without markers nor waveforms"
                )
            blank_trace = np.zeros(n_samples)

            # I think this does might add some traces dynamically if they are
            # not the same in all elements. Add check in the beginning
            step_waveforms_list = [
                step_waveforms.get(key, blank_trace) for key in used_channels
            ]
            step_markers_list = tuple(
                [step_markers[i].get(key, blank_trace) for key in used_channels]
                for i in range(2)
            )

            waveforms.append(step_waveforms_list)
            m1s.append(step_markers_list[0])
            m2s.append(step_markers_list[1])
            # sequencing
            seq_opts = elem["sequencing"]
            nreps.append(seq_opts.get("nrep", 1))
            trig_waits.append(seq_opts.get("trig_wait", 0))
            goto_states.append(seq_opts.get("goto_state", 0))
            jump_tos.append(seq_opts.get("jump_to", 0))
        # transpose list of lists
        waveforms = [list(x) for x in zip(*waveforms)]
        m1s = [list(x) for x in zip(*m1s)]
        m2s = [list(x) for x in zip(*m2s)]

        self.make_send_and_load_awg_file(
            waveforms,
            m1s,
            m2s,
            nreps,
            trig_waits,
            goto_states,
            jump_tos,
            channels=used_channels,
            filename=filename,
            preservechannelsettings=preservechannelsettings,
        )

    def _generate_awg_file(
        self,
        packed_waveforms: Dict[str, np.ndarray],
        wfname_l: np.ndarray,
        nrep: Sequence[int],
        trig_wait: Sequence[int],
        goto_state: Sequence[int],
        jump_to: Sequence[int],
        channel_cfg: Dict[str, Any],
        sequence_cfg: Optional[Dict[str, float]] = None,
        preservechannelsettings: bool = False,
    ) -> bytes:
        """
        This function generates an .awg-file for uploading to the AWG.
        The .awg-file contains a waveform list, full sequencing information
        and instrument configuration settings.

        Args:
            packed_waveforms: dictionary containing packed waveforms
                with keys wfname_l

            wfname_l: array of waveform names, e.g.
                array([[segm1_ch1,segm2_ch1..], [segm1_ch2,segm2_ch2..],...])

            nrep: list of len(segments) of integers specifying the
                no. of repetions per sequence element.
                Allowed values: 1 to 65536.

            trig_wait: list of len(segments) of integers specifying the
                trigger wait state of each sequence element.
                Allowed values: 0 (OFF) or 1 (ON).

            goto_state: list of len(segments) of integers specifying the
                goto state of each sequence element. Allowed values: 0 to 65536
                (0 means next)

            jump_to: list of len(segments) of integers specifying
                the logic jump state for each sequence element. Allowed values:
                0 (OFF) or 1 (ON).

            channel_cfg: dictionary of valid channel configuration
                records. See self.AWG_FILE_FORMAT_CHANNEL for a complete
                overview of valid configuration parameters.

            preservechannelsettings: If True, the current channel
                settings are queried from the instrument and added to
                channel_cfg (does not overwrite). Default: False.

            sequence_cfg: dictionary of valid head configuration records
                     (see self.AWG_FILE_FORMAT_HEAD)
                     When an awg file is uploaded these settings will be set
                     onto the AWG, any parameter not specified will be set to
                     its default value (even overwriting current settings)

        for info on filestructure and valid record names, see AWG Help,
        File and Record Format (Under 'Record Name List' in Help)
        """
        if preservechannelsettings:
            channel_settings = self.generate_channel_cfg()
            for setting in channel_settings:
                if setting not in channel_cfg:
                    channel_cfg.update({setting: channel_settings[setting]})

        timetuple = tuple(np.array(localtime())[[0, 1, 8, 2, 3, 4, 5, 6, 7]])

        # general settings
        head_str = BytesIO()
        bytes_to_write = self._pack_record("MAGIC", 5000, "h") + self._pack_record(
            "VERSION", 1, "h"
        )
        head_str.write(bytes_to_write)
        # head_str.write(string(bytes_to_write))

        if sequence_cfg is None:
            sequence_cfg = self.generate_sequence_cfg()

        for k in list(sequence_cfg.keys()):
            if k in self.AWG_FILE_FORMAT_HEAD:
                head_str.write(
                    self._pack_record(k, sequence_cfg[k], self.AWG_FILE_FORMAT_HEAD[k])
                )
            else:
                log.warning("AWG: " + k + " not recognized as valid AWG setting")
        # channel settings
        ch_record_str = BytesIO()
        for k in list(channel_cfg.keys()):
            ch_k = k[:-1] + "N"
            if ch_k in self.AWG_FILE_FORMAT_CHANNEL:
                pack = self._pack_record(
                    k, channel_cfg[k], self.AWG_FILE_FORMAT_CHANNEL[ch_k]
                )
                ch_record_str.write(pack)

            else:
                log.warning(
                    "AWG: " + k + " not recognized as valid AWG channel setting"
                )

        # waveforms
        ii = 21

        wf_record_str = BytesIO()
        wlist = list(packed_waveforms.keys())
        wlist.sort()
        for wf in wlist:
            wfdat = packed_waveforms[wf]
            lenwfdat = len(wfdat)

            wf_record_str.write(
                self._pack_record(
                    f"WAVEFORM_NAME_{ii}", wf + "\x00", "{}s".format(len(wf + "\x00"))
                )
                + self._pack_record(f"WAVEFORM_TYPE_{ii}", 1, "h")
                + self._pack_record(f"WAVEFORM_LENGTH_{ii}", lenwfdat, "l")
                + self._pack_record(f"WAVEFORM_TIMESTAMP_{ii}", timetuple[:-1], "8H")
                + self._pack_record(f"WAVEFORM_DATA_{ii}", wfdat, f"{lenwfdat}H")
            )
            ii += 1

        # sequence
        kk = 1
        seq_record_str = BytesIO()

        for segment in wfname_l.transpose():
            seq_record_str.write(
                self._pack_record(f"SEQUENCE_WAIT_{kk}", trig_wait[kk - 1], "h")
                + self._pack_record(f"SEQUENCE_LOOP_{kk}", int(nrep[kk - 1]), "l")
                + self._pack_record(f"SEQUENCE_JUMP_{kk}", jump_to[kk - 1], "h")
                + self._pack_record(f"SEQUENCE_GOTO_{kk}", goto_state[kk - 1], "h")
            )
            for wfname in segment:
                if wfname is not None:
                    # TODO (WilliamHPNielsen): maybe infer ch automatically
                    # from the data size?
                    ch = wfname[-1]
                    seq_record_str.write(
                        self._pack_record(
                            "SEQUENCE_WAVEFORM_NAME_CH_" + ch + f"_{kk}",
                            wfname + "\x00",
                            "{}s".format(len(wfname + "\x00")),
                        )
                    )
            kk += 1

        awg_file = (
            head_str.getvalue()
            + ch_record_str.getvalue()
            + wf_record_str.getvalue()
            + seq_record_str.getvalue()
        )
        return awg_file

    def send_awg_file(
        self, filename: str, awg_file: bytes, verbose: bool = False
    ) -> None:
        """
        Writes an .awg-file onto the disk of the AWG.
        Overwrites existing files.

        Args:
            filename: The name that the file will get on
                the AWG.
            awg_file: A byte sequence containing the awg_file.
                Usually the output of self.make_awg_file.
            verbose: A boolean to allow/suppress printing of messages
                about the status of the filw writing. Default: False.
        """
        if verbose:
            print(
                "Writing to:",
                self.ask("MMEMory:CDIRectory?").replace("\n", "\\ "),
                filename,
            )
        # Header indicating the name and size of the file being send
        name_str = f'MMEMory:DATA "{filename}",'.encode("ASCII")
        size_str = ("#" + str(len(str(len(awg_file)))) + str(len(awg_file))).encode(
            "ASCII"
        )
        mes = name_str + size_str + awg_file
        self.visa_handle.write_raw(mes)

    def load_awg_file(self, filename: str) -> None:
        """
        Loads an .awg-file from the disc of the AWG into the AWG memory.
        This may overwrite all instrument settings, the waveform list, and the
        sequence in the sequencer.

        Args:
            filename: The filename of the .awg-file to load.
        """
        s = f'AWGControl:SREStore "{filename}"'
        b = s.encode(encoding="ASCII")
        log.debug(f"Loading awg file using {s}")
        self.visa_handle.write_raw(b)
        # we must update the appropriate parameter(s) for the sequence
        self.sequence_length.set(self.sequence_length.get())

    def make_awg_file(
        self,
        waveforms: Union[Sequence[Sequence[np.ndarray]], Sequence[np.ndarray]],
        m1s: Union[Sequence[Sequence[np.ndarray]], Sequence[np.ndarray]],
        m2s: Union[Sequence[Sequence[np.ndarray]], Sequence[np.ndarray]],
        nreps: Sequence[int],
        trig_waits: Sequence[int],
        goto_states: Sequence[int],
        jump_tos: Sequence[int],
        channels: Optional[Sequence[int]] = None,
        preservechannelsettings: bool = True,
    ) -> bytes:
        """
        Args:
            waveforms: A list of the waveforms to be packed. The list
                should be filled like so:
                [[wfm1ch1, wfm2ch1, ...], [wfm1ch2, wfm2ch2], ...]
                Each waveform should be a numpy array with values in the range
                -1 to 1 (inclusive). If you do not wish to send waveforms to
                channels 1 and 2, use the channels parameter.

            m1s: A list of marker 1's. The list should be filled
                like so:
                [[elem1m1ch1, elem2m1ch1, ...], [elem1m1ch2, elem2m1ch2], ...]
                Each marker should be a numpy array containing only 0's and 1's

            m2s: A list of marker 2's. The list should be filled
                like so:
                [[elem1m2ch1, elem2m2ch1, ...], [elem1m2ch2, elem2m2ch2], ...]
                Each marker should be a numpy array containing only 0's and 1's

            nreps: List of integers specifying the no. of
                repetitions per sequence element.  Allowed values: 0 to
                65536. O corresponds to Infinite repetitions.

            trig_waits: List of len(segments) of integers specifying the
                trigger wait state of each sequence element.
                Allowed values: 0 (OFF) or 1 (ON).

            goto_states: List of len(segments) of integers
                specifying the goto state of each sequence
                element. Allowed values: 0 to 65536 (0 means next)

            jump_tos: List of len(segments) of integers specifying
                the logic jump state for each sequence element. Allowed values:
                0 (OFF) or 1 (ON).

            channels (list): List of channels to send the waveforms to.
                Example: [1, 3, 2]

            preservechannelsettings (bool): If True, the current channel
                settings are found from the parameter history and added to
                the .awg file. Else, channel settings are not written in the
                file and will be reset to factory default when the file is
                loaded. Default: True.
        """
        packed_wfs = {}
        waveform_names = []
        if not isinstance(waveforms[0], abc.Sequence):
            waveforms_int: Sequence[Sequence[np.ndarray]] = [
                cast(Sequence[np.ndarray], waveforms)
            ]
            m1s_int: Sequence[Sequence[np.ndarray]] = [cast(Sequence[np.ndarray], m1s)]
            m2s_int: Sequence[Sequence[np.ndarray]] = [cast(Sequence[np.ndarray], m2s)]
        else:
            waveforms_int = cast(Sequence[Sequence[np.ndarray]], waveforms)
            m1s_int = cast(Sequence[Sequence[np.ndarray]], m1s)
            m2s_int = cast(Sequence[Sequence[np.ndarray]], m2s)

        for ii in range(len(waveforms_int)):
            namelist = []
            for jj in range(len(waveforms_int[ii])):
                if channels is None:
                    thisname = f"wfm{jj + 1:03d}ch{ii + 1}"
                else:
                    thisname = f"wfm{jj + 1:03d}ch{channels[ii]}"
                namelist.append(thisname)

                package = self._pack_waveform(
                    waveforms_int[ii][jj], m1s_int[ii][jj], m2s_int[ii][jj]
                )

                packed_wfs[thisname] = package
            waveform_names.append(namelist)

        wavenamearray = np.array(waveform_names, dtype="str")

        channel_cfg: Dict[str, Any] = {}

        return self._generate_awg_file(
            packed_wfs,
            wavenamearray,
            nreps,
            trig_waits,
            goto_states,
            jump_tos,
            channel_cfg,
            preservechannelsettings=preservechannelsettings,
        )

    def make_send_and_load_awg_file(
        self,
        waveforms: Sequence[Sequence[np.ndarray]],
        m1s: Sequence[Sequence[np.ndarray]],
        m2s: Sequence[Sequence[np.ndarray]],
        nreps: Sequence[int],
        trig_waits: Sequence[int],
        goto_states: Sequence[int],
        jump_tos: Sequence[int],
        channels: Optional[Sequence[int]] = None,
        filename: str = "customawgfile.awg",
        preservechannelsettings: bool = True,
    ) -> None:
        """
        Makes an .awg-file, sends it to the AWG and loads it. The .awg-file
        is uploaded to C:\\\\Users\\\\OEM\\\\Documents. The waveforms appear in
        the user defined waveform list with names wfm001ch1, wfm002ch1, ...

        Args:
            waveforms: A list of the waveforms to upload. The list
                should be filled like so:
                [[wfm1ch1, wfm2ch1, ...], [wfm1ch2, wfm2ch2], ...]
                Each waveform should be a numpy array with values in the range
                -1 to 1 (inclusive). If you do not wish to send waveforms to
                channels 1 and 2, use the channels parameter.

            m1s: A list of marker 1's. The list should be filled
                like so:
                [[elem1m1ch1, elem2m1ch1, ...], [elem1m1ch2, elem2m1ch2], ...]
                Each marker should be a numpy array containing only 0's and 1's

            m2s: A list of marker 2's. The list should be filled
                like so:
                [[elem1m2ch1, elem2m2ch1, ...], [elem1m2ch2, elem2m2ch2], ...]
                Each marker should be a numpy array containing only 0's and 1's

            nreps: List of integers specifying the no. of
                repetions per sequence element.  Allowed values: 0 to
                65536. 0 corresponds to Infinite repetions.

            trig_waits: List of len(segments) of integers specifying the
                trigger wait state of each sequence element.
                Allowed values: 0 (OFF) or 1 (ON).

            goto_states: List of len(segments) of integers
                specifying the goto state of each sequence
                element. Allowed values: 0 to 65536 (0 means next)

            jump_tos: List of len(segments) of integers specifying
                the logic jump state for each sequence element. Allowed values:
                0 (OFF) or 1 (ON).

            channels: List of channels to send the waveforms to.
                Example: [1, 3, 2]

            filename: The name of the .awg-file. Should end with the .awg
                extension. Default: 'customawgfile.awg'

            preservechannelsettings: If True, the current channel
                settings are found from the parameter history and added to
                the .awg file. Else, channel settings are reset to the factory
                default values. Default: True.
        """

        # waveform names and the dictionary of packed waveforms
        awg_file = self.make_awg_file(
            waveforms,
            m1s,
            m2s,
            nreps,
            trig_waits,
            goto_states,
            jump_tos,
            channels=channels,
            preservechannelsettings=preservechannelsettings,
        )

        # by default, an unusable directory is targeted on the AWG
        self.visa_handle.write("MMEMory:CDIRectory " + '"C:\\Users\\OEM\\Documents"')

        self.send_awg_file(filename, awg_file)
        currentdir = self.visa_handle.query("MMEMory:CDIRectory?")
        currentdir = currentdir.replace('"', "")
        currentdir = currentdir.replace("\n", "\\")
        loadfrom = f"{currentdir}{filename}"
        self.load_awg_file(loadfrom)

    def make_and_save_awg_file(
        self,
        waveforms: Sequence[Sequence[np.ndarray]],
        m1s: Sequence[Sequence[np.ndarray]],
        m2s: Sequence[Sequence[np.ndarray]],
        nreps: Sequence[int],
        trig_waits: Sequence[int],
        goto_states: Sequence[int],
        jump_tos: Sequence[int],
        channels: Optional[Sequence[int]] = None,
        filename: str = "customawgfile.awg",
        preservechannelsettings: bool = True,
    ) -> None:
        """
        Makes an .awg-file and saves it locally.

        Args:
            waveforms: A list of the waveforms to upload. The list
                should be filled like so:
                [[wfm1ch1, wfm2ch1, ...], [wfm1ch2, wfm2ch2], ...]
                Each waveform should be a numpy array with values in the range
                -1 to 1 (inclusive). If you do not wish to send waveforms to
                channels 1 and 2, use the channels parameter.

            m1s: A list of marker 1's. The list should be filled
                like so:
                [[elem1m1ch1, elem2m1ch1, ...], [elem1m1ch2, elem2m1ch2], ...]
                Each marker should be a numpy array containing only 0's and 1's

            m2s: A list of marker 2's. The list should be filled
                like so:
                [[elem1m2ch1, elem2m2ch1, ...], [elem1m2ch2, elem2m2ch2], ...]
                Each marker should be a numpy array containing only 0's and 1's

            nreps: List of integers specifying the no. of
                repetions per sequence element.  Allowed values: 0 to
                65536. O corresponds to Infinite repetions.

            trig_waits: List of len(segments) of integers specifying the
                trigger wait state of each sequence element.
                Allowed values: 0 (OFF) or 1 (ON).

            goto_states: List of len(segments) of integers
                specifying the goto state of each sequence
                element. Allowed values: 0 to 65536 (0 means next)

            jump_tos: List of len(segments) of integers specifying
                the logic jump state for each sequence element. Allowed values:
                0 (OFF) or 1 (ON).

            channels: List of channels to send the waveforms to.
                Example: [1, 3, 2]

            preservechannelsettings: If True, the current channel
                settings are found from the parameter history and added to
                the .awg file. Else, channel settings are not written in the
                file and will be reset to factory default when the file is
                loaded. Default: True.

            filename: The full path of the .awg-file. Should end with the
                .awg extension. Default: 'customawgfile.awg'
        """
        awg_file = self.make_awg_file(
            waveforms,
            m1s,
            m2s,
            nreps,
            trig_waits,
            goto_states,
            jump_tos,
            channels=channels,
            preservechannelsettings=preservechannelsettings,
        )
        with open(filename, "wb") as fid:
            fid.write(awg_file)

    def get_error(self) -> str:
        """
        This function retrieves and returns data from the error and
        event queues.

        Returns:
            String containing the error/event number, the error/event
            description.
        """
        return self.ask("SYSTEM:ERRor:NEXT?")

    def _pack_waveform(
        self, wf: np.ndarray, m1: np.ndarray, m2: np.ndarray
    ) -> np.ndarray:
        """
        Converts/packs a waveform and two markers into a 16-bit format
        according to the AWG Integer format specification.
        The waveform occupies 14 bits and the markers one bit each.
        See Table 2-25 in the Programmer's manual for more information

        Since markers can only be in one of two states, the marker input
        arrays should consist only of 0's and 1's.

        Args:
            wf: A numpy array containing the waveform. The
                data type of wf is unimportant.
            m1: A numpy array containing the first marker.
            m2: A numpy array containing the second marker.

        Returns:
            An array of unsigned 16 bit integers.

        Raises:
            Exception: if the lengths of w, m1, and m2 don't match
            TypeError: if the waveform contains values outside (-1, 1)
            TypeError: if the markers contain values that are not 0 or 1
        """

        # Input validation
        if not ((len(wf) == len(m1)) and (len(m1) == len(m2))):
            raise Exception("error: sizes of the waveforms do not match")
        if np.min(wf) < -1 or np.max(wf) > 1:
            raise TypeError(
                "Waveform values out of bonds." + " Allowed values: -1 to 1 (inclusive)"
            )
        if not np.all(np.in1d(m1, np.array([0, 1]))):
            raise TypeError(
                "Marker 1 contains invalid values." + " Only 0 and 1 are allowed"
            )
        if not np.all(np.in1d(m2, np.array([0, 1]))):
            raise TypeError(
                "Marker 2 contains invalid values." + " Only 0 and 1 are allowed"
            )

        # Note: we use np.trunc here rather than np.round
        # as it is an order of magnitude faster
        packed_wf = np.trunc(16384 * m1 + 32768 * m2 + wf * 8191 + 8191.5).astype(
            np.uint16
        )

        if len(np.where(packed_wf == -1)[0]) > 0:
            print(np.where(packed_wf == -1))
        return packed_wf

    ###########################
    # Waveform file functions #
    ###########################

    def _file_dict(
        self, wf: np.ndarray, m1: np.ndarray, m2: np.ndarray, clock: Optional[float]
    ) -> Dict[str, Union[np.ndarray, float, None]]:
        """
        Make a file dictionary as used by self.send_waveform_to_list

        Args:
            wf: A numpy array containing the waveform. The
                data type of wf is unimportant.
            m1: A numpy array containing the first marker.
            m2: A numpy array containing the second marker.
            clock: The desired clock frequency

        Returns:
            dict: A dictionary with keys 'w', 'm1', 'm2', 'clock_freq', and
                'numpoints' and corresponding values.
        """

        outdict = {
            "w": wf,
            "m1": m1,
            "m2": m2,
            "clock_freq": clock,
            "numpoints": len(wf),
        }

        return outdict

    def delete_all_waveforms_from_list(self) -> None:
        """
        Delete all user-defined waveforms in the list in a single
        action. Note that there is no “UNDO” action once the waveforms
        are deleted. Use caution before issuing this command.

        If the deleted waveform(s) is (are) currently loaded into
        waveform memory, it (they) is (are) unloaded. If the RUN state
        of the instrument is ON, the state is turned OFF. If the
        channel is on, it will be switched off.
        """
        self.write("WLISt:WAVeform:DELete ALL")

    def get_filenames(self) -> str:
        """Duplicate of self.get_folder_contents"""
        return self.ask("MMEMory:CATalog?")

    def send_DC_pulse(
        self, DC_channel_number: int, set_level: float, length: float
    ) -> None:
        """
        Sets the DC level on the specified channel, waits a while and then
        resets it to what it was before.

        Note: Make sure that the output DC state is ON.

        Args:
            DC_channel_number (int): The channel number (1-4).
            set_level (float): The voltage level to set to (V).
            length (float): The time to wait before resetting (s).
        """
        DC_channel_number -= 1
        chandcs = [self.ch1_DC_out, self.ch2_DC_out, self.ch3_DC_out, self.ch4_DC_out]

        restore = chandcs[DC_channel_number].get()
        chandcs[DC_channel_number].set(set_level)
        sleep(length)
        chandcs[DC_channel_number].set(restore)

    def is_awg_ready(self) -> bool:
        """
        Assert if the AWG is ready.

        Returns:
            True, irrespective of anything.
        """
        try:
            self.ask("*OPC?")
        # makes the awg read again if there is a timeout
        except Exception as e:
            log.warning(e)
            log.warning("AWG is not ready")
            self.visa_handle.read()
        return True

    def send_waveform_to_list(
        self, w: np.ndarray, m1: np.ndarray, m2: np.ndarray, wfmname: str
    ) -> None:
        """
        Send a single complete waveform directly to the "User defined"
        waveform list (prepend it). The data type of the input arrays
        is unimportant, but the marker arrays must contain only 1's
        and 0's.

        Args:
            w: The waveform
            m1: Marker1
            m2: Marker2
            wfmname: waveform name

        Raises:
            Exception: if the lengths of w, m1, and m2 don't match
            TypeError: if the waveform contains values outside (-1, 1)
            TypeError: if the markers contain values that are not 0 or 1
        """
        log.debug(f"Sending waveform {wfmname} to instrument")
        # Check for errors
        dim = len(w)

        # Input validation
        if not ((len(w) == len(m1)) and (len(m1) == len(m2))):
            raise Exception("error: sizes of the waveforms do not match")
        if min(w) < -1 or max(w) > 1:
            raise TypeError(
                "Waveform values out of bonds." + " Allowed values: -1 to 1 (inclusive)"
            )
        if (list(m1).count(0) + list(m1).count(1)) != len(m1):
            raise TypeError(
                "Marker 1 contains invalid values." + " Only 0 and 1 are allowed"
            )
        if (list(m2).count(0) + list(m2).count(1)) != len(m2):
            raise TypeError(
                "Marker 2 contains invalid values." + " Only 0 and 1 are allowed"
            )

        self._values["files"][wfmname] = self._file_dict(w, m1, m2, None)

        # if we create a waveform with the same name but different size,
        # it will not get over written
        # Delete the possibly existing file (will do nothing if the file
        # doesn't exist
        s = f'WLISt:WAVeform:DEL "{wfmname}"'
        self.write(s)

        # create the waveform
        s = f'WLISt:WAVeform:NEW "{wfmname}",{dim:d},INTEGER'
        self.write(s)
        # Prepare the data block
        number = (
            (2**13 - 1) + (2**13 - 1) * w + 2**14 * np.array(m1) + 2**15 * np.array(m2)
        )
        number = number.astype("int")
        ws_array = arr.array("H", number)

        ws = ws_array.tobytes()
        s1_str = f'WLISt:WAVeform:DATA "{wfmname}",'
        s1 = s1_str.encode("UTF-8")
        s3 = ws
        s2_str = "#" + str(len(str(len(s3)))) + str(len(s3))
        s2 = s2_str.encode("UTF-8")

        mes = s1 + s2 + s3
        self.visa_handle.write_raw(mes)

    def clear_message_queue(self, verbose: bool = False) -> None:
        """
        Function to clear up (flush) the VISA message queue of the AWG
        instrument. Reads all messages in the the queue.

        Args:
            verbose: If True, the read messages are printed.
                Default: False.
        """
        original_timeout = self.visa_handle.timeout
        self.visa_handle.timeout = 1000  # 1 second as VISA counts in ms
        gotexception = False
        while not gotexception:
            try:
                message = self.visa_handle.read()
                if verbose:
                    print(message)
            except VisaIOError:
                gotexception = True
        self.visa_handle.timeout = original_timeout

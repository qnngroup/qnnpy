# Add this directory to the environment for debugging.
if __name__ == '__main__':
    import sys
    sys.path.append('.')

# Add all run-time requirements.
from numpy import void
from qnnpy.instruments.instrument import Instrument

# Support for bytes
from numpy import byte

# Class SpectraPro500i
# TODO documentation.
class SpectraPro500i(Instrument):
    def __init__(self, termination_character: byte = b'\x0a', port: str = ''):
        super().__init__(termination_character=termination_character, port=port)
        
    def init(self):
        

# Local debugging scripts, will only run when directly running this script.
if __name__ == '__main__':
    sp = SpectraPro500i()
    sp.connect('COM1')
    print(sp.status)
    print(sp.link)
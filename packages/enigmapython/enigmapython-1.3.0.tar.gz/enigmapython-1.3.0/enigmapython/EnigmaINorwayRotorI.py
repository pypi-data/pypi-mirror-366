from .Rotor import Rotor
from .Alphabets import Alphabets

class EnigmaINorwayRotorI(Rotor):
    
    wiring = 'wtokasuyvrbxjhqcpzefmdinlg'
    notch_indexes = [16]
    tag = "IN_I"
    
    def __init__(self, position = 0, ring = 0):
        super().__init__(
                            wiring=self.wiring, 
                            position=position, 
                            ring=ring, 
                            notch_indexes=self.notch_indexes,
                            alphabet=Alphabets.lookup.get('latin_i18n_26chars_lowercase')
                        )
    

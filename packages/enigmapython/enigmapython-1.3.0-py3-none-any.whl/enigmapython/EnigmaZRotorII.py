from .Rotor import Rotor
from .Alphabets import Alphabets

class EnigmaZRotorII(Rotor):
    
    wiring = '5841097632'
    notch_indexes = [5]
    tag = "Z_II"
    
    def __init__(self, position = 0, ring = 0):
        super().__init__(
                            wiring = self.wiring, 
                            position=position, 
                            ring=ring, 
                            notch_indexes=self.notch_indexes, 
                            alphabet=Alphabets.lookup.get("enigma_z_10chars_numbers")
                        )
    

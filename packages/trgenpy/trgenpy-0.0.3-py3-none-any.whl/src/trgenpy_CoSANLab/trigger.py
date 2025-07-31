class Trigger:
    def __init__(self, id, memory_length):
        self.id = id
        
        # Set type label
        self.type = ""
        if(id < 7 and id >= 0):
            self.type = "NeuroScan"
        elif(id < 15 and id >= 8):
            self.type = "Synamps"
        elif(id == 16):
            self.type = "TMSO"
        elif(id == 17):
            self.type = "TMSI"
        elif(id < 26 and id >= 18):
            self.type = "GPIO"
        
        # set max trigger memory length (mtml)
        self._memory_length = memory_length
        self.memory = [0] * memory_length

    def __repr__(self):
        return f"<Trigger id={self.id} instructions={len(self.memory)}>"

    def set_instruction(self, index, instruction):
        if not (0 <= index < self._memory_length):
            raise IndexError(f"Indice {index} fuori limiti (max {self._memory_length - 1})")
        self.memory[index] = instruction
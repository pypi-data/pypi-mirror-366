# Instruction encoding/decoding (as per gui_trigger.c)
INST_MSK       = 0x7
INST_UNACTIVE  = 0x0
INST_ACTIVE    = 0x1
INST_WAITPE    = 0x2
INST_WAITNE    = 0x3
INST_REPEAT    = 0x7
INST_END       = 0x4    
INST_NOT_ADMISSIBLE = 0x5

def unactive_for_us(x): return (x << 3) | INST_UNACTIVE
def active_for_us(x):   return (x << 3) | INST_ACTIVE
def wait_pe(tr):        return (tr << 3) | INST_WAITPE
def wait_ne(tr):        return (tr << 3) | INST_WAITNE
def repeat(addr, times):return (times << 8) | (addr << 3) | INST_REPEAT
def end():              return INST_END
def not_admissible():   return INST_NOT_ADMISSIBLE

def decode_instruction(word):
    opcode = word & INST_MSK
    if opcode == INST_UNACTIVE:
        return ('UNACTIVE', word >> 3)
    elif opcode == INST_ACTIVE:
        return ('ACTIVE', word >> 3)
    elif opcode == INST_WAITPE:
        return ('WAIT_PE', word >> 3)
    elif opcode == INST_WAITNE:
        return ('WAIT_NE', word >> 3)
    elif opcode == INST_REPEAT:
        addr = (word >> 3) & 0x1F
        times = word >> 8
        return ('REPEAT', {'addr': addr, 'times': times})
    elif opcode == INST_END:
        return ('END', None)
    else:
        return ('UNKNOWN', None)

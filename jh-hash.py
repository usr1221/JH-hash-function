class HashReturn:
    SUCCESS = 0
    FAIL = 1
    BAD_HASHLEN = 2

class HashState:
    def __init__(self, hashbitlen: int):
        self.hashbitlen = hashbitlen
        self.databinlen = 0
        self.datasize_in_buffer = 0
        self.H = [0] * 128
        self.A = [0] * 256
        self.roundconstant = [0] * 64
        self.buffer = [0] * 64

roundconstant_zero = [
    0x6, 0xa, 0x0, 0x9, 0xe, 0x6, 0x6, 0x7, 0xf, 0x3, 0xb, 0xc, 0xc, 0x9, 0x0, 0x8,
    0xb, 0x2, 0xf, 0xb, 0x1, 0x3, 0x6, 0x6, 0xe, 0xa, 0x9, 0x5, 0x7, 0xd, 0x3, 0xe,
    0x3, 0xa, 0xd, 0xe, 0xc, 0x1, 0x7, 0x5, 0x1, 0x2, 0x7, 0x7, 0x5, 0x0, 0x9, 0x9,
    0xd, 0xa, 0x2, 0xf, 0x5, 0x9, 0x0, 0xb, 0x0, 0x6, 0x6, 0x7, 0x3, 0x2, 0x2, 0xa
]

sbox = [
    [9,0,4,11,13,12,3,15,1,10,2,6,7,5,8,14],
    [3,12,6,13,5,7,1,9,15,2,0,4,11,10,14,8]
]

# Linear transformation L on two 4-bit values
def L(a: int, b: int):
    b ^= (((a << 1) ^ (a >> 3) ^ ((a >> 2) & 2)) & 0xf)
    a ^= (((b << 1) ^ (b >> 3) ^ ((b >> 2) & 2)) & 0xf)
    return a, b

# Perform a round transformation on the hash state
def R8(hashstate: HashState):
    tem = [0] * 256
    roundconstant_expanded = [0] * 256
    # Expand round constants into 256 one-bit elements
    for i in range(256):
        roundconstant_expanded[i] = (hashstate.roundconstant[i >> 2] >> (3 - (i & 3))) & 1
    # S-box layer, each constant bit selects one S-box from S0 and S1
    for i in range(256):
        tem[i] = sbox[roundconstant_expanded[i]][hashstate.A[i]]
    # MDS layer
    for i in range(0, 256, 2):
        tem[i], tem[i + 1] = L(tem[i], tem[i + 1])
    # Initial swap Pi_8
    for i in range(0, 256, 4):
        tem[i+2], tem[i+3] = tem[i+3], tem[i+2]
    # Permutation P'_8
    for i in range(128):
        hashstate.A[i] = tem[i << 1]
        hashstate.A[i + 128] = tem[(i << 1) + 1]
    # Final swap Phi_8
    for i in range(128, 256, 2):
        hashstate.A[i], hashstate.A[i + 1] = hashstate.A[i + 1], hashstate.A[i]

# Update the round constants
def update_roundconstant(hashstate: HashState):
    tem = [0] * 64
    # S-box layer
    for i in range(64):
        tem[i] = sbox[0][hashstate.roundconstant[i]]
    # MDS layer
    for i in range(0, 64, 2):
        tem[i], tem[i + 1] = L(tem[i], tem[i + 1])
    # Initial swap Pi_6
    for i in range(0, 64, 4):
        tem[i+2], tem[i+3] = tem[i+3], tem[i+2]
    # Permutation P'_6
    for i in range(32):
        hashstate.roundconstant[i] = tem[i << 1]
        hashstate.roundconstant[i + 32] = tem[(i << 1) + 1]
    # Final swap Phi_6
    for i in range(32, 64, 2):
        hashstate.roundconstant[i], hashstate.roundconstant[i + 1] = hashstate.roundconstant[i + 1], hashstate.roundconstant[i]

# Initial permutation step
def E8_initialgroup(hashstate: HashState):
    tem = [0] * 256
    # Group the H state into the A state
    for i in range(256):
        t0 = (hashstate.H[i >> 3] >> (7 - (i & 7))) & 1
        t1 = (hashstate.H[(i + 256) >> 3] >> (7 - (i & 7))) & 1
        t2 = (hashstate.H[(i + 512) >> 3] >> (7 - (i & 7))) & 1
        t3 = (hashstate.H[(i + 768) >> 3] >> (7 - (i & 7))) & 1
        tem[i] = (t0 << 3) | (t1 << 2) | (t2 << 1) | t3
    # Padding the odd-th elements and even-th elements separately
    for i in range(128):
        hashstate.A[i << 1] = tem[i]
        hashstate.A[(i << 1) + 1] = tem[i + 128]

# Final permutation step
def E8_finaldegroup(hashstate: HashState):
    tem = [0] * 256
    # Ungroup the A state into the H state
    for i in range(128):
        tem[i] = hashstate.A[i << 1]
        tem[i + 128] = hashstate.A[(i << 1) + 1]
    for i in range(128):
        hashstate.H[i] = 0
    for i in range(256):
        t0 = (tem[i] >> 3) & 1
        t1 = (tem[i] >> 2) & 1
        t2 = (tem[i] >> 1) & 1
        t3 = (tem[i] >> 0) & 1
        hashstate.H[i >> 3] |= t0 << (7 - (i & 7))
        hashstate.H[(i + 256) >> 3] |= t1 << (7 - (i & 7))
        hashstate.H[(i + 512) >> 3] |= t2 << (7 - (i & 7))
        hashstate.H[(i + 768) >> 3] |= t3 << (7 - (i & 7))

# Full E8 permutation
def E8(hashstate: HashState):
    # Initialize round constants
    for i in range(64):
        hashstate.roundconstant[i] = roundconstant_zero[i]
    # Initial permutation step
    E8_initialgroup(hashstate)
    # Perform 42 rounds of the R8 transformation
    for i in range(42):
        R8(hashstate)
        update_roundconstant(hashstate)
    # Final permutation step
    E8_finaldegroup(hashstate)

# Compression function F8
def F8(hashstate: HashState):
    # XOR the message with the first half of H
    for i in range(64):
        hashstate.H[i] ^= hashstate.buffer[i]
    # Perform E8 permutation
    E8(hashstate)
    # XOR the message with the last half of H
    for i in range(64):
        hashstate.H[i + 64] ^= hashstate.buffer[i]

# Initialization function for the hash state
def Init(hashstate: HashState, hashbitlen: int) -> int:
    hashstate.databinlen = 0
    hashstate.datasize_in_buffer = 0
    hashstate.hashbitlen = hashbitlen
    # Initialize buffer and H state
    for i in range(64):
        hashstate.buffer[i] = 0
    for i in range(128):
        hashstate.H[i] = 0
    # Initialize the initial hash value of JH
    hashstate.H[1] = hashbitlen & 0xff
    hashstate.H[0] = (hashbitlen >> 8) & 0xff
    # Compute H0 from H(-1) with message M(0) being set as 0
    F8(hashstate)
    return HashReturn.SUCCESS

# Update function for processing data
def Update(hashState: HashState, data: bytes, databitlen: int) -> int:
    hashState.databinlen += databitlen
    index = 0

    # Handle any remaining data in the buffer, fill it to a full message block first
    if hashState.datasize_in_buffer > 0 and (hashState.datasize_in_buffer + databitlen) < 512:
        if databitlen % 8 == 0:
            hashState.buffer[hashState.datasize_in_buffer // 8: (hashState.datasize_in_buffer // 8) + (databitlen // 8)] = data[:databitlen // 8]
        else:
            hashState.buffer[hashState.datasize_in_buffer // 8: (hashState.datasize_in_buffer // 8) + (databitlen // 8) + 1] = data[:(databitlen // 8) + 1]
        hashState.datasize_in_buffer += databitlen
        databitlen = 0

    # Handle the incoming data, sufficient for a full block
    if hashState.datasize_in_buffer > 0 and (hashState.datasize_in_buffer + databitlen) >= 512:
        hashState.buffer[hashState.datasize_in_buffer // 8:] = data[:64 - (hashState.datasize_in_buffer // 8)]
        index = 64 - (hashState.datasize_in_buffer // 8)
        databitlen -= (512 - hashState.datasize_in_buffer)
        F8(hashState)
        hashState.datasize_in_buffer = 0

    # Hash the remaining full message blocks
    while databitlen >= 512:
        hashState.buffer = list(data[index:index + 64])
        F8(hashState)
        index += 64
        databitlen -= 512

    # Store the partial block into buffer, assume that -- if part of the last byte is not part of the message, then that part consists of 0 bits
    if databitlen > 0:
        if databitlen % 8 == 0:
            hashState.buffer[:databitlen // 8] = data[index:index + (databitlen // 8)]
        else:
            hashState.buffer[:(databitlen // 8) + 1] = data[index:index + (databitlen // 8) + 1]
        hashState.datasize_in_buffer = databitlen

    return HashReturn.SUCCESS

# Finalization function for producing the hash value
def Final(hashState: HashState, hashval: bytearray) -> int:
    # Handle padding and final blocks
    if hashState.databinlen % 512 == 0:
        hashState.buffer = [0] * 64
        hashState.buffer[0] = 0x80
        hashState.buffer[63] = hashState.databinlen & 0xff
        hashState.buffer[62] = (hashState.databinlen >> 8) & 0xff
        hashState.buffer[61] = (hashState.databinlen >> 16) & 0xff
        hashState.buffer[60] = (hashState.databinlen >> 24) & 0xff
        hashState.buffer[59] = (hashState.databinlen >> 32) & 0xff
        hashState.buffer[58] = (hashState.databinlen >> 40) & 0xff
        hashState.buffer[57] = (hashState.databinlen >> 48) & 0xff
        hashState.buffer[56] = (hashState.databinlen >> 56) & 0xff
        F8(hashState)
    else:
        if hashState.datasize_in_buffer % 8 == 0:
            for i in range((hashState.databinlen % 512) // 8, 64):
                hashState.buffer[i] = 0
        else:
            for i in range(((hashState.databinlen % 512) // 8) + 1, 64):
                hashState.buffer[i] = 0

        hashState.buffer[(hashState.databinlen % 512) // 8] |= 1 << (7 - (hashState.databinlen % 8))
        F8(hashState)
        hashState.buffer = [0] * 64
        hashState.buffer[63] = hashState.databinlen & 0xff
        hashState.buffer[62] = (hashState.databinlen >> 8) & 0xff
        hashState.buffer[61] = (hashState.databinlen >> 16) & 0xff
        hashState.buffer[60] = (hashState.databinlen >> 24) & 0xff
        hashState.buffer[59] = (hashState.databinlen >> 32) & 0xff
        hashState.buffer[58] = (hashState.databinlen >> 40) & 0xff
        hashState.buffer[57] = (hashState.databinlen >> 48) & 0xff
        hashState.buffer[56] = (hashState.databinlen >> 56) & 0xff
        F8(hashState)

    # Truncate the final hash value to generate the message digest
    if hashState.hashbitlen == 224:
        hashval.extend(hashState.H[100:128])
    elif hashState.hashbitlen == 256:
        hashval.extend(hashState.H[96:128])
    elif hashState.hashbitlen == 384:
        hashval.extend(hashState.H[80:128])
    elif hashState.hashbitlen == 512:
        hashval.extend(hashState.H[64:128])

    return HashReturn.SUCCESS

# Top-level hash function
def Hash(hashbitlen: int, data: bytes, databitlen: int, hashval: bytearray) -> int:
    # Check for valid hash bit length
    if hashbitlen in (224, 256, 384, 512):
        state = HashState(hashbitlen)
        # Initialize the hash state
        Init(state, hashbitlen)
        # Update the hash state with input data
        Update(state, data, databitlen)
        # Finalize the hash value
        Final(state, hashval)
        return HashReturn.SUCCESS
    else:
        return HashReturn.BAD_HASHLEN
import random
import string
import itertools
import hashlib
import numpy as np
from Crypto.Cipher import ARC4
from enum import Enum

def generate_random_secret(size=20, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def bytes_to_bits(by):
    bi = "{:0{l}b}".format(int.from_bytes(by, byteorder='big'), l=len(by) * 8)
    return [int(b) for b in bi]

def bits_to_bytes(bi):
    bi = ''.join([str(x) for x in bi])
    return int(bi, 2).to_bytes((len(bi) + 7) // 8, byteorder='big')

def split_blocks(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))

def merge_blocks(iterable):
    return list(itertools.chain.from_iterable(iterable))

class Coder():
    def __init__(self, block_size=16):
        self.secret = None
        self.keys = {'p': None, 'd': None, 's': None} # permutation, diffusion, selection
        self.block_size = block_size # bits
        self.X = None
        self.Y = None
        self.p_box = None
        self.blocks = None
        self.not_positions = None
        self.circular_shifts = None

        self.generate_keys()

    def generate_keys(self):
        self.secret = generate_random_secret().encode()
        key = hashlib.sha512(self.secret).digest()
        self.keys['p'] = [x for x in key[0:23]]
        self.keys['d'] = key[23:39]
        self.keys['s'] = [x for x in key[39:62]]

    def generate_permutation_box(self, N):
        # Init
        # Fill key values
        key = self.keys['p'][:N]
        S = len(key)
        p_box = [0] * N
        for i in range(min(S, N)):
            p_box[i] = key[i]
        for i in range(S - 1):
            p_box[i] += p_box[i + 1]
        p_box[S - 1] = key[0]
        # Fill other values
        if (N > S):
            j = S
            for i in range(S - 1):
                for k in range(i, S - 1):
                    p_box[j] = p_box[i] + p_box[k + 1]
                    j += 1
                    if (j >= N):
                        break
                if (j >= N):
                    break
        # Apply mod
        for i in range(N):
            p_box[i] %= (N - 1)

        # Eliminate (remove repeated values)
        # L, R = 0, N - 1
        # while(L < R):
        #     for i in range(L + 1, R):
        #         if p_box[L] == p_box[i]:
        #             print('Removed', p_box[i])
        #             p_box[i] = -1
        #     for i in range(L + 1, R - 1):
        #         if p_box[R] == p_box[i]:
        #             print('Removed', p_box[i])
        #             p_box[i] = -1
        #         print(i)
        #     L += 1
        #     R -= 1
        p_box_local = p_box
        p_box = []
        used = set()

        for x in p_box_local:
            if x in used:
                p_box.append(-1)
            else:
                p_box.append(x)
                used.add(x)

        # Fill
        missing = [i for i in range(N)]
        for x in p_box:
            if x != -1:
                try:
                    missing.remove(x)
                except ValueError:
                    pass
        m = len(missing)
        # Fill values one by one from left and right sides
        i = 0
        while(i < m):
            j = N - 1
            while((j >= 0) and (p_box[j] != -1)):
                j -= 1
            if (j >= 0):
                p_box[j] = missing[i]
                i += 1

            k = 0
            while((k < N) and (p_box[k] != -1)):
                k += 1
            if (k < N):
                p_box[k] = missing[i]
                i += 1

        if len(p_box) > len(set(p_box)):
            print('Non-unique!')
            return None
        return p_box

    def permute_bits(self):
        # Generate and apply permutation box
        if not self.p_box:
            self.p_box = self.generate_permutation_box(len(self.X))
        self.X = list(map(self.X.__getitem__, self.p_box))

    def encrypt_blocks(self):
        # Break X into blocks
        self.blocks = list(split_blocks(self.X, self.block_size))

        # Create secret blocks by applying RC4 to each block
        if not self.not_positions:
            self.not_positions = []
            cipher = ARC4.new(self.keys['d'])
            for block in self.blocks:
                secret_block = bytes_to_bits(cipher.encrypt(bits_to_bytes(block)))
                # Extract positions of 1's
                pos = [i for i,val in enumerate(secret_block) if val == 1]
                self.not_positions.append(pos)
        # Apply secret NOT operations
        for n in range(len(self.blocks)):
            for i in self.not_positions[n]:
                self.blocks[n][i] = 0 if self.blocks[n][i] == 1 else 1

        # Dynamic Key Selection Algorithm
        if not self.circular_shifts:
            # Generate delta-p-box and secret bank
            delta_p_box = self.generate_permutation_box(len(self.blocks))
            secret_bank = random.choices(range(0, self.block_size // 4 + 1), k=len(self.blocks))
            # Create and apply circular shifts
            self.circular_shifts = []
            for i in range(len(self.blocks)):
                self.circular_shifts.append(secret_bank[delta_p_box[i]])

        for i in range(len(self.blocks)):
            self.blocks[i] = list(np.roll(self.blocks[i], self.circular_shifts[i]))

    def encode(self, X):
        self.X = bytes_to_bits(X)
        # Permutation
        self.permute_bits()
        # Dynamic blocks encryption
        self.encrypt_blocks()
        # Output encoded text
        result = merge_blocks(self.blocks)
        return bits_to_bytes(result)

    def inverse_permute_bits(self):
        # Generate and apply inverse permutation box
        inverse_p_box = [0] * len(self.p_box)
        for i in range(len(self.p_box)):
            inverse_p_box[self.p_box[i]] = i
        self.Y = list(map(self.Y.__getitem__, inverse_p_box))

    def decrypt_blocks(self):
        self.blocks = list(split_blocks(self.Y, self.block_size))

        # Apply inverse circular shifts
        for i in range(len(self.blocks)):
            self.blocks[i] = list(np.roll(self.blocks[i], - self.circular_shifts[i]))

        # Apply secret NOT operations
        for n in range(len(self.blocks)):
            for i in self.not_positions[n]:
                self.blocks[n][i] = 0 if self.blocks[n][i] == 1 else 1

    def decode(self, Y):
        self.Y = bytes_to_bits(Y)
        # Dynamic blocks decryption
        self.decrypt_blocks()
        # Restore Y before permutation
        self.Y = merge_blocks(self.blocks)
        # Inverse permutation
        self.inverse_permute_bits()
        # Output decoded text
        return bits_to_bytes(self.Y)

    def decrypt_blocks_res(self, Z1, Z2):
        blocks1 = list(split_blocks(Z1, self.block_size))
        blocks2 = list(split_blocks(Z2, self.block_size))

        # Apply inverse circular shifts
        for i in range(len(blocks1)):
            blocks1[i] = list(np.roll(blocks1[i], - self.circular_shifts[i]))
            blocks2[i] = list(np.roll(blocks2[i], - self.circular_shifts[i]))

        self.blocks = blocks1.copy()
        # Tricky moment: we need to combine results of normal and homomorphic operations
        # performed on encoded texts, so we choose normal bits from first result and bits from secret NOT positions
        # from second. This operation may be omitted for XOR but not for AND!
        for n in range(len(self.blocks)):
            for i in self.not_positions[n]:
                self.blocks[n][i] = blocks2[n][i]
                # Apply secret NOT operations
                self.blocks[n][i] = 0 if self.blocks[n][i] == 1 else 1

    def decode_res(self, Z1, Z2):
        Z1 = bytes_to_bits(Z1)
        Z2 = bytes_to_bits(Z2)
        # Dynamic blocks decryption
        self.decrypt_blocks_res(Z1, Z2)
        # Restore Y before permutation
        self.Y = merge_blocks(self.blocks)
        # Inverse permutation
        self.inverse_permute_bits()
        # Output decoded text
        return bits_to_bytes(self.Y)

class Operations(Enum):
    XOR = 1
    AND = 2

class Functions:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def plain_xor(self):
        p_xor = bytearray((a ^ b) for (a, b) in zip(self.X, self.Y))
        return bytes(p_xor)

    def plain_and(self):
        p_and = bytes((a & b) for (a, b) in zip(self.X, self.Y))
        return bytes(p_and)

    def nohe_xor(self):
        homomorphic_xor = bytearray((a ^ b) for (a, b) in zip(self.X, self.Y))
        bi = [1 if x == 0 else 0 for x in bytes_to_bits(homomorphic_xor)]
        homomorphic_xor = bits_to_bytes(bi)
        return bytes(homomorphic_xor)

    def nohe_and(self):
        homomorphic_and = bytes((a | b) for (a, b) in zip(self.X, self.Y))
        return bytes(homomorphic_and)

'''
A small example to show how algorithm works:
Two different texts are encoded, decoded and results are compared

if __name__ == '__main__':
    import difflib
    
    coder = Coder()
    X = 'fjclak2i3epofckal;we'.encode()
    Y = 'aalskdj2;3l4foq2kf9w'.encode()
    
    for text in [X, Y]:
        enc = coder.encode(text)
        dec = coder.decode(enc)

        print(f'Text: {text}')
        print(f'Encoded: {enc}')
        print(f'Decoded: {dec}')

        # Check for differences
        output = [li for li in difflib.ndiff(text, dec) if li[0] != ' ']
        print(f'Check equal: {output}')
'''
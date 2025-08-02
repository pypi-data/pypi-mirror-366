"""
core.py — C2H5OH Core Encryption Algorithms
------------------------------------------
Thuật toán mật mã do テオネ先生 sáng tạo:
- Hố đen (Black Hole Absorb)
- Tăng-Giảm-Tuần Hoàn (Periodic Shift)
"""

import random


def periodic_shift(n: int) -> int:
    if n % 2 == 1:
        return (n + 1) // 2
    else:
        from math import pow
        return int(n ** pow((2 * n + 1), 1 / (n / 2)))


def parse_digits(n: int) -> list:
    """Tách từng chữ số trong số nguyên `n` thành list."""
    return [int(d) for d in str(abs(n))]


def generate_binary_key(length: int) -> str:
    return ''.join(random.choice('01') for _ in range(length))


def expand_to_length(seq: list, target_len: int) -> list:
    """Nối lại chính seq cho đến khi đủ độ dài."""
    out = []
    while len(out) < target_len:
        out.extend(seq)
    return out[:target_len]


class C2H5OHProtocol:
    def __init__(self, key_length: int = 16):
        self.key_length = key_length

    def encrypt(self, message: str, key_base: int) -> str:
        msg_bytes = message.encode('utf-8')
        msg_len = len(msg_bytes)

        # Sinh khóa nhị phân
        self._last_key_bits = [int(b) for b in generate_binary_key(self.key_length)]

        # Phân tích key_base
        n_analyzed = parse_digits(periodic_shift(key_base))

        # Chuỗi tăng từ 1 đến m
        inc_seq = list(range(1, msg_len + 1))

        # Ghép lại thành chuỗi o
        o_seq = self._last_key_bits + n_analyzed + inc_seq
        self._last_o = expand_to_length(o_seq, msg_len)

        # Mã hóa
        encoded = []
        for i, byte in enumerate(msg_bytes):
            c = (self._last_o[i] - byte) % 256
            encoded.append(format(c, '02x'))

        self._last_key_base = key_base
        return ''.join(encoded)

    def decrypt(self, ciphertext: str) -> str:
        if not hasattr(self, '_last_o'):
            raise ValueError("Không có khóa `o` để giải mã.")

        num_bytes = len(ciphertext) // 2
        decoded_bytes = bytearray()

        for i in range(num_bytes):
            c = int(ciphertext[2*i:2*i+2], 16)
            b = (self._last_o[i] - c) % 256
            decoded_bytes.append(b)

        return decoded_bytes.decode('utf-8', errors='strict')

    def get_binary_key(self):
        return self._last_key_bits

    def get_o_sequence(self):
        return self._last_o
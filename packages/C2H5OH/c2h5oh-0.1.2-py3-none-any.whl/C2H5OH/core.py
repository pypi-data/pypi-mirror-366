"""
core.py — C2H5OH Core Encryption Algorithms
------------------------------------------
Thuật toán mật mã do テオネ先生 sáng tạo:
- Hố đen (Black Hole Absorb)
- Tăng-Giảm-Tuần Hoàn (Periodic Shift)
"""

import random


def nth_root(base: float, n: float) -> float:
    """Căn bậc n của số `base`."""
    if n == 0:
        raise ValueError("Không thể lấy căn bậc 0")
    return base ** (1 / n)


def blackhole_absorb(_: int) -> int:
    """Thuật toán Hố Đen: bất kỳ giá trị nào → 1."""
    return 1


def periodic_shift(n: int) -> int:
    """
    Thuật toán Tăng-Giảm-Tuần Hoàn:
    - Lẻ: (n+1)//2
    - Chẵn: n^(căn bậc (n/2) của (2n+1))
    """
    if n % 2 == 1:
        return (n + 1) // 2
    else:
        root = nth_root(2 * n + 1, n / 2)
        return int(n ** root)


def cyclic_increase_sequence(start: int, length: int) -> list:
    """Sinh chuỗi tăng kiểu: [n, n+1, n+1+2, n+1+2+3, ...]"""
    seq = [start]
    add = 1
    for _ in range(length - 1):
        seq.append(seq[-1] + add)
        add += 1
    return seq


def generate_binary_key(length: int) -> str:
    """Sinh khóa nhị phân ngẫu nhiên độ dài `length`."""
    return ''.join(random.choice('01') for _ in range(length))


def encode_message(msg: str, key_base: int, key_length: int = 16) -> str:
    """
    Mã hóa chuỗi `msg` bằng thuật toán tuần hoàn + XOR với khóa nhị phân.
    """
    key = generate_binary_key(key_length)
    shift_seq = cyclic_increase_sequence(periodic_shift(key_base), len(msg))
    encoded = []

    for i, ch in enumerate(msg):
        code = ord(ch)
        shift = shift_seq[i % len(shift_seq)] % 256
        xor_bit = int(key[i % key_length])
        encoded_val = (code + shift) ^ xor_bit
        encoded.append(format(encoded_val, '02x'))

    return ''.join(encoded)


def blackhole_defense(ciphertext: str, attacker_detected: bool) -> str:
    """
    Nếu phát hiện attacker, toàn bộ ciphertext trở thành '1' (blackhole logic).
    """
    if attacker_detected:
        return '1' * len(ciphertext)
    return ciphertext


class C2H5OHProtocol:
    """Giao thức mã hóa C2H5OH của テオネ先生"""

    def __init__(self, key_length: int = 16):
        self.key_length = key_length

    def encrypt(self, message: str, key_base: int) -> str:
       self._last_key = generate_binary_key(self.key_length)
       self._last_key_base = key_base
       shift_seq = cyclic_increase_sequence(periodic_shift(key_base), len(message.encode("utf-8")))
       encoded = []

       message_bytes = message.encode("utf-8")  # 👈

       for i, byte in enumerate(message_bytes):
            shift = shift_seq[i % len(shift_seq)] % 256
            xor_bit = int(self._last_key[i % self.key_length])
            encoded_val = (byte + shift) ^ xor_bit
            encoded.append(format(encoded_val, '02x'))

       return ''.join(encoded)

    def decrypt(self, ciphertext: str) -> str:
        if not hasattr(self, '_last_key') or not hasattr(self, '_last_key_base'):
            raise ValueError("Chưa có thông tin khóa. Hãy mã hóa trước khi giải mã.")

        num_bytes = len(ciphertext) // 2
        shift_seq = cyclic_increase_sequence(
        periodic_shift(self._last_key_base),
        num_bytes
    )
        decoded_bytes = bytearray()

        for i in range(num_bytes):
            encoded_val = int(ciphertext[2*i:2*i+2], 16)
            shift = shift_seq[i % len(shift_seq)] % 256
            xor_bit = int(self._last_key[i % self.key_length])
            original_byte = (encoded_val ^ xor_bit) - shift
            decoded_bytes.append(original_byte % 256)

        return decoded_bytes.decode("utf-8", errors="strict")

    def fallback_blackhole(self) -> str:
        """
        Trả về chuỗi '1' cố định để phòng thủ khẩn cấp khi bị tấn công.
        """
        return '1' * 32
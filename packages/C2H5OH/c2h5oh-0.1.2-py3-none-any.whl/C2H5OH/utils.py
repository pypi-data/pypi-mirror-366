"""
utils.py — Các hàm phụ trợ cho C2H5OH Crypto Library
---------------------------------------------------
Bao gồm hỗ trợ BB84, sinh khóa, entropy, encode/decode giống PyNaCl.
"""

import random
import time
import base64


def gen_binary_string(length: int) -> str:
    """Sinh chuỗi nhị phân ngẫu nhiên dài `length`."""
    return ''.join(random.choice('01') for _ in range(length))


def generate_binary_key(length: int) -> str:
    """Sinh khóa nhị phân giống cách dùng trong BB84."""
    return gen_binary_string(length)


def generate_numeric_key(length: int) -> list[int]:
    """Sinh khóa số (0 hoặc 1) kiểu danh sách."""
    return [random.randint(0, 1) for _ in range(length)]


def compare_bases(sender: str, receiver: str) -> list[int]:
    """
    So sánh cơ sở BB84 để lấy chỉ số trùng nhau.
    Returns:
        List[int]: Danh sách vị trí giống nhau
    """
    return [i for i in range(len(sender)) if sender[i] == receiver[i]]


def extract_key(data: str, indices: list[int]) -> str:
    """
    Trích khóa tại các vị trí chỉ định từ chuỗi dữ liệu.
    Args:
        data (str): chuỗi dữ liệu gốc
        indices (List[int]): vị trí trích
    Returns:
        str: chuỗi được trích
    """
    return ''.join(data[i] for i in indices)


def format_timestamp() -> str:
    """Trả về thời gian hiện tại định dạng đẹp."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def entropy(binary_string: str) -> float:
    """Tính entropy của chuỗi nhị phân."""
    p0 = binary_string.count('0') / len(binary_string)
    p1 = 1 - p0
    import math
    if p0 == 0 or p1 == 0:
        return 0.0
    return -p0 * math.log2(p0) - p1 * math.log2(p1)


def string_to_bits(message: str) -> str:
    """Chuyển chuỗi thành chuỗi bit (binary)."""
    return ''.join(format(ord(c), '08b') for c in message)


def bits_to_string(bits: str) -> str:
    """Chuyển chuỗi bit về văn bản."""
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(b, 2)) for b in chars)


def base64_encode(message: str) -> str:
    """Mã hóa base64."""
    return base64.b64encode(message.encode()).decode()


def base64_decode(b64_string: str) -> str:
    """Giải mã base64."""
    return base64.b64decode(b64_string.encode()).decode()
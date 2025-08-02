"""
test.py — Kiểm thử các module chính trong thư viện C2H5OH
----------------------------------------------------------
Chạy kiểm thử các chức năng:
- Thuật toán tăng–giảm–tuần hoàn
- Thuật toán hố đen
- Mã hóa thông điệp với key
- Hàm phụ trợ (utils)
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from C2H5OH.core import periodic_shift as increasing_oscillation, blackhole_absorb, C2H5OHProtocol
from C2H5OH import utils


def test_oscillation():
    print("🔬 Kiểm thử thuật toán tăng–giảm–tuần hoàn:")
    for n in [1, 3, 10, 50, 100]:
        result = increasing_oscillation(n)
        print(f"  ➤ f({n}) = {result}")


def test_blackhole():
    print("\n🕳️ Kiểm thử thuật toán hố đen:")
    for n in [1, 3, 100, 10**10, 10**99]:
        result = blackhole_absorb(n)
        print(f"  ➤ BH({n}) = {result}")


def test_protocol():
    print("\n🔐 Kiểm thử giao thức mã hóa C2H5OHProtocol:")
    message = "Quantum test"
    key = utils.gen_binary_string(16)

    key_length = 16
    key_base = 16
    protocol = C2H5OHProtocol(key_length)
    encrypted = protocol.encrypt(message, key_base=key_base)
    decrypted = protocol.decrypt(encrypted)

    print(f"  ➤ Message:   {message}")
    print(f"  ➤ Key:       {key}")
    print(f"  ➤ Encrypted: {encrypted}")
    print(f"  ➤ Decrypted: {decrypted}")
    assert decrypted == message, "❌ Giải mã thất bại!"


def test_utils():
    print("\n🛠️ Kiểm thử utils:")
    msg = "Hello"
    bits = utils.string_to_bits(msg)
    back = utils.bits_to_string(bits)
    entropy_val = utils.entropy(bits)
    print(f"  ➤ Bits:     {bits}")
    print(f"  ➤ Back:     {back}")
    print(f"  ➤ Entropy:  {entropy_val:.4f}")
    assert back == msg
   
def test_blackhole_defense():
    print("\n🚨 Mô phỏng tấn công và phòng thủ blackhole:")

    # Người gửi mã hóa
    message = "Secret message"
    key_base = 42
    protocol = C2H5OHProtocol()
    encrypted = protocol.encrypt(message, key_base=key_base)

    print(f"  ➤ Người gửi mã hóa: {encrypted}")

    # Kẻ tấn công cướp ciphertext
    attacker_steals = True
    defended = blackhole_defense(encrypted, attacker_detected=attacker_steals)

    print(f"  ➤ Sau khi phát hiện tấn công: {defended}")

    # Đảm bảo hệ thống tự phá hủy mã
    assert set(defended) == {'1'}, "❌ Blackhole defense không hoạt động!"    


if __name__ == "__main__":
    print("🧪 BẮT ĐẦU KIỂM THỬ THƯ VIỆN C2H5OH\n")
    test_oscillation()
    test_blackhole()
    test_protocol()
    test_utils()
    print("\n✅ HOÀN TẤT TẤT CẢ KIỂM THỬ.")
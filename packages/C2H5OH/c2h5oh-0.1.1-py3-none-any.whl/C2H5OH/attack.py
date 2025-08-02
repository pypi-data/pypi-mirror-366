import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from C2H5OH.core import blackhole_defense, encode_message

def simulate_attack_scenario():
    print("🚨 Mô phỏng tấn công mã hóa C2H5OH - Thuật toán Hố Đen\n")
    message = "Teone_Sensei"
    key_base = 100

    cipher = encode_message(message, key_base)
    print(f"🔐 Mã sau khi encode ban đầu: {cipher}")

    attacker_detected = True

    secured_cipher = blackhole_defense(cipher, attacker_detected)
    print(f"🛡️  Sau khi phòng thủ (blackhole): {secured_cipher}")

    if secured_cipher == "1" * len(cipher):
        print("✅ Thành công: Mật mã đã được phá hủy để ngăn kẻ tấn công.")
    else:
        print("⚠️  Không có tấn công: Mật mã được giữ nguyên.")

if __name__ == "__main__":
    simulate_attack_scenario()
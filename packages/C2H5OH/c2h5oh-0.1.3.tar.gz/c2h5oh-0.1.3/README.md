# 🔐 C2H5OH – Bộ Mật Mã Cổ Điển & Đặc Biệt

> 🧪 Phát triển bởi テオネ先生 (2025)  
> 📜 License: [GNU GPL v3.0](LICENSE.txt)

---

## 🌟 Giới thiệu

**C2H5OH** là một thư viện mã hóa đơn giản, sáng tạo nhưng độc đáo – với các thuật toán mô phỏng logic toán học – mô hình hóa các hiện tượng tự nhiên như: **Tăng–Giảm–Tuần hoàn**, **Hố Đen**, **Mô phỏng BB84**,...

Được xây dựng hướng tới tính giáo dục, thử nghiệm, và ý tưởng sáng tạo hơn là bảo mật thực chiến.

---

## 🧠 Các thành phần chính

- 🔁 `periodic_shift(n)` – tăng/giảm/tuần hoàn thông minh dựa trên số nguyên.
- 🕳️ `blackhole_absorb(n)` – mọi giá trị đều bị hút về 1.
- 🔐 `C2H5OHProtocol` – mã hóa chuỗi dùng `key_base`, `cyclic shift`, và XOR khóa nhị phân.
- 🛡️ `blackhole_defense()` – cơ chế tự hủy nếu phát hiện tấn công (mô phỏng cơ bản BB84).
- 🧰 **Utils** – chuyển đổi string ↔ bit, đo entropy, sinh khóa nhị phân,...

---

## ⚙️ Cài đặt

**Cách 1** – khi đã upload lên PyPI:

```bash
pip install c2h5oh
```
Cách 2 – tự build thủ công:

```
git clone https://github.com/teone-sensei/C2H5OH.git
cd C2H5OH
python setup.py sdist bdist_wheel
```

---

🚀 Ví dụ sử dụng

```Python
from C2H5OH.core import C2H5OHProtocol

protocol = C2H5OHProtocol(key_length=16)
ciphertext = protocol.encrypt("Quantum test", key_base=42)
plaintext = protocol.decrypt(ciphertext)

print("Giải mã:", plaintext)
```

---

📂 Cấu trúc thư viện

C2H5OH_project/
├── C2H5OH/
│   ├── __init__.py
│   ├── core.py
│   ├── utils.py
│   ├── attack.py
│   └── version.py
├── Tests/
│   └── test.py
├── LICENSE.txt
├── README.md
├── setup.py
├── pyproject.toml
└── requirements.txt


---

🧪 Kiểm thử

Chạy toàn bộ test bằng:

python Tests/test.py


---

📜 License

This project is licensed under the GNU General Public License v3.0
© 2025 テオネ先生
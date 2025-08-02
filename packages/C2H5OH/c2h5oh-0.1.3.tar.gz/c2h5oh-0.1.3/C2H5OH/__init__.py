"""
C2H5OH Library
==============
Thư viện hỗ trợ các phép biến đổi, mã hóa, giải mã, và các thuật toán sáng tạo khác
dựa trên logic cổ điển và các mô hình đặc biệt do Teone-sensei phát triển.

Module chính:
- core      : chứa các hàm giải mã, encode, biến đổi số học độc quyền
- utils     : các hàm hỗ trợ như kiểm tra tính chẵn/lẻ, làm tròn, mô phỏng vòng lặp,...
- version   : chứa thông tin phiên bản và tác giả
"""

__version__ = "0.1.3"
__author__ = "テオネ先生"
__all__ = [
    "core",
    "utils",
    "version"
]

from . import core
from . import utils
from . import version
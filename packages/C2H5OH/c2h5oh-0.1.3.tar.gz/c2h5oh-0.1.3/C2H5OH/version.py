"""
Thông tin phiên bản của thư viện C2H5OH
"""

__version__ = "0.1.3"
__codename__ = "Ethanol Pulse"
__release_date__ = "2025-08-01"
__author__ = "テオネ先生"
__description__ = (
    "Thư viện mật mã và toán học độc quyền phát triển từ mô hình tuần hoàn cổ điển "
    "với các thuật toán biến dạng sáng tạo và mô phỏng lượng tử giả định."
)

def info():
    return f"""
    📦 Thư viện: C2H5OH
    👨‍🔬 Tác giả: {__author__}
    🧪 Codename: {__codename__}
    🕓 Version : {__version__} ({__release_date__})
    📘 Mô tả   : {__description__}
    """
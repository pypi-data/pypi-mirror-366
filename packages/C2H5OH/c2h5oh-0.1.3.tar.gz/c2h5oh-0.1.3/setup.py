from setuptools import setup, find_packages

setup(
    name="C2H5OH",
    version="0.1.3",
    author="テオネ先生",
    author_email="theonlyone11k2@gmail.com",  # <-- BẮT BUỘC có nếu public PyPI (có thể dùng email phụ)
    description="Thuật toán mã hóa cổ điển và đặc biệt: Tăng-Giảm-Tuần-Hoàn, Hố Đen, mô phỏng BB84.",
    #long_description=open("README.md", encoding="utf-8").read(),
    #long_description_content_type="text/markdown",
    url="https://github.com/teone-sensei/C2H5OH",  # <-- GitHub nếu có
    packages=find_packages(),
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
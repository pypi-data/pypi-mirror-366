from setuptools import setup, find_packages

# README.mdを読み込む
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='funcs-for-pfs',  # PyPIに登録する際のパッケージ名（ハイフンで区切る）
    version='0.1.2',  # パッケージのバージョン
    packages=find_packages(),  # funcs_for_pfs パッケージを自動検出
    install_requires=[
        'toolz',  # 外部パッケージの依存関係
    ],
    long_description=long_description,  # READMEの内容を設定
    long_description_content_type='text/markdown',  # マークダウン形式を指定
    author='kcdlr',
    author_email='nina.aiden168@salmonserenade.com',
    description='This is a collection of handy functions for performing functional pipeline processing (Point-Free Style) in Python.',
    license='CC0',  # ライセンス
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
import os

a = Analysis(['dataset_dl\\main.py'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[('dataset_dl\\extruct.py', '.'),
                    ('resources\\fonts\\NotoSansJP-Regular.otf','resources\\fonts'),
                    ('resources\\fonts\\OFL.txt','resources\\fonts'),
                    ('resources\\dataset-dl.ico', 'resources')],
             hiddenimports=['pywintypes'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          Tree('resources', prefix='resources'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='dataset-dl',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='resources\\dataset-dl.ico')

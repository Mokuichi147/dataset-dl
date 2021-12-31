# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
from os import getcwd
from os.path import join

a = Analysis([join('src','main.py')],
             pathex=[getcwd()],
             binaries=[],
             datas=[(join('src','extruct.py'), '.'),
                    (join('resources','fonts','NotoSansJP-Regular.otf'), join('resources','fonts')),
                    (join('resources','fonts','OFL.txt'), join('resources','fonts')),
                    (join('resources','dataset-dl.ico'), 'resources')],
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
          console=False , icon=join('resources','dataset-dl.ico'))

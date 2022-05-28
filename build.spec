# -*- mode: python ; coding: utf-8 -*-

from os import getcwd
from os.path import join
import sys

block_cipher = None
datas = [(join('src','core.py'), '.'),
         (join('src','extruct.py'), '.'),
         (join('src','utilio.py'), '.'),
         (join('resources','fonts','NotoSansJP-Regular.otf'), join('resources','fonts')),
         (join('resources','fonts','OFL.txt'), join('resources','fonts')),
         (join('resources','dataset-dl.ico'), 'resources')]
icon = None
app_name = 'dataset-dl'

if sys.platform == 'win32':
    datas.append((join('resources','dataset-dl.ico'), 'resources'))
    icon = join('resources','dataset-dl.ico')
elif sys.platform == 'darwin':
    datas.append((join('resources','dataset-dl.icns'), 'resources'))
    icon = join('resources','dataset-dl.icns')
    app_name += '.app'

a = Analysis([join('src','dataset-dl.py')],
             pathex = [getcwd()],
             binaries = [],
             datas = datas,
             hiddenimports = [],
             hookspath = [],
             runtime_hooks = [],
             excludes = [],
             win_no_prefer_redirects = False,
             win_private_assemblies = False,
             cipher = block_cipher,
             noarchive = False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          Tree('resources', prefix='resources'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name = app_name,
          debug = False,
          bootloader_ignore_signals = False,
          strip = False,
          upx = False,
          upx_exclude = [],
          runtime_tmpdir = None,
          console = False,
          icon = icon)
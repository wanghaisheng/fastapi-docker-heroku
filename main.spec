# -*- mode: python ; coding: utf-8 -*-
import sys
from pywebio.utils import pyinstaller_datas
import platform
block_cipher = None
datas = pyinstaller_datas()
if platform.system() == 'Windows':

    a = Analysis(['./main.py'],
hiddenimports=['sqlalchemy.sql.default_comparator'],    
                 pathex=[],
                 binaries=[],
                 datas=datas,
                 
                 hookspath=[],
                 runtime_hooks=[],
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=False,
                 cipher=block_cipher,
                 noarchive=True)
    pyz = PYZ(a.pure, a.zipped_data,
              cipher=block_cipher)
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='link-detect',
              debug=True,
              bootloader_ignore_signals=False,
              strip=False,
              upx=False,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=False,
              icon='icons/spy_128.ico'
              )

elif platform.system() == 'Linux':

    a = Analysis(['./main.py'],
hiddenimports=['sqlalchemy.sql.default_comparator'],    

                 pathex=[],
                 binaries=[],
                 datas=datas,
                 
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
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='link-detect',
              debug=True,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=True)

elif platform.system() == 'Darwin':

    a = Analysis(['./main.py'],
                 pathex=[],
                 binaries=[],
hiddenimports=['sqlalchemy.sql.default_comparator'],    

                 datas=datas,
                 
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
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='link-detect',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=False,
              icon='./icon.icns')
    app = BUNDLE(exe,
                 name='link-detect.app',
                 icon='./icon.icns',
                 bundle_identifier=None)

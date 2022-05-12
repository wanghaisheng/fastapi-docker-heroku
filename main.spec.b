# -*- mode: python ; coding: utf-8 -*-
import sys
import platform
from pywebio.utils import pyinstaller_datas
datas = pyinstaller_datas()
datas=datas.extend(( './assets/', 'assets' ))
uvicorn_hiddenImport=['uvicorn.lifespan.off','uvicorn.lifespan.on','uvicorn.lifespan',
'uvicorn.protocols.websockets.auto','uvicorn.protocols.websockets.wsproto_impl',
'uvicorn.protocols.websockets_impl','uvicorn.protocols.http.auto',
'uvicorn.protocols.http.h11_impl','uvicorn.protocols.http.httptools_impl',
'uvicorn.protocols.websockets','uvicorn.protocols.http','uvicorn.protocols',
'uvicorn.loops.auto','uvicorn.loops.asyncio','uvicorn.loops.uvloop','uvicorn.loops',
'uvicorn.logging','app','sqlalchemy.sql.default_comparator']


block_cipher = None
datas = pyinstaller_datas()
if platform.system() == 'Windows':

    a = Analysis(['./main.py'],
hiddenimports=uvicorn_hiddenImport,    
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
              icon='assets/icons/spy_128.ico'
              )

elif platform.system() == 'Linux':

    a = Analysis(['./main.py'],
hiddenimports=uvicorn_hiddenImport,    

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
hiddenimports=uvicorn_hiddenImport,    

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
              icon='assets/icons/spy_128.ico'
              )
    app = BUNDLE(exe,
                 name='link-detect.app',
              icon='assets/icons/spy_128.ico',
                 bundle_identifier=None)

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['i2sv3.py'],
             pathex=['/Users/Y-S/Desktop/i2s-clean'],
             binaries=[('/System/Library/Frameworks/Tk.framework/Tk', 'tk'), ('/System/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl', 'tcl')],
             datas=[('/Users/Y-S/Desktop/i2s-clean/100x167.jpg', 'data'),('/Users/Y-S/Desktop/i2s-clean/icon-last-01.png', 'data'),('/Users/Y-S/Desktop/i2s-clean/dropdown-01.png', 'data'),('/Users/Y-S/Desktop/i2s-clean/dropdownwhite-01.png', 'data')],
             hiddenimports=[],
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
          [],
          exclude_binaries=True,
          name='i2s',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='i2sv3')
app = BUNDLE(coll,
             name='i2s.app',
             icon='/Users/Y-S/Desktop/i2s-clean/icon.icns',
             bundle_identifier=None)

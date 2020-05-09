# -*- mode: python -*-

block_cipher = None


a = Analysis(['ddb/__main__.py'],
             pathex=[],
             binaries=[],
             datas=[('ddb/feature/jsonnet/lib/*', 'ddb/feature/jsonnet/lib')],
             hiddenimports=['pkg_resources.py2_warn'],  # https://github.com/pypa/setuptools/issues/1963
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=True,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ddb',
          debug=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=True )
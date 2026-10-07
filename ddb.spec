# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# binaryornot (pulled in by cookiecutter) reads its signature lists through
# importlib.resources, so its data files must be shipped alongside the modules.
datas = [
    ('ddb/feature/jsonnet/lib/*', 'ddb/feature/jsonnet/lib'),
    *collect_data_files('binaryornot'),
]

a = Analysis(['ddb/__main__.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=[
                 'ddb.feature.jsonnet.docker',
                 'cookiecutter.extensions',  # https://github.com/cookiecutter/cookiecutter/blob/b155476851448f1858884bf73c177c997319f5a6/cookiecutter/environment.py#L25-L30
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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

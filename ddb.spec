# -*- mode: python -*-

block_cipher = None


a = Analysis(['ddb/__main__.py'],
             pathex=[],
             binaries=[],
             datas=[
                 ('ddb/feature/jsonnet/lib/*', 'ddb/feature/jsonnet/lib')
             ],
             hiddenimports=[
                 'ddb.feature.jsonnet.docker',
                 'pkg_resources.py2_warn',  # https://github.com/pypa/setuptools/issues/1963
                 'cookiecutter.extensions',  # https://github.com/cookiecutter/cookiecutter/blob/b155476851448f1858884bf73c177c997319f5a6/cookiecutter/environment.py#L25-L30
                 'jinja2_time'
             ],
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
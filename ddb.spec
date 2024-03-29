# -*- mode: python -*-

block_cipher = None

# since version 2.2.3, cookiecutter comes with a VERSION.txt file that needs to be included
# as a datafile. This is kind of a temporary hack until a PR for cookiecutter is accepted
# to turn this VERSION.txt file into a regular Python module.

import cookiecutter
from pathlib import Path
COOKIECUTTER_PATH = Path(cookiecutter.__file__).parent.resolve()


a = Analysis(['ddb/__main__.py'],
             pathex=[],
             binaries=[],
             datas=[
                 ('ddb/feature/jsonnet/lib/*', 'ddb/feature/jsonnet/lib'),
                 (str(COOKIECUTTER_PATH / 'VERSION.txt'), 'cookiecutter'),
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
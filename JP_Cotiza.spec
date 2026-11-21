# PyInstaller spec: ejecutar desde la carpeta del proyecto en Windows.
from PyInstaller.utils.hooks import collect_all
mysql_datas, mysql_bins, mysql_hidden = collect_all('mysql.connector')
reportlab_datas, reportlab_bins, reportlab_hidden = collect_all('reportlab')
a = Analysis(
    ['main.py'], pathex=[], binaries=mysql_bins + reportlab_bins,
    datas=[('database/sql', 'database/sql')] + mysql_datas + reportlab_datas,
    hiddenimports=mysql_hidden + reportlab_hidden,
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='JP_Cotiza',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=True,
          console=False, disable_windowed_traceback=False, argv_emulation=False,
          target_arch=None, codesign_identity=None, entitlements_file=None)

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\cursor\\webdriverautomation\\PythonWinAppDriverDemo\\test_fiserv_demo.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\cursor\\webdriverautomation\\PythonWinAppDriverDemo\\windows_automation.py', '.')],
    hiddenimports=['selenium', 'appium', 'appium.webdriver', 'appium.webdriver.common.mobileby'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='fiserv_demo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

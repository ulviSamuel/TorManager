"""
Setup script per py2app
Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['tor_menu.py']
DATA_FILES = ['icon_def.png']  # Se hai le icone, altrimenti lascia vuoto
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',
    'plist': {
        'LSUIElement': True,  # Impedisce all'app di apparire nel Dock
        'CFBundleName': 'TorManager',
        'CFBundleDisplayName': 'Tor Manager',
        'CFBundleIdentifier': 'com.yourname.torctrl',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    },
    'packages': ['rumps', 'requests'],
}

setup(
    name="TorCtrl",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

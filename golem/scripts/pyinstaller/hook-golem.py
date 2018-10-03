from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('golem') + \
                collect_submodules('apps') + \
                ['Cryptodome', 'xml', 'scrypt', 'mock']

datas = [
    ('apps/lux/resources/scripts/docker_luxtask.py',
     'apps/lux/resources/scripts/'),
    ('apps/lux/resources/scripts/docker_luxmerge.py',
     'apps/lux/resources/scripts/'),
]

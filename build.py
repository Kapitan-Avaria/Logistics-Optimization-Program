import PyInstaller.__main__

source_path = 'C:\\Data and Projects\\Vershina\\Logistics-Optimization-Program\\source'

PyInstaller.__main__.run([
    '--onedir',
    '--console',
    '--name', 'VRP_Program',
    '--distpath', '.\\distribution\\dist',
    '--workpath', '.\\distribution\\build',
    '--specpath', '.\\distribution',
    '--contents-directory', 'program_data',
    '--add-data', source_path + '\\static:static',
    '--add-data', source_path + '\\templates:templates',
    '--add-data',  source_path + '\\data:data',
    # '--debug', 'all',
    'source\\main.py'
])

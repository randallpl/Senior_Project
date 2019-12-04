python --version 3>NUL
if errorlevel 1 goto errorNoPython

goto mapReader

:errorNoPython
"%~dp0python-3.8.0-amd64.exe" /quiet InstallAllUsers=1 "TargetDir=%ProgramFiles%\Python3.8" Include_pip=1 Include_test=0 PrependPath=1
goto mapReader

:mapReader
"%ProgramFiles%\Python3.8\python.exe" -m pip install pyqt5 --user
"%ProgramFiles%\Python3.8\python.exe" -m pip install geopy --user
"%ProgramFiles%\Python3.8\python.exe" -m pip install pandas --user
"%ProgramFiles%\Python3.8\python.exe" -m pip install PyQtWebEngine --user
start "Starting Map Reader" "%ProgramFiles%\Python3.8\pythonw.exe" "%~dp0Map_Reader\Starter.py"
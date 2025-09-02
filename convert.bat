@echo off
REM Simple batch script for Windows users to convert OBJ and STL files to POV-Ray
REM Usage: convert.bat input.obj [output.pov] [width] [height]
REM Example: convert.bat model.obj
REM Example: convert.bat model.stl output.pov
REM Example: convert.bat model.obj output.pov 1024 768

if "%1"=="" (
    echo Usage: convert.bat input.obj [output.pov] [width] [height]
    echo Example: convert.bat model.obj
    echo Example: convert.bat model.stl output.pov
    echo Example: convert.bat model.obj output.pov 1024 768
    exit /b 1
)

if "%2"=="" (
    python obj2pov.py "%1" -v
) else if "%3"=="" (
    python obj2pov.py "%1" -o "%2" -v
) else if "%4"=="" (
    python obj2pov.py "%1" -o "%2" -W %3 -v
) else (
    python obj2pov.py "%1" -o "%2" -W %3 -H %4 -v
)


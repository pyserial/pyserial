@set DIRVERNAME=giveio

@echo Installing Windows NT/2k/XP driver: %DIRVERNAME%

@loaddrv install %DIRVERNAME%
@if errorlevel 3 goto error

@loaddrv start %DIRVERNAME%
@if errorlevel 1 goto error
@goto exit

:error
@echo ERROR: Installation of %DIRVERNAME% failed
:exit
@pause

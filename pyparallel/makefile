all:
	./setup.py build --compiler=mingw32
	cp build/lib.win32-2.2/_pyparallel.pyd ./parallel

installer: all
	./setup.py bdist_wininst

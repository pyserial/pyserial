COPT    = -O2 -Wall -g -mno-cygwin

loaddrv.exe: loaddrv.c loaddrv.h
	gcc ${COPT} $< -o $@
	strip $@

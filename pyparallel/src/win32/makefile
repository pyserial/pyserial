CFLAGS  = -mno-cygwin -mdll -O -Wall

.PHONY: clean FORCE

simpleio.dll: simpleio.o
	gcc -mno-cygwin -mdll -static -s $^ -Wl,--export-all-symbols,--kill-at -o $@

clean:
	rm -f simpleio.dll simpleio.o

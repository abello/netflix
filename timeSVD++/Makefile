CFLAGS=-c -O3 -march=native -flto -fwhole-program -Wall -Winline
CFLAGS2=-c -O0 -Wall -Winline -g

all: timesvdpp

timesvdpp: timesvdpp.o
	g++ timesvdpp.o -o timesvdpp

timesvdpp.o: timesvdpp.cpp
	g++ $(CFLAGS) timesvdpp.cpp

clean:
	rm -rf *.o timesvdpp

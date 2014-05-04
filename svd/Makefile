CFLAGS=-c -O3 -Wall -Winline

all: svd

svd: svd.o
	g++ svd.o -o svd

svd.o: svd.cpp
	g++ $(CFLAGS) svd.cpp

clean:
	rm -rf *.o svd

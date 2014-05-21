CFLAGS=-c -O3 -march=native -flto -fwhole-program -Wall -Winline

all: svd

svd: BlockTimePreprocessor.o svd.o
	g++ BlockTimePreprocessor.o svd.o -o svd

svd.o: svd.cpp
	g++ $(CFLAGS) svd.cpp

BlockTimePreprocessor.o: BlockTimePreprocessor.cpp
	g++ $(CFLAGS) BlockTimePreprocessor.cpp

clean:
	rm -rf *.o svd

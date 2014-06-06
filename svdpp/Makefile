CFLAGS=-c -O3 -march=native -mavx -flto -fwhole-program -Wall -Winline
CFLAGS2=-c -O0 -Wall -Winline -g

all: svdpp

svdpp: BlockTimePreprocessor.o svdpp.o
	g++ BlockTimePreprocessor.o svdpp.o -o svdpp

svdpp.o: svdpp.cpp
	g++ $(CFLAGS) svdpp.cpp

BlockTimePreprocessor.o: BlockTimePreprocessor.cpp
	g++ $(CFLAGS2) BlockTimePreprocessor.cpp

clean:
	rm -rf *.o svdpp

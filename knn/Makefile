CFLAGS=-c -O3 -Wall -Winline -g
LDFLAGS=-g

all: knn

svd: knn.o
	g++ $(LDFLAGS) svd.o -o svd

svd.o: knn.cpp
	g++ $(CFLAGS) knn.cpp

clean:
	rm -rf *.o knn

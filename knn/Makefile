CFLAGS=-c -O3 -Wall -Winline

all: knn

svd: knn.o
	g++ svd.o -o svd

svd.o: knn.cpp
	g++ $(CFLAGS) knn.cpp

clean:
	rm -rf *.o knn

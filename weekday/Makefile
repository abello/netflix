CFLAGS= -g -c -O0 -march=native -flto -fwhole-program -Wall -Winline

all: weekday

weekday: weekday.o
	g++ weekday.o -o weekday

weekday.o: weekday.cpp
	g++ $(CFLAGS) weekday.cpp

clean:
	rm -rf *.o weekday

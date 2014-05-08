#ifndef BLOCKTIMEPREPROCESSOR_HPP
#define BLOCKTIMEPREPROCESSOR_HPP

#include <math.h>
#include <fstream>
#include <iostream>
#include <string>
#include <string.h>
#include <sstream>
#include <stdio.h>
#include <cstdlib>
#include <time.h>
#include "Rating.hpp"

#define NUM_USERS 458293
#define NUM_MOVIES 17770
//#define NUM_RATINGS 98291669
#define NUM_RATINGS 99666408
#define NUM_DATES 2243
#define GLOBAL_AVG 3.512599976023349
using namespace std;

class BlockTimePreprocessor{
private:
	short bin_size;
	int num_bins;
    float *bin_offset;
public:
    BlockTimePreprocessor(short bin_size_in, Rating *ratings);
    ~BlockTimePreprocessor() {delete[] bin_offset;};
    void preprocess(Rating *ratings);
    float postprocess(int date, float rating);
};

#endif //BLOCKTIMEPREPROCESSOR_HPP
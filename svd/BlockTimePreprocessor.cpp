#include "BlockTimePreprocessor.hpp"

BlockTimePreprocessor::BlockTimePreprocessor(short bin_size_in, Rating *ratings)
{
	cerr << "Generating bins for BlockTimePreprocessor..." << endl;
    bin_size = bin_size_in;
    num_bins = NUM_DATES / bin_size + 1;
    bin_offset = new float[num_bins];
    double global_avg = 0.0;
    int *bin_cnt = new int[num_bins];
    for (int i = 0; i < num_bins; i++)
    {
    	bin_offset[i] = 0.0;
    	bin_cnt[i] = 0;
    }
    for (int i = 0; i < NUM_RATINGS; i++)
    {
    	int bin = ratings[i].date / bin_size;
    	bin_offset[bin] += ratings[i].rating;
    	global_avg += ratings[i].rating;
    	bin_cnt[bin]++;
    }
    global_avg /= NUM_RATINGS;
    cerr << "GLAVG " << global_avg << endl;
    for (int i = 0; i < num_bins; i++)
    {
    	bin_offset[i] = bin_offset[i] / bin_cnt[i] - global_avg;
    	cerr << i << "  " << bin_offset[i] << endl;
    }
    delete[] bin_cnt;
    cerr << "Generation has terminated!" << endl;
} 


void BlockTimePreprocessor::preprocess(Rating *ratings)
{
	for (int i = 0; i < NUM_RATINGS; i++)
	{
        ratings[i].rating -= bin_offset[ratings[i].date / bin_size];
	}
}

float BlockTimePreprocessor::postprocess(int date, float rating)
{
	return rating + bin_offset[date / bin_size];
}
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
#include "BlockTimePreprocessor.hpp"

#define NUM_USERS 458293
#define NUM_MOVIES 17770
//#define NUM_RATINGS 98291669
#define NUM_RATINGS 99666408
#define GLOBAL_AVG 3.512599976023349
#define GLOBAL_OFF_AVG 0.0481786328365
#define NUM_PROBE_RATINGS 1374739
#define MAX_CHARS_PER_LINE 30
#define NUM_EPOCHS 120
#define NUM_FEATURES 50
#define LRATE_mb 0.003     // m_bias
#define LAMDA_mb 0.0       // m_bias
#define LRATE_ub 0.012     // c_bias
#define LAMDA_ub 0.030     // c_bias
#define LRATE_mf 0.011     // m_factor
#define LAMDA_mf 0.006     // m_factor
#define LRATE_uf 0.006     //  c_factor
#define LAMDA_uf 0.080     //  c_factor
#define LRATE_mw 0.001     // movie_weights
#define LAMDA_mw 0.030     // movie_weights
#define NUM_BINS 5


using namespace std;

class SVDpp {
private:
    double userBias[NUM_USERS]; // b_u
    double movieBias[NUM_MOVIES]; // b_i
    float userFeatures[NUM_FEATURES][NUM_USERS];
    double movieFeatures[NUM_FEATURES][NUM_MOVIES];
    int numRated[NUM_USERS];
    int ratingLoc[NUM_USERS]; // The first instance of users' rating in the ratings matrix

    double movieWeights[NUM_MOVIES][NUM_FEATURES];
    float sumMW[NUM_USERS][NUM_FEATURES];
    double tmpSum[NUM_FEATURES];
    Rating ratings[NUM_RATINGS];
    BlockTimePreprocessor *btp;
//     ofstream rmseOut;
//     ifstream probe;
    inline double predictRating(short movieId, int userId);
    inline double predictRating(short movieId, int userId, int date); 
    void outputRMSE(short numFeats);
    stringstream mdata;
public:
    SVDpp();
    ~SVDpp() { };
    void loadData();
    inline void calcMWSum(int userId);
    void run();
    void output();
    void save();
    void probe();
};

SVDpp::SVDpp() 
{
    int f, j, k;

    mdata << "-F=" << NUM_FEATURES << "-LRT_mb" << LRATE_mb << "-LAM_mb=" << LAMDA_mb << "-LRT_ub=" << LRATE_ub << "-LAM_ub=" << LAMDA_ub << "-LRT_mf=" << LRATE_mf << "-LAM_mf=" << LAMDA_mf << "-LRT_uf=" << LRATE_uf << "-LAM_uf" << LAMDA_uf << "-LRT_mw=" << LRATE_mw << "-LAM_mw=" << LAMDA_mw << "-NBINS=" << NUM_BINS;

    // Init biases
    for (int i = 0; i < NUM_USERS; i++) {
        userBias[i] = (0.1 - (-0.01)) * (((double) rand()) / (double) RAND_MAX) + (-0.01);
    }
    for (int i = 0; i < NUM_MOVIES; i++) {
        movieBias[i] = (-0.1 - (-0.5)) * (((double) rand()) / (double) RAND_MAX) + (-0.5);
    }

    // Init features
    for (f = 0; f < NUM_FEATURES; f++) {
        for (j = 0; j < NUM_USERS; j++) {
            userFeatures[f][j] = (-0.002 - (-0.01)) * (((double) rand()) / (double) RAND_MAX) + (-0.01);
        }
        for (k = 0; k < NUM_MOVIES; k++) {
            movieFeatures[f][k] = (0.02 - 0.01) * (((double) rand()) / (double) RAND_MAX) + 0.01;
        }
    }

    // Initialize numRated array to all zeros.
    for (int i = 0; i < NUM_USERS; i++) {
        numRated[i] = 0;
    }
}

void SVDpp::loadData() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    int date;
    int rating;
    int i = 0;
    int curUser = 0;
    ifstream trainingDta ("../processed_data/train+probe.dta"); 
    if (trainingDta.fail()) {
        cout << "train.dta: Open failed.\n";
        exit(-1);
    }

    // Initialize ratingLoc to -1
    for (i = 0; i < NUM_USERS; i++) {
        ratingLoc[i] = -1;
    }
    i = 0;

    while (getline(trainingDta, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1; // sub 1 for zero indexed
        movieId = atoi(strtok(NULL, " ")) - 1;
        date = atoi(strtok(NULL, " ")); 
        rating = atoi(strtok(NULL, " "));
        ratings[i].userId = userId;
        ratings[i].movieId = (short) movieId;
        ratings[i].date = (short) date;
        ratings[i].rating = rating;
//         ratings[i].cache = 0.0; // set to 0 temporarily.
        if (ratingLoc[userId] == -1) {
            ratingLoc[userId] = i; // Store the pointer to this rating for this user.
        }
        i++;
        if (curUser == userId) {
            numRated[curUser]++; 
        }
        else {
            numRated[userId]++;
            curUser = userId;
        }
    }
    
    // Initialize movie weights
    for (int i = 0; i < NUM_MOVIES; i++) {
        for (int j = 0; j < NUM_FEATURES; j++) {
            movieWeights[i][j] = (0.1 - 0.0) * (((double) rand()) / (double) RAND_MAX) + 0.0;
        }
    }

    trainingDta.close();
    btp = new BlockTimePreprocessor(NUM_BINS, ratings);
    btp->preprocess(ratings);
}

void SVDpp::run() {
    int f, i, userId, k;
    double err, p, tmpMW, sq;
    double uBias, mBias;
    double uf, mf;
    Rating *rating;
    int userLast = -1;
    short movieId;
    clock_t time, tf, tmw, tp, ts, tot_tf, tot_tmw, tot_tp, tot_ts;

    // Precalculate the sumMW values for all users.
//     for (i = 0; i < NUM_USERS; i++) {
//         calcMWSum(i);
//     }

    time = clock();
    
    for (int z = 0; z < NUM_EPOCHS; z++) {
        sq = 0.0;
        tot_tf = 0;
        tot_tmw = 0;
        tot_tp = 0;
        tot_ts = 0;

        k = 0;
        for (i = 0; i < NUM_RATINGS; i++) {
                
            rating = ratings + i;
            movieId = rating->movieId; 
            userId = rating->userId;

            // This will be true right when we encounter the next user in the ratings list.
            if (userId != userLast) {
                calcMWSum(userId);
                for (f = 0; f < NUM_FEATURES; f++) {
                    tmpSum[f] = 0.0;
                }
            }

//             tp = clock();
            p = predictRating(movieId, userId);
            err = rating->rating - p;
            sq += err * err;
//             tot_tp += clock() - tp;

//             ts = clock();
//             tot_ts += clock() - ts;
            
            // train biases
            uBias = userBias[userId];
            mBias = movieBias[movieId];
            userBias[userId] += (LRATE_ub * (err - LAMDA_ub * uBias));
            movieBias[movieId] += (LRATE_mb * (err - LAMDA_mb * mBias));          
            
//             tf = clock();
            for (f = 0; f < NUM_FEATURES; f++) {
                uf = userFeatures[f][userId];
                mf = movieFeatures[f][movieId];
                userFeatures[f][userId] += (LRATE_uf * (err * mf - LAMDA_uf * uf)); 
                movieFeatures[f][movieId] += 
                    (LRATE_mf * (err * (uf + (1.0 / sqrt(numRated[userId])) * sumMW[userId][f]) - LAMDA_mf * mf));
                tmpSum[f] += (err * numRated[userId] * mf);
            }
//             tot_tf =+ clock() - tf;
            
//             tmw = clock();
            // Train movie weights
            if (userId != userLast) {
                rating = &ratings[ratingLoc[userId]];
                k = 0;
                while (k < numRated[userId]) {
                    movieId = rating->movieId;
                    for (f = 0; f < NUM_FEATURES; f++) {
                        tmpMW = movieWeights[movieId][f];
                        movieWeights[movieId][f] += (LRATE_mw * (tmpSum[f] - LAMDA_mw * tmpMW)); 
                        // Update sumMW so we don't have to recalculate it entirely.
                        sumMW[userId][f] += movieWeights[movieId][f] - tmpMW;
                    }
                    rating++;
                    k++;
                }
                userLast = userId;
            }
//             tot_tmw += clock() - tmw;
        }

        for (i = 0; i < NUM_USERS; i++) {
            calcMWSum(i);
        }

        time = clock() - time;
        cout << "Iteration " << z << " completed." << endl;
        cout << "RMSE: " << sqrt(sq/NUM_RATINGS) << " -- " << ((float) time)/CLOCKS_PER_SEC << endl;
        cout << "TF: " << ((float) tot_tf)/(CLOCKS_PER_SEC) << endl;
        cout << "TMW: " << ((float) tot_tmw)/(CLOCKS_PER_SEC) << endl;
        cout << "TP: " << ((float) tot_tp)/(CLOCKS_PER_SEC) << endl;
        cout << "TS: " << ((float) tot_ts)/(CLOCKS_PER_SEC) << endl;
        cout << "=================================" << endl;

    }
}

inline void SVDpp::calcMWSum(int userId) {
    int movieId;
    int k = 0;
    Rating *rating = &(ratings[ratingLoc[userId]]);
    for (int f = 0; f < NUM_FEATURES; f++) {
        sumMW[userId][f] = 0.0;
    }
    while (k < numRated[userId]) {
        movieId = rating->movieId; 
        for (int f = 0; f < NUM_FEATURES; f++) {
            sumMW[userId][f] += movieWeights[movieId][f];
        }
        rating++;
        k++;
    }
}

// Used for train
inline double SVDpp::predictRating(short movieId, int userId) {
    double sum = 0.0;
    double norm = 1.0 / sqrt(numRated[userId]);
    sum += userBias[userId] + movieBias[movieId];
    for (int f = 0; f < NUM_FEATURES; f++) {
        sum += movieFeatures[f][movieId] * (userFeatures[f][userId] + norm * sumMW[userId][f]);
    }
    sum = sum > 5 ? 5 : sum;
    sum = sum < 1 ? 1 : sum;
    return sum;
}

inline double SVDpp::predictRating(short movieId, int userId, int date) {
    double sum = 0.0;
    double norm = 1.0 / sqrt(numRated[userId]);
    sum += userBias[userId] + movieBias[movieId];
    for (int f = 0; f < NUM_FEATURES; f++) {
        sum += movieFeatures[movieId][f] * (userFeatures[userId][f] + norm * sumMW[userId][f]);
    }

    sum = btp->postprocess(date, sum);

    sum = sum > 5 ? 5 : sum;
    sum = sum < 1 ? 1 : sum;
    return sum;
}

/* Generate out of sample RMSE for the current number of features, then
   write this to a rmseOut. */
void SVDpp::outputRMSE(short numFeats) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId, movieId, date;
    double predicted, actual; // ratings
    double err, sq, rmse;
    stringstream fname;
    fname << "rmseOut" << mdata.str();
    ofstream rmseOut(fname.str().c_str(), ios::app);
    ifstream probe("../results/probe.dta");
    if (!rmseOut.is_open() || !probe.is_open()) {
        cout << "Files for RMSE output: Open failed.\n";
        exit(-1);
    }
    sq = 0;
    while (getline(probe, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) -1;
        movieId = atoi(strtok(NULL, " ")) - 1;
        date = atoi(strtok(NULL, " "));
        actual = (double) atoi(strtok(NULL, " "));
        predicted = predictRating(movieId, userId, date);
        err = actual - predicted;
        sq += err * err;
    }
    rmse = sqrt(sq/NUM_PROBE_RATINGS);
    rmseOut << rmse << '\n';
}

void SVDpp::output() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    int date;
    double rating;
    stringstream fname;
    fname << "../results/output" << mdata.str();

    ifstream qual ("../processed_data/qual.dta");
    ofstream out (fname.str().c_str(), ios::trunc); 
    if (qual.fail() || out.fail()) {
        cout << "qual.dta: Open failed.\n";
        exit(-1);
    }
    while (getline(qual, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1;
        movieId = (short) atoi(strtok(NULL, " ")) - 1;
        date = atoi(strtok(NULL, " "));
        rating = predictRating(movieId, userId, date);
        out << rating << '\n';
    }
}

/* Save the calculated features and other parameters. */
void SVDpp::save() {
    int i, j;
    stringstream fname;
    fname << "../results/features" << mdata.str();

    ofstream saved(fname.str().c_str(), ios::trunc);
    if (saved.fail()) {
        cout << "features.svd: Open failed.\n";
        exit(-1);
    }
    for (i = 0; i < NUM_USERS; i++) {
        for (j = 0; j < NUM_FEATURES; j++) {
            saved << userFeatures[j][i] << ' ';
        }
        saved << '\n';
    }
    for (i = 0; i < NUM_MOVIES; i++) {
        for (j = 0; j < NUM_FEATURES; j++) {
            saved << movieFeatures[j][i] << ' ';
        }
        saved << '\n';
    }
    saved.close();
}

/* Save the results of the probe */
void SVDpp::probe() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    stringstream fname;
    int userId, movieId, date;
    fname << "../results/probe" << mdata.str();

    ofstream saved(fname.str().c_str(), ios::trunc);
    ifstream p("../processed_data/probe.dta");
    if (saved.fail()) {
        cout << "probe-: Open failed.\n";
        exit(-1);
    }
    if (p.fail()) {
        cout << "probe.dta-: Open failed.\n";
        exit(-1);
    }

    // For each line of probe, parse it and predict rating
    while (getline(p, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1; // sub 1 for zero indexed
        movieId = (short) atoi(strtok(NULL, " ")) - 1;
        date = atoi(strtok(NULL, " ")); 
        
        saved << predictRating(movieId, userId, date) << "\n";
    }

    saved.close();
    p.close();
}

int main() {
    SVDpp *svdpp = new SVDpp();
    svdpp->loadData();
    svdpp->run();
    svdpp->output();
//     svdpp->save();
//     svdpp->probe();
    cout << "SVD++ completed.\n";

    return 0;
}

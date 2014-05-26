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
// #define NUM_RATINGS 98291669
#define NUM_RATINGS 99666408
#define GLOBAL_AVG 3.512599976023349
#define GLOBAL_OFF_AVG 0.0481786328365
#define NUM_PROBE_RATINGS 1374739
#define MAX_CHARS_PER_LINE 30
#define NUM_EPOCHS 25 
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
#define LRATE_bl 0.01 // Baseline LRATE
#define LAMDA_bl 0.030
#define BETA 0.4
#define MIN_TIME
#define MAX_TIME
#define PER_BIN (MAX_TIME - MIN_TIME + 1) / BINS
#define BINS 30


using namespace std;

class TimeSVDpp {
private:
    double userBias[NUM_USERS]; // b_u
    double movieBias[NUM_MOVIES]; // b_i
    double alpha[NUM_USERS]; // alpha_u
    double t_u[NUM_USERS]; // t_u, precalculated before run()
//     double *userBins[NUM_USERS]; // b_{u, t}
    double movieBins[NUM_MOVIES][BINS]; // b_{i, Bin(t)}
    float userFeatures[NUM_FEATURES][NUM_USERS];
    double movieFeatures[NUM_FEATURES][NUM_MOVIES];
    int numRated[NUM_USERS];
    int ratingLoc[NUM_USERS]; // The first instance of users' rating in the ratings matrix

    double movieWeights[NUM_MOVIES][NUM_FEATURES];
    float sumMW[NUM_USERS][NUM_FEATURES];
    double tmpSum[NUM_FEATURES];
    Rating ratings[NUM_RATINGS];
//     ofstream rmseOut;
//     ifstream probe;
    inline double predictRating(short movieId, int userId, int time, short timeIdx);
    inline double predictRating(short movieId, int userId, short time);
    void outputRMSE(short numFeats);
    stringstream mdata;
public:
    TimeSVDpp();
    ~TimeSVDpp() { };
    void loadData();
    inline void calcMWSum(int userId);
    void run();
    void output(int iter);
    void save();
    void probe(int iter);
    void probeRMSE();
    inline double dev(int userId, short time);
    inline int bin(short time);
};

TimeSVDpp::TimeSVDpp() 
{
    int f, j, k;

    mdata << "-F=" << NUM_FEATURES <<  "-NR=" << NUM_RATINGS << "-NB=" << BINS << "-SD";

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

void TimeSVDpp::loadData() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId, movieId, time, rating;
    int j, i = 0;
    int curUser = 0;
    int curTime = -1;
    int userDays[NUM_USERS]; // count number of unique days for each user's ratings

    ifstream trainingDta ("../processed_data/train+probe.dta"); 
//     ifstream trainingDta ("../processed_data/train.dta"); 
    if (trainingDta.fail()) {
        cout << "train.dta: Open failed.\n";
        exit(-1);
    }

    for (j = 0; j < NUM_USERS; j++) {
        userDays[j] = 0; 
        ratingLoc[j] = -1; // Initialize ratingLoc to -1
        t_u[j] = 0.0; // Initialize the t_u array to all zeros. 
    }

    while (getline(trainingDta, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1; // sub 1 for zero indexed
        movieId = atoi(strtok(NULL, " ")) - 1;
        time = atoi(strtok(NULL, " ")); 
        rating = atoi(strtok(NULL, " "));
        ratings[i].userId = userId;
        ratings[i].movieId = (short) movieId;
        ratings[i].time = (short) time;
        ratings[i].rating = rating;

        t_u[userId] += time;

        if (ratingLoc[userId] == -1) {
            ratingLoc[userId] = i; // Store the pointer to this rating for this user.
        }
        if (curUser == userId) {
            if (time != curTime) {
                userDays[userId]++; 
                curTime = time;
            }
            numRated[curUser]++; 
        }
        else {
            numRated[userId]++;
            userDays[userId]++;
            curTime = time;
            curUser = userId;
        }
        i++;
    }
    trainingDta.close();
    
    // Initialize movie weights
    for (i = 0; i < NUM_MOVIES; i++) {
        for (j = 0; j < NUM_FEATURES; j++) {
            movieWeights[i][j] = (0.1 - 0.0) * (((double) rand()) / (double) RAND_MAX) + 0.0;
        }
        for (j = 0; j < BINS; j++) {
            movieBins[i][j] = 0.1 * (((double) rand()) / (double) RAND_MAX);
        }
    }

    // Initialize userBins arrays.
    for (i = 0 ; i < NUM_USERS; i++) {
//         userBins[i] = new double[userDays[i]];
//         for (j = 0; j < userDays[i]; j++) {
//             userBins[i][j] = 0.1 * (((double) rand()) / (double) RAND_MAX);
//         }
        // Divide time sums in t_u[userId] by numRated[userId] to get means
        t_u[i] /= (double) numRated[i];
        // Initialize alpha array.
        alpha[i] = 0.1 * (((double) rand()) / (double) RAND_MAX);
    }
}

void TimeSVDpp::run() {
    int f, i, userId, k;
    double err, p, tmpMW, sq;
    double uBias, mBias;
    double uf, mf, reg;
    Rating *rating;
    short movieId, time;
    int curTime, binIdx, tmpbin;
//     clock_t time, tf, tmw, tp, ts, tot_tf, tot_tmw, tot_tp, tot_ts;
    clock_t tf, tmw, tp, ts, tot_tf, tot_tmw, tot_tp, tot_ts;

    // Precalculate the sumMW values for all users.
//     for (i = 0; i < NUM_USERS; i++) {
//         calcMWSum(i);
//     }

    
    for (int z = 0; z < NUM_EPOCHS; z++) {
        sq = 0.0;
        tot_tf = 0;
        tot_tmw = 0;
        tot_tp = 0;
        tot_ts = 0;
        reg = pow(0.9, z);

        k = 0;
        i = 0;
//         time = clock();
        while (i < NUM_RATINGS) {
//             cout << "user: " << i << endl;
//             cout << "numRated: " << numRated[i] << endl;
//             cout << endl;
                
            rating = ratings + i;
            userId = rating->userId;

            // This will be true right when we encounter the next user in the ratings list.
            calcMWSum(userId);
            for (f = 0; f < NUM_FEATURES; f++) {
                tmpSum[f] = 0.0;
            }
        
//             binIdx = -1; // userBins index
//             curTime = -1;
            // For each movie rated by userId
            for (k = 0; k < numRated[userId]; k++) {
                rating = ratings + k + i;
                movieId = rating->movieId; 
                time = rating->time;
                p = predictRating(movieId, userId, time);
                err = rating->rating - p;
                sq += err * err;

//                 // Update userBins, b_{i, t}
//                 if (curTime != time) {
//                     curTime = time;
//                     binIdx++;
//                 }

                // Update alphas
                alpha[userId] += (reg * LRATE_bl * (dev(userId, time) * err - LAMDA_bl * alpha[userId]));

//                 // Update userBins
//                 userBins[userId][binIdx] += (reg * LRATE_bl * (err - LAMDA_bl * userBins[userId][binIdx]));

                // Update movieBins
                tmpbin = bin(time);
                movieBins[movieId][tmpbin] += (reg * LRATE_bl * (err - LAMDA_bl * movieBins[movieId][tmpbin]));
            
                // train biases
                uBias = userBias[userId];
                mBias = movieBias[movieId];
                userBias[userId] += (reg *LRATE_ub * (err - LAMDA_ub * uBias));
                movieBias[movieId] += (reg * LRATE_mb * (err - LAMDA_mb * mBias));          
                
                for (f = 0; f < NUM_FEATURES; f++) {
                    uf = userFeatures[f][userId];
                    mf = movieFeatures[f][movieId];
                    userFeatures[f][userId] += (reg * LRATE_uf * (err * mf - LAMDA_uf * uf)); 
                    movieFeatures[f][movieId] += 
                        (reg * LRATE_mf * (err * (uf + (1.0 / sqrt(numRated[userId])) * sumMW[userId][f]) - LAMDA_mf * mf));
                    tmpSum[f] += (err * (1.0 / sqrt(numRated[userId])) * mf);
                }
            }
            
            k = 0;
            // For every movie rated by userId
            for (k = 0; k < numRated[userId]; k++) {
            // Train movie weights
                rating = ratings + k + i;
                movieId = rating->movieId;
                for (f = 0; f < NUM_FEATURES; f++) {
                    tmpMW = movieWeights[movieId][f];
                    movieWeights[movieId][f] += (reg * LRATE_mw * (tmpSum[f] - LAMDA_mw * tmpMW)); 
                    // Uptime sumMW so we don't have to recalculate it entirely.
                    sumMW[userId][f] += movieWeights[movieId][f] - tmpMW;
                }
            }
            
            i += numRated[userId];
        } // Finished all users

        for (i = 0; i < NUM_USERS; i++) {
            calcMWSum(i);
        }

//         time = clock() - time;
        cout << "Iteration " << z << " completed." << endl;
        cout << "RMSE: " << sqrt(sq/NUM_RATINGS); //<< " -- " << ((float) time)/CLOCKS_PER_SEC << endl;
        probeRMSE();

        // Save probe for this iter
//         probe(z);
        output(z);

        cout << "=================================" << endl;

    }
}

inline void TimeSVDpp::calcMWSum(int userId) {
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

inline double TimeSVDpp::dev(int userId, short time) {
    short diff = time - t_u[userId];
    int sign = diff > 0 ? 1 : -1;
    return sign * pow(sign * diff, BETA);

}

inline int TimeSVDpp::bin(short time) {
    int bin = time / PER_BIN;
    if (bin == BINS)
        bin--;
    return bin;
}

// Used for train
inline double TimeSVDpp::predictRating(short movieId, int userId, int time, short timeIdx) {
    double sum = GLOBAL_AVG;
    double norm = 1.0 / sqrt(numRated[userId]);
    sum += userBias[userId] + movieBias[movieId] + alpha[userId] * dev(userId, time) + 
        movieBins[movieId][bin(time)];
//         userBins[userId][timeIdx] + movieBins[movieId][bin(time)];
    for (int f = 0; f < NUM_FEATURES; f++) {
        sum += movieFeatures[f][movieId] * (userFeatures[f][userId] + norm * sumMW[userId][f]);
    }
    sum = sum > 5 ? 5 : sum;
    sum = sum < 1 ? 1 : sum;
    return sum;
}

inline double TimeSVDpp::predictRating(short movieId, int userId, short time) {
    double sum = GLOBAL_AVG;
    double norm = 1.0 / sqrt(numRated[userId]);
    sum += userBias[userId] + movieBias[movieId] + alpha[userId] * dev(userId, time) + 
        movieBins[movieId][bin(time)];
//         userBins[userId][time] + movieBins[movieId][bin(time)];
    for (int f = 0; f < NUM_FEATURES; f++) {
        sum += movieFeatures[f][movieId] * (userFeatures[f][userId] + norm * sumMW[userId][f]);
    }
    sum = sum > 5 ? 5 : sum;
    sum = sum < 1 ? 1 : sum;
    return sum;
}

/* Generate out of sample RMSE for the current number of features, then
   write this to a rmseOut. */
void TimeSVDpp::outputRMSE(short numFeats) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId, movieId, time;
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
        time = atoi(strtok(NULL, " "));
        actual = (double) atoi(strtok(NULL, " "));
        predicted = predictRating(movieId, userId, time);
        err = actual - predicted;
        sq += err * err;
    }
    rmse = sqrt(sq/NUM_PROBE_RATINGS);
    rmseOut << rmse << '\n';
}

void TimeSVDpp::output(int iter = NUM_EPOCHS) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    int time;
    double rating;
    stringstream fname;
    fname << "../results/output" << iter << mdata.str();

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
        time = atoi(strtok(NULL, " "));
        rating = predictRating(movieId, userId, time);
        out << rating << '\n';
    }
}

/* Save the calculated features and other parameters. */
void TimeSVDpp::save() {
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
void TimeSVDpp::probe(int iter = NUM_EPOCHS) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    stringstream fname;
    int userId, movieId, time;
    fname << "../results/probe" << iter << mdata.str();

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
        time = atoi(strtok(NULL, " ")); 
        
        saved << predictRating(movieId, userId, time) << "\n";
    }

    saved.close();
    p.close();
}

// Calculates RMSE for probe
void TimeSVDpp::probeRMSE() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    stringstream fname;
    int userId, movieId, time, rating, num_probe;
    double sq = 0, err = 0;

    ifstream p("../processed_data/probe.dta");
    if (p.fail()) {
        cout << "probe.dta-: Open failed.\n";
        exit(-1);
    }

    num_probe = 0;
    // For each line of probe, parse it and predict rating
    while (getline(p, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1; // sub 1 for zero indexed
        movieId = (short) atoi(strtok(NULL, " ")) - 1;
        time = atoi(strtok(NULL, " ")); 
        
        // Get actual rating
        rating = atoi(strtok(NULL, " "));
        
        err = predictRating(movieId, userId, time) - rating;
        sq += err * err;
        num_probe ++;
    }

    cout << sqrt(sq/num_probe) << endl;
    p.close();
}

int main() {
    TimeSVDpp *tsvdpp = new TimeSVDpp();
    tsvdpp->loadData();
    tsvdpp->run();
    tsvdpp->output();
//     tsvdpp->save();
//     tsvdpp->probe();
    cout << "TimeSVD++ completed.\n";

    return 0;
}

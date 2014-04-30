#include <math.h>
#include <fstream>
#include <iostream>
#include <string>
#include <string.h>
#include <sstream>
#include <stdio.h>
#include <cstdlib>
#include <time.h>

#define NUM_USERS 458293
#define NUM_MOVIES 17770
#define NUM_RATINGS 98291669
#define GLOBAL_AVG 3.512599976023349
#define GLOBAL_OFF_AVG 0.0481786328365
#define NUM_PROBE_RATINGS 1374739
#define MAX_CHARS_PER_LINE 30
#define NUM_FEATURES 60
#define MIN_EPOCHS 120
#define MAX_EPOCHS 170
#define MIN_IMPROVEMENT 0.0001
#define LRATE 0.001
#define K_MOVIE 25
#define K 0.02
#define FEAT_INIT GLOBAL_AVG/NUM_FEATURES

// calculate and save out of sample RMSE
// #define RMSEOUT

// Whether to traine features one by one or not
// TODO: All at a time doesn't work, gotta fix cache
#define ONEBYONE 


// Created using this article and some code: http://www.timelydevelopment.com/demos/NetflixPrize.aspx

using namespace std;

struct Rating {
    int userId;
    short movieId;
    short rating;
    double cache;
};

class SVD {
private:
    double movieAvgs[NUM_MOVIES];
    double userOffsets[NUM_USERS];
    double userFeatures[NUM_FEATURES][NUM_USERS];
    double movieFeatures[NUM_FEATURES][NUM_MOVIES];
    Rating ratings[NUM_RATINGS];
//     ofstream rmseOut;
//     ifstream probe;
    double predictRating(short movieId, int userId, int feature, double cached, bool addTrailing);
    double predictRating(short movieId, int userId); 
    void outputRMSE(short numFeats);
    stringstream mdata;
public:
    SVD();
    ~SVD() { };
    void loadData();
    void computeBaselines();
    void run();
    void output();
    void save();
};

SVD::SVD() 
//     : rmseOut("rmseOut.txt", ios::trunc), probe("../processed_data/probe.dta")
{
    int f, j, k;
#ifdef ONEBYONE
    mdata << "-OBO-F=" << NUM_FEATURES << "-E=" << MIN_EPOCHS << "," << MAX_EPOCHS << "-k=" << K << "-l=" << LRATE;
#else
    mdata << "-ALL-F=" << NUM_FEATURES << "-E=" << MIN_EPOCHS << "," << MAX_EPOCHS << "-k=" << K << "-l=" << LRATE;

#endif
//     srand(time(NULL));
    for (f = 0; f < NUM_FEATURES; f++) {
        for (j = 0; j < NUM_USERS; j++) {
//             userFeatures[f][j] = ((rand() % 201) - 100) / 1000.0;
            userFeatures[f][j] = FEAT_INIT;
        }
        for (k = 0; k < NUM_MOVIES; k++) {
//             movieFeatures[f][k] = ((rand() % 201) - 100) / 1000.0;
            movieFeatures[f][k] = FEAT_INIT;
        }
    }
}

void SVD::loadData() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    int time;
    int rating;
    int i = 0;
    ifstream trainingDta ("../processed_data/train.dta"); 
    if (trainingDta.fail()) {
        cout << "train.dta: Open failed.\n";
        exit(-1);
    }
    while (getline(trainingDta, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1; // sub 1 for zero indexed
        movieId = atoi(strtok(NULL, " ")) - 1;
        time = atoi(strtok(NULL, " ")); 
        rating = atoi(strtok(NULL, " "));
        ratings[i].userId = userId;
        ratings[i].movieId = (short) movieId;
        ratings[i].rating = rating;
        ratings[i].cache = 0.0;
        i++;
    }
    trainingDta.close();
}

void SVD::computeBaselines() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int cur = 0;
    int iter = 0;
    int curCount = 0;
    int userId, time, rating, i, movieId;
    double ratingSum = 0.0;
    double offSum = 0.0; // Sum of offsets for a user;
    Rating *ratingPtr;
    ifstream trainingDtaMu("../processed_data/train-mu.dta");
    if (trainingDtaMu.fail()) {
        cout << "train-mu: Open failed.\n";
        exit(-1);
    }
    // Compute movie averages.
    while (getline(trainingDtaMu, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1;
        iter = atoi(strtok(NULL, " ")) - 1;
        time = atoi(strtok(NULL, " "));
        rating = atoi(strtok(NULL, " "));
        if (iter == cur) {
            curCount++;
            ratingSum += 1.0 * rating;
        }
        else {
            movieAvgs[cur] = (GLOBAL_AVG * K_MOVIE + ratingSum) / (K_MOVIE + curCount);
            curCount = 1; // Counting the current new movie;
            ratingSum = (1.0) * rating;
            cur = iter;
        }
    }
    trainingDtaMu.close();

    cur = 0;
    iter = 0;
    curCount = 0;
    // Compute user offsets
    for (i = 0; i < NUM_RATINGS; i++) {
        ratingPtr = ratings + i;
        iter = ratingPtr->userId;
        movieId = ratingPtr->movieId;
        if (iter == cur) {
            offSum += (1.0 * ratingPtr->rating) - movieAvgs[movieId]; 
            curCount++;
        }
        else { 
            userOffsets[cur] = (GLOBAL_OFF_AVG * K_MOVIE + offSum) / (K_MOVIE + curCount);
            offSum = (1.0 * ratingPtr->rating) - movieAvgs[movieId];
            curCount = 1;
            cur = iter;
        }
    }
}

void SVD::run() {
    int f, e, i, userId;
    double sq, rmse, rmse_last, err, p;
    short movieId;
    double uf, mf;
    Rating *rating;

    rmse_last = 0;
    rmse = 2.0;

#ifdef ONEBYONE
    for (f = 0; f < NUM_FEATURES; f++) {
        cout << "Computing feature " << f << ".\n";
        for (e = 0; ((e < MIN_EPOCHS)  || (rmse <= rmse_last - MIN_IMPROVEMENT)) && (e < MAX_EPOCHS); e++) {
            cout << rmse_last << "\n";
            rmse_last = rmse;
            sq = 0;
            for (i = 0; i < NUM_RATINGS; i++) {
                rating = ratings + i;
                movieId = rating->movieId;
                userId = rating->userId;
                p = predictRating(movieId, userId, f, rating->cache, true);
                err = (1.0 * rating->rating - p); 
                sq += err * err;
                uf = userFeatures[f][userId];
                mf = movieFeatures[f][movieId];

                userFeatures[f][userId] += (LRATE * (err * mf - K * uf));
                movieFeatures[f][movieId] += (LRATE * (err * uf - K * mf));
            }
            rmse = sqrt(sq/NUM_RATINGS);
        }
#ifdef RMSEOUT
        outputRMSE(f);
#endif
        for (i = 0; i < NUM_RATINGS; i++) {
            rating = ratings + i;
            rating->cache = predictRating(rating->movieId, rating->userId, f, rating->cache, false);
        }
    }
#endif // ONEBYONE


#ifndef ONEBYONE

    for (e = 0; ((e < MIN_EPOCHS)  || (rmse <= rmse_last - MIN_IMPROVEMENT)) && (e < MAX_EPOCHS); e++) {
        for (f = 0; f < NUM_FEATURES; f++) {
            cout << "Computing feature " << f << ".\n";
            cout << rmse_last << "\n";
            rmse_last = rmse;
            sq = 0;
            for (i = 0; i < NUM_RATINGS; i++) {
                rating = ratings + i;
                movieId = rating->movieId;
                userId = rating->userId;
                p = predictRating(movieId, userId);
                err = (1.0 * rating->rating - p); 
                sq += err * err;
                uf = userFeatures[f][userId];
                mf = movieFeatures[f][movieId];

                userFeatures[f][userId] += (LRATE * (err * mf - K * uf));
                movieFeatures[f][movieId] += (LRATE * (err * uf - K * mf));
            }
            rmse = sqrt(sq/NUM_RATINGS);
        }
#ifdef RMSEOUT
        outputRMSE(f);
#endif
    }

#endif // ONEBYONE


}

inline double SVD::predictRating(short movieId, int userId, int feature, double cached, bool addTrailing) {
    double sum = cached;

    sum += userFeatures[feature][userId] * movieFeatures[feature][movieId];
    if (addTrailing) {
        sum += (NUM_FEATURES - feature - 1) * (FEAT_INIT * FEAT_INIT);
    }


    if (sum > 5) {
        sum = 5;
    }
    else if (sum < 1) {
        sum = 1;
    }

    return sum;
}

inline double SVD::predictRating(short movieId, int userId) {
    int f;
    double sum = 0;
    for (f = 0; f < NUM_FEATURES; f++) {
        sum += userFeatures[f][userId] * movieFeatures[f][movieId];
    }

    if (sum > 5) {
        sum = 5;
    }
    else if (sum < 1) {
        sum = 1;
    }
    return sum;
}

/* Generate out of sample RMSE for the current number of features, then
   write this to a rmseOut. */
void SVD::outputRMSE(short numFeats) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId, movieId, time;
    double predicted, actual; // ratings
    double err, sq, rmse;
    stringstream fname;
#ifdef ONEBYONE
    fname << "rmseOut-OBO" << mdata;
#else
    fname << "rmseOut-ALL-F=" << mdata;
#endif
    ofstream rmseOut(fname.str().c_str(), ios::app);
    ifstream probe("../processed_data/probe.dta");
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
        predicted = predictRating(movieId, userId);
        err = actual - predicted;
        sq += err * err;
    }
    rmse = sqrt(sq/NUM_PROBE_RATINGS);
    rmseOut << rmse << '\n';
}

void SVD::output() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    double rating;
    stringstream fname;
    fname << "output" << mdata;

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
        rating = predictRating(movieId, userId);
        out << rating << '\n';
    }
}

/* Save the calculated features and other parameters. */
void SVD::save() {
    int i, j;
    stringstream fname;
    fname << "features" << mdata;

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

int main() {
    SVD *svd = new SVD();
    svd->loadData();
    svd->computeBaselines();
    svd->run();
    svd->output();
    svd->save();
    cout << "SVD completed.\n";

    return 0;
}

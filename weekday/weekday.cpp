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
#define NUM_EPOCHS 30
#define NUM_FEATURES 300
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
#define LRATE_mbn 0.012
#define LAMDA_mbn 0.060
#define NUM_BINS 5

#define NUM_WEEKS 321


using namespace std;


class Weekday {
private:
    double userBias[NUM_USERS]; // b_u
    double movieBias[NUM_MOVIES]; // b_i
    float userFeatures[NUM_USERS][NUM_FEATURES];
    double movieFeatures[NUM_MOVIES][NUM_FEATURES];
    double movieBins[NUM_MOVIES][NUM_BINS];
    int numRated[NUM_USERS];
    int ratingLoc[NUM_USERS]; // The first instance of users' rating in the ratings matrix

    double movieWeights[NUM_MOVIES][NUM_FEATURES];
    float sumMW[NUM_USERS][NUM_FEATURES];
    double tmpSum[NUM_FEATURES];
    Rating ratings[NUM_RATINGS];
//     ofstream rmseOut;
//     ifstream probe;
    inline double predictRating(short movieId, int userId, short date); 
    int bin(short date);
    void outputRMSE(short numFeats);
    stringstream mdata;

    float m_users[NUM_USERS][7];
    float m_movies[NUM_MOVIES][7];
public:
    Weekday();
    ~Weekday() { };
    void loadData();
    inline void calcMWSum(int userId);
    void run();
    void output(int iter);
    void save();
    void probe(int iter);
    void probeRMSE();
};

Weekday::Weekday() 
{
    int f, j, k;

    mdata << "-F=" << NUM_FEATURES << "-NR=" << NUM_RATINGS << "-NB=" << NUM_BINS << "-SD-TBS";

    // Init biases
    for (int i = 0; i < NUM_USERS; i++) {
        userBias[i] = (0.1 - (-0.01)) * (((double) rand()) / (double) RAND_MAX) + (-0.01);
    }
    for (int i = 0; i < NUM_MOVIES; i++) {
        movieBias[i] = (-0.1 - (-0.5)) * (((double) rand()) / (double) RAND_MAX) + (-0.5);
    }

    // Init features
    for (j = 0; j < NUM_USERS; j++) {
        for (f = 0; f < NUM_FEATURES; f++) {
            userFeatures[j][f] = (-0.002 - (-0.01)) * (((double) rand()) / (double) RAND_MAX) + (-0.01);
        }
    }
    for (k = 0; k < NUM_MOVIES; k++) {
        for (f = 0; f < NUM_FEATURES; f++) {
            movieFeatures[k][f] = (0.02 - 0.01) * (((double) rand()) / (double) RAND_MAX) + 0.01;
        }
    }

    // Initialize numRated array to all zeros.
    for (int i = 0; i < NUM_USERS; i++) {
        numRated[i] = 0;
    }
}

void Weekday::loadData() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    int date;
    int rating;
    int j, i = 0;
    int curUser = 0;
    ifstream trainingDta ("../processed_data/train+probe.dta"); 
//     ifstream trainingDta ("../processed_data/train.dta"); 
    if (trainingDta.fail()) {
        cout << "train.dta: Open failed.\n";
        exit(-1);
    }

    // Initialize ratingLoc to -1
    for (j = 0; j < NUM_USERS; j++) {
        ratingLoc[j] = -1;
    }

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
        for (int j = 0; j < NUM_BINS; j++) {
            movieBins[i][j] = 0.0;
        }
    }

    trainingDta.close();
}

void Weekday::run() {
    int f, i, userId, k;
    double err, p, tmpMW, sq;
    double uBias, mBias;
    double uf, mf, reg;
    Rating *rating;
    int userLast = -1;
    short movieId, date;

    int w;

    // weekday
    int wd;

    unsigned int n_users[NUM_USERS][7];
    unsigned int n_movies[NUM_MOVIES][7];

    for (i = 0; i < NUM_USERS; i++) {
        for (w = 0; w < 7; w++) {
            n_users[i][w] = 0;
            m_users[i][w] = 0;
        }
    }

    for (i = 0; i < NUM_MOVIES; i++) {
        for (w = 0; w < 7; w++) {
            n_movies[i][w] = 0;
            m_movies[i][w] = 0;
        }
    }



    for (i = 0; i < NUM_RATINGS; i++) {
        rating = ratings + i;
        userId = rating->userId;
        movieId = rating->movieId;
        date = rating->date;

        wd = date % 7;



        m_users[userId][wd] += rating->rating;
        m_movies[movieId][wd] += rating->rating;


        n_users[userId][wd] += 1;
        n_movies[movieId][wd] += 1;
    }

    for (i = 0; i < NUM_USERS; i++) {
        for (w = 0; w < 7; w++) {
            if (n_users[i][w] != 0) {
                m_users[i][w] = m_users[i][w] / n_users[i][w];
            }
        }
    }


    for (i = 0; i < NUM_MOVIES; i++) {
        for (w = 0; w < 7; w++) {
            if (n_movies[i][w] != 0) {
                m_movies[i][w] = m_movies[i][w] / n_movies[i][w];
            }
        }
    }


}

int Weekday::bin(short date) {
    int idx = date / (2243 / NUM_BINS);
    if (idx == NUM_BINS) 
        idx--;
    return idx;
}

inline void Weekday::calcMWSum(int userId) {
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
inline double Weekday::predictRating(short movieId, int userId, short date) {
    double sum = GLOBAL_AVG;
    double norm = 1.0 / sqrt(numRated[userId]);
    sum += userBias[userId] + movieBias[movieId] + movieBins[movieId][bin(date)];
    for (int f = 0; f < NUM_FEATURES; f++) {
        sum += movieFeatures[movieId][f] * (userFeatures[userId][f] + norm * sumMW[userId][f]);
    }
    sum = sum > 5 ? 5 : sum;
    sum = sum < 1 ? 1 : sum;
    return sum;
}

/* Generate out of sample RMSE for the current number of features, then
   write this to a rmseOut. */
void Weekday::outputRMSE(short numFeats) {
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

void Weekday::output(int iter = NUM_EPOCHS) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    int date;
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
        date = atoi(strtok(NULL, " "));
        rating = predictRating(movieId, userId, date);
        out << rating << '\n';
    }
}

/* Save the calculated features and other parameters. */
void Weekday::save() {
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
            saved << userFeatures[i][j] << ' ';
        }
        saved << '\n';
    }
    for (i = 0; i < NUM_MOVIES; i++) {
        for (j = 0; j < NUM_FEATURES; j++) {
            saved << movieFeatures[i][j] << ' ';
        }
        saved << '\n';
    }
    saved.close();
}

/* Save the results of the probe */
void Weekday::probe(int iter = NUM_EPOCHS) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    stringstream fname;
    int userId, movieId, date;
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
        date = atoi(strtok(NULL, " ")); 
        
        saved << predictRating(movieId, userId, date) << "\n";
    }

    saved.close();
    p.close();
}

// Calculates RMSE for probe
void Weekday::probeRMSE() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    stringstream fname;
    int userId, movieId, date, rating, num_probe;
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
        date = atoi(strtok(NULL, " ")); 
        
        // Get actual rating
        rating = atoi(strtok(NULL, " "));
        
        err = predictRating(movieId, userId, date) - rating;
        sq += err * err;
        num_probe ++;
    }

    cout << sqrt(sq/num_probe) << endl;
    p.close();
}

int main() {
    Weekday *model = new Weekday();
    model->loadData();
    model->run();
//     svdpp->output();
//     svdpp->save();
//     svdpp->probe();
    cout << "Weekday completed.\n";

    return 0;
}

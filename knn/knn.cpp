#include <math.h>
#include <fstream>
#include <iostream>
#include <string>
#include <string.h>
#include <sstream>
#include <stdio.h>
#include <cstdlib>
#include <time.h>
#include <vector>

#define NUM_USERS 458293
#define NUM_MOVIES 17770
#define NUM_RATINGS 98291669
#define GLOBAL_AVG 3.512599976023349
#define GLOBAL_OFF_AVG 0.0481786328365
#define NUM_PROBE_RATINGS 1374739
#define MAX_CHARS_PER_LINE 30

// Ideas and some pseudocode from: http://dmnewbie.blogspot.com/2009/06/calculating-316-million-movie.html


using namespace std;

struct mu_pair {
    unsigned int user;
    unsigned char rating;
};

struct um_pair {
    unsigned short movie;
    unsigned char rating;
};

// Pearson intermediates, as described in dmnewbie's blog
struct s_inter {
    float x; // sum of ratings of movie i
    float y; // sum of ratings of movie j
    float xy; // sum (rating_i * rating_j)
    float xx; // sum (rating_i^2)
    float yy; // sum (rating_j^2)
    unsigned int n; // Num users who rated both movies
};


class KNN {
private:
    // um: for every user, stores (movie, rating) pairs.
    vector<um_pair> um[NUM_USERS];

    // mu: for every movie, stores (user, rating) pairs.
    vector<mu_pair> mu[NUM_MOVIES];

    // Intermediates for every movie pair
    s_inter inter[NUM_MOVIES][NUM_MOVIES];

    // Pearson coefficients for every movie pair
    float P[NUM_MOVIES][NUM_MOVIES];

    double predictRating(short movieId, int userId); 
    void outputRMSE(short numFeats);
    stringstream mdata;
public:
    KNN();
    ~KNN() { };
    void loadData();
    void run();
    void output();
    void save();
    void probe();
    inline float getP(short i, short j);
};

KNN::KNN() 
{
    mdata << "-KNN-";
}

void KNN::loadData() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
    int time;
    int rating;

    int j;

    int i = 0;
    int last_seen = 0;

    ifstream trainingDta ("../processed_data/train.dta"); 
    if (trainingDta.fail()) {
        cout << "train.dta: Open failed.\n";
        exit(-1);
    }
    while (getline(trainingDta, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1; // sub 1 for zero indexed
        movieId = (short) atoi(strtok(NULL, " ")) - 1;
        time = atoi(strtok(NULL, " ")); 
        rating = (char) atoi(strtok(NULL, " "));
        
        if (last_seen == userId) {
            i++;
        }
        else {
            i = 0;
            last_seen = userId;
        }

        um[userId].push_back(um_pair());
        um[userId][i].movie = movieId;
        um[userId][i].rating = rating;
    }
    trainingDta.close();

    cout << "Loaded um" << endl;

    i = 0;
    last_seen = 0;

    // Repeat again, not for mu dta
    ifstream trainingDtaMu ("../processed_data/train-mu.dta"); 
    if (trainingDtaMu.fail()) {
        cout << "train-mu.dta: Open failed.\n";
        exit(-1);
    }
    while (getline(trainingDtaMu, line)) {
        memcpy(c_line, line.c_str(), MAX_CHARS_PER_LINE);
        userId = atoi(strtok(c_line, " ")) - 1; // sub 1 for zero indexed
        movieId = (short) atoi(strtok(NULL, " ")) - 1;
        time = atoi(strtok(NULL, " ")); 
        rating = (char) atoi(strtok(NULL, " "));

        if (last_seen == movieId) {
            i++;
        }
        else {
            i = 0;
            last_seen = movieId;
        }
        
        mu[movieId].push_back(mu_pair());
        mu[movieId][i].user = userId;
        mu[movieId][i].rating = rating;
    }
    trainingDtaMu.close();
    cout << "Loaded mu" << endl;

    // Zero out intermediates
    for (i = 0; i < NUM_MOVIES; i++) {
        for (j = 0; j < NUM_MOVIES; j++) {
            inter[i][j].x = 0;

        }
    }
    cout << "Zeroed out intermediates" << endl;

}


void KNN::run() {
    int i, j, userId;
    double rmse, rmse_last;
    short movieId;
    s_inter tmp;
    float x, y, xy, xx, yy;
    unsigned int n;
    
    rmse_last = 0;
    rmse = 2.0;

    // Compute intermediates


    // Calculate Pearson coeff. based on: 
    // https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient
    for (i = 0; i < NUM_MOVIES; i++) {
        for (j = i; j < NUM_MOVIES; j++) {
            tmp = inter[i][j];
            x = tmp.x;
            y = tmp.y;
            xy = tmp.xy;
            xx = tmp.xx;
            yy = tmp.yy;
            n = tmp.n;

            P[i][j] = (n * xy - x * y) / (sqrt((n - 1) * xx - x*x) * sqrt((n - 1) * yy - (y * y)));
        }
    }

}

// Get Pearson coefficient of two movies
inline float KNN::getP(short i, short j) {
    // TODO: Symmetry
    return P[i][j];
}

inline double KNN::predictRating(short movieId, int userId) {
    // TODO
    double sum = 0;
    return sum;
}

/* Generate out of sample RMSE for the current number of features, then
   write this to a rmseOut. */
void KNN::outputRMSE(short numFeats) {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId, movieId, time;
    double predicted, actual; // ratings
    double err, sq, rmse;
    stringstream fname;
    fname << "rmseOut" << mdata.str();
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

void KNN::output() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    int userId;
    int movieId;
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
        rating = predictRating(movieId, userId);
        out << rating << '\n';
    }
}

/* Save the calculated parameters. */
void KNN::save() {
    int i, j;
    stringstream fname;
    fname << "../results/features" << mdata.str();

    ofstream saved(fname.str().c_str(), ios::trunc);
    if (saved.fail()) {
        cout << "features.knn: Open failed.\n";
        exit(-1);
    }
    saved.close();
}

/* Save the results of the probe */
void KNN::probe() {
    string line;
    char c_line[MAX_CHARS_PER_LINE];
    stringstream fname;
    int userId, movieId, time;
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
        time = atoi(strtok(NULL, " ")); 
        
        saved << predictRating(movieId, userId) << "\n";
    }

    saved.close();
    p.close();
}

int main() {
    KNN *knn = new KNN();
    knn->loadData();
    knn->run();
    knn->output();
//     knn->save();
    knn->probe();
    cout << "KNN completed.\n";

    return 0;
}

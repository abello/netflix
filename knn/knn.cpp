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

// Minimum common neighbors required for decent prediction
#define MIN_COMMON 16

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


    // Pearson coefficients for every movie pair
    float P[NUM_MOVIES][NUM_MOVIES];

    double predictRating(short movieId, int userId); 
    void outputRMSE(short numFeats);
    stringstream mdata;

    float movieAvg[NUM_MOVIES];
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

    int i = -1;
    int last_seen = 0;

    // Used for movie avgs
    int num_ratings = 0;
    int avg = 0;

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

    i = -1;
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

        // If we're still on the same movie
        if (last_seen == movieId) {
            i++;
            num_ratings += 1;
            avg += rating;
        }
        else {
            i = 0;
            last_seen = movieId;
            movieAvgs[movie] = float(avg)/num_ratings
            num_ratings = 1;
            avg = rating;
        }
        
        mu[movieId].push_back(mu_pair());
        mu[movieId][i].user = userId;
        mu[movieId][i].rating = rating;
    }
    trainingDtaMu.close();
    cout << "Loaded mu" << endl;

}


void KNN::run() {
    int i, j, u, m, user, z;
    double rmse, rmse_last;
    short movie;
    float x, y, xy, xx, yy;
    unsigned int n;

    char rating_i, rating_j;

    // Vector size
    int size1, size2;

    // Intermediates for every movie pair
    s_inter tmp[NUM_MOVIES];
    
    rmse_last = 0;
    rmse = 2.0;


    // Compute intermediates
    for (i = 0; i < NUM_MOVIES; i++) {

        // Zero out intermediates
        for (z = 0; z < NUM_MOVIES; z++) {
            tmp[z].x = 0;
            tmp[z].y = 0;
            tmp[z].xy = 0;
            tmp[z].xx = 0;
            tmp[z].yy = 0;
            tmp[z].n = 0;
        }

        size1 = mu[i].size();

        if ((i % 100) == 0) {
            cout << i << endl;
        }

        // For each user that rated movie i
        for (u = 0; u < size1; u++) {
            user = mu[i][u].user;

            size2 = um[user].size();
            // For each movie j rated by current user
            for (m = 0; m < size2; m++) {
                movie = um[user][m].movie; // id of movie j

                // At this point, we know that user rated both movie i AND movie
                // Thus we can update the pearson coeff for the pair XY

                // Rating of movie i
                rating_i = mu[i][u].rating;

                // Rating of movie j
                rating_j = um[user][m].rating;

                // Increment rating of movie i
                tmp[movie].x += rating_i;

                // Increment rating of movie j
                tmp[movie].y += rating_j;

                tmp[movie].xy += rating_i * rating_j;
                tmp[movie].xx += rating_i * rating_i;
                tmp[movie].yy += rating_j * rating_j;

                // Increment number of viewers of movies i AND j
                tmp[movie].n += 1;
            }
        }

        // Calculate Pearson coeff. based on: 
        // https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient
        for (z = 0; z < NUM_MOVIES; z++) {
            x = tmp[z].x;
            y = tmp[z].y;
            xy = tmp[z].xy;
            xx = tmp[z].xx;
            yy = tmp[z].yy;
            n = tmp[z].n;
            if (n < MIN_COMMON) {
                P[i][z] = 0;
            }
            else {
                P[i][z] = (n * xy - x * y) / (sqrt((n - 1) * xx - x*x) * sqrt((n - 1) * yy - (y * y)));
            }
        }

    }

}

// Get Pearson coefficient of two movies
inline float KNN::predictRating(short i, short j) {
    // TODO: Symmetry
//     return P[i][j];
    return 1;
}

inline double KNN::predictRating(short movie, int user) {
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

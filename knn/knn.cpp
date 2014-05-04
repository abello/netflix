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

// Ideas and pseudocode from: http://dmnewbie.blogspot.com/2009/06/calculating-316-million-movie.html


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
};


class SVD {
private:
    // um: for every user, stores (movie, rating) pairs.
    vector<um_pair> um;

    // mu: for every movie, stores (user, rating) pairs.
    vector<mu_pair> mu;

    // Intermediates for every movie
    s_inter inter[NUM_MOVIES];

    double predictRating(short movieId, int userId); 
    void outputRMSE(short numFeats);
    stringstream mdata;
public:
    SVD();
    ~SVD() { };
    void loadData();
    void run();
    void output();
    void save();
    void probe();
};

SVD::SVD() 
{
    mdata << "-KNN-";
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


void SVD::run() {
    int f, e, i, chances, userId;
    double sq, rmse, rmse_last, err, p;
    short movieId;
    double uf, mf;
    Rating *rating;

    rmse_last = 0;
    rmse = 2.0;

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


}

inline double SVD::predictRating(short movieId, int userId) {
    // TODO
    double sum = 0;
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

void SVD::output() {
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
void SVD::save() {
    int i, j;
    stringstream fname;
    fname << "../results/features" << mdata.str();

    ofstream saved(fname.str().c_str(), ios::trunc);
    if (saved.fail()) {
        cout << "features.svd: Open failed.\n";
        exit(-1);
    }
    saved.close();
}

/* Save the results of the probe */
void SVD::probe() {
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
    SVD *svd = new SVD();
    svd->loadData();
    svd->run();
    svd->output();
//     svd->save();
    svd->probe();
    cout << "SVD completed.\n";

    return 0;
}

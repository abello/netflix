#ifndef RATING_HPP
#define RATING_HPP

struct Rating {
    int userId;
    short movieId;
    int date;
    float rating;
    double cache;
};

#endif // RATING_HPP
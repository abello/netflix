#ifndef RATING_HPP
#define RATING_HPP

struct Rating {
    int userId;
    short movieId;
    short date;
    float rating;
    float cache;
};

#endif // RATING_HPP

#ifndef RATING_HPP
#define RATING_HPP
#include <stdint.h>

struct Rating {
    uint32_t userId;
    uint16_t movieId;
    uint16_t date;
    float rating;
};

#endif // RATING_HPP

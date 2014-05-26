#ifndef RATING_HPP
#define RATING_HPP

// For types, check: http://www.societyofrobots.com/member_tutorials/book/export/html/341
// http://www.cplusplus.com/reference/cstdint/

struct Rating {
    uint32_t userId;
    uint16_t movieId;
    uint16_t time;
    uint8_t rating;
};

// 4 + 2 + 2 + 1 = 9 bytes. Probably 12 bytes with alignment

#endif // RATING_HPP

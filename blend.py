import numpy as np
# Useful: arxiv.org/pdf/0911.0460.pdf

# Pass in all learned prediction functions, and the data used for blending 
# (in numpy array format). All prediction functions passed to this function 
# should be of the format g(user_id, movie_id) = rating. 
def blender(blend_dta, *funcs):
    X = np.ndarray(shape=(np.shape(blend_dta)[0], len(funcs)))
    y = np.ndarray(shape=(np.shape(blend_dta[0], 1)))

    # Initialize X
    for i in xrange(np.shape(blend_dta)[0]):
        row = blend_dta[i]
        y[i][0] = row[-1]
        for j in xrange(len(funcs)):
            X[i][j] = funcs[j](row[0], row[1])
    
    # Calculate pinv of X (this step might take a while...)
    X_pinv = np.linalg.pinv(X)
    w = np.dot(X_pinv, y)

    # Create returned function
#     def blended(user_id, movie_id):
#         summed = 0
#         for i in xrange(len(funcs)):
#             summed += w[i][0] * funcs[i](user_id, movie_id)
#     return blended


    # Print weights
    for i in xrange(len*funcs):
        print w[i][0]


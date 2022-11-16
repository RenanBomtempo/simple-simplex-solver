import numpy as np

def makeMatrixFullRank(A):
    if np.linalg.matrix_rank(A) == A.shape[0]: return A, []
    row = 1
    rowsEliminated = []
    counter = 0
    while 1:
        counter += 1
        B = A[0:(row+1), :]
        C = np.linalg.qr(B.T)[1]
        C[np.isclose(C, 0)] = 0
        if not np.any(C[row, :]):
            rowsEliminated.append(counter)
            A = np.delete(A, (row), axis=0)
        else:
            row += 1
        # end if
        if row >= A.shape[0]: break
    # end for
    return A, rowsEliminated
# end makeMatrixFullRank

if __name__ == "__main__":
    A = np.matrix([[1, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0],
                   [0, 0, 0, 1, 0],
                   [1, 0, 1, 1, 1],
                   [0, 0, 0, 0, 1]]
                   )
    print(A)
    A, rowsEliminated = makeMatrixFullRank(A)
    print(A)
    print(rowsEliminated)
# end if


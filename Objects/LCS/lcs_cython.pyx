'''
Author:        James Parkington
Created Date:  5/7/2023
Modified Date: 7/9/2023

This file provides an optimized implementation of the Longest Common Subsequence (LCS) algorithm using Cython.
The purpose of this file is to improve the performance of the LCS calculation when working with large sequences.
Cython is used to generate C code from this Python-like source code, allowing for faster execution.

The main difference between this implementation and a typical Python implementation is the use of Cython's
cpdef function declaration, as well as the use of typed memory views and native C data types.

This file is meant to be used as an imported module in other Python scripts that require an efficient LCS algorithm,
especially when working with large data sets.
'''

from    libc.stdint cimport uint64_t
import  numpy       as np
cimport numpy       as np

cpdef object lcs_indices(np.ndarray[uint64_t, ndim = 1] short_seq,
                         np.ndarray[uint64_t, ndim = 1] long_seq):

    '''
    Finds the longest common subsequence (LCS) and its indices for two sequences using Cython.

    This method is an optimized version of the original lcs_indices function,
    which has been translated into Cython code to improve performance.

    The input sequences should be provided as NumPy arrays with dtype=np.int64.

    Args:
        short_seq: A NumPy array representing the shorter sequence.
        long_seq: A NumPy array representing the longer sequence.

    Returns:
        A tuple containing the length of the LCS and a list of two tuples,
        where each tuple contains the start and end indices of the LCS in the short and long sequences.
    '''

    cdef int i, j
    cdef int m, n
    m, n = long_seq.shape[0], short_seq.shape[0]
    cdef np.ndarray[uint64_t, ndim = 2] dp = np.zeros((n + 1, m + 1), dtype = np.uint64)
    cdef np.ndarray[uint64_t, ndim = 2] ss = np.zeros((n + 1, m + 1), dtype = np.uint64)
    cdef np.ndarray[uint64_t, ndim = 2] sl = np.zeros((n + 1, m + 1), dtype = np.uint64)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if short_seq[i - 1] == long_seq[j - 1]:
                dp[i, j] = dp[i - 1, j - 1] + 1
                ss[i, j] = ss[i - 1, j - 1] if dp[i - 1, j - 1] > 0 else i - 1
                sl[i, j] = sl[i - 1, j - 1] if dp[i - 1, j - 1] > 0 else j - 1
            else:
                if dp[i - 1, j] > dp[i, j - 1]:
                    dp[i, j] = dp[i - 1, j]
                    ss[i, j] = ss[i - 1, j]
                    sl[i, j] = sl[i - 1, j]
                else:
                    dp[i, j] = dp[i, j - 1]
                    ss[i, j] = ss[i, j - 1]
                    sl[i, j] = sl[i, j - 1]

    return dp[n, m], [(ss[n, m], ss[n, m] + dp[n, m] - 1), (sl[n, m], sl[n, m] + dp[n, m] - 1)]

from Parser      import *
from Utilities   import *
from typing      import *
import dask      as dk

class Matcher:
    def __init__(self, 
                 parser, 
                 partitions):
        
        self.parser        = parser
        self.bitboard_sums = parser.get_positions() 
        self.partitions    = partitions


    def optimized_lcs(self, short_seq, long_seq):
        n, m    = len(short_seq), len(long_seq)
        w       = 64
        bitsets = {x: np.zeros((m + w - 1) // w, dtype=np.uint64) for x in set(short_seq)}

        for i, x in enumerate(long_seq[1:]):
            bitsets[x][(i + 1) // w] |= 1 << ((i + 1) % w)

        dp = np.zeros((m + w - 1) // w, dtype=np.uint64)

        for x in short_seq[1:]:
            bitset      = bitsets[x]
            new_dp      = np.zeros_like(dp)
            new_dp[:-1] = dp[:-1] | ((dp[:-1] & bitset[:-1]) + (dp[1:] & bitset[1:])) << 1
            new_dp[-1]  = dp[-1] | (dp[-1] & bitset[-1]) << 1
            dp          = new_dp

        lcs_length = 0
        for i in range(w):
            lcs_length = max(lcs_length, sum(bin(dp[j] >> i).count('1') for j in range(dp.size)))

        return lcs_length
    

    def process_partition(self, partition):
        sequences = partition['sequences']
        return self.optimized_lcs(self.user_bitboard_sums, sequences)
    

    def find_best_lcs(self):
        sorted_partitions = sorted(self.partitions, key=lambda p: p['total_ply'], reverse=True)
        best_lcs_length = 0

        for partition in sorted_partitions:
            lcs_length = dk.delayed(self.process_partition)(partition)
            best_lcs_length = max(best_lcs_length, lcs_length)

            if best_lcs_length >= partition['total_ply']:
                break

        best_lcs_length = dk.compute(best_lcs_length)[0]

        return best_lcs_length


# from fact_lcs import lcs

# # Example usage
# user_bitboards = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
# long_seq = [0, 2, 4, 6, 8, 10, 1, 3, 5, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

# lcs_length = lcs(user_bitboards, long_seq)
# print(lcs_length)  # Output: 9
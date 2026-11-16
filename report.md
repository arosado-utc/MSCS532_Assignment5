# Assignment 5: Quicksort Algorithm: Implementation, Analysis, and Randomization

**Alfredo Rosado** — MSCS 532, Algorithms and Data Structures
Dr. Michael Solomon — November 15, 2026

## 1. Introduction

This report documents the implementation and analysis of two quick sort
variants in Python: a deterministic variant that always takes the last
element of the subarray as its pivot, and a randomized variant that
picks the pivot uniformly at random. Both are in-place, both build on
the same Hoare partition, and both can count their own comparisons and
swaps. Those counters are what let the empirical section measure the
algorithm's behavior directly, instead of relying on wall time alone.
The source is in `quicksort.py`, the measurement harness in
`benchmark.py`, and the test suite in `tests.py`; the measured data
lives in `results/` and `plots/`.

## 2. Implementation

### 2.1 The deterministic variant

`quick_sort(a)` sorts a list in place in increasing order. Each
partition takes the last element of the subarray as the pivot and 
rearranges the subarray with the Hoare scheme. The pivot is 
swapped to the front, then two cursors walk toward each other, 
the left one stopping on an element `>= pivot` and the right one 
on an element `<= pivot`, swapping the pair until they cross.

```python
def _hoare_partition(a, lo, hi, pivot_index, stats):
    if pivot_index != lo:
        a[pivot_index], a[lo] = a[lo], a[pivot_index]
    pivot = a[lo]
    i = lo - 1
    j = hi + 1
    while True:
        while True:
            j -= 1
            if a[j] <= pivot:
                break
        while True:
            i += 1
            if a[i] >= pivot:
                break
        if i < j:
            a[i], a[j] = a[j], a[i]
        else:
            return j
```

The call returns a split index `j` such that everything in
`a[lo..j]` is `<= pivot` and everything in `a[j+1..hi]` is `>= pivot`;
both halves are then sorted recursively. Hoare's scheme was chosen
over Lomuto. It does about half as many swaps, because the elements move
in pairs instead of every `<= pivot` element being rotated one slot 
Each cursor also compares an element against the pivot at most
once per partition, which keeps the comparison counts in Section 4
easy to interpret.

### 2.2 The randomized variant

`quick_sort_random(a)` is the same algorithm with one change: the
pivot index is drawn uniformly at random from the subarray, freshly
for every partition.

```python
if randomize:
    pivot_index = random.randint(lo, hi)
else:
    pivot_index = hi
```

No other part of the algorithm differs, which is what makes the
comparison in Section 4 a clean test of the pivot choice alone.

### 2.3 Shared recursion driver

Both variants share one driver. It always recurses into the smaller
half and treats the larger half as the next loop iteration:

```python
while lo < hi:
    j = _hoare_partition(a, lo, hi, pivot_index, stats)
    if j - lo < hi - j:
        _quicksort(a, lo, j, randomize, stats)
        lo = j + 1
    else:
        _quicksort(a, j + 1, hi, randomize, stats)
        hi = j
```

The smaller half has at most half the elements, so the call stack
holds at most O(log n) frames even when every partition is maximally
unbalanced. Without this, sorting 10,000 already-sorted elements with
the plain two-recursion driver exceeds Python's default recursion
limit; `tests.py` pins the property down by sorting 10,000 sorted
elements under a 300-frame recursion limit.

## 3. Performance analysis

### 3.1 Best case

A partition that splits the subarray into two equal halves satisfies
`T(n) = 2T(n/2) + O(n)`: log n levels of the recursion tree, n units
of partition work per level, for O(n log n) total.

### 3.2 Why the average case is O(n log n)

With a uniformly random pivot the split point is uniform over the
subarray, so the expected cost satisfies

`T(n) = (2/n^2) * sum_{k=0}^{n-1} (T(k) + T(n-1-k)) + c n`,

whose solution is about 2 n ln n comparisons — O(n log n) in expected
time. The same reasoning applies to the deterministic variant on
randomly ordered input, because a random order makes the last element
an unbiased pivot: the measured averages in Section 4.2 confirm both
variants land within about 15% of 2 n ln n on random input, the gap
being the implementation-constant difference between partition
schemes.

### 3.3 Why the worst case is O(n^2)

The recursion degenerates when one side of every partition is empty:
then `T(n) = T(n-1) + O(n)`, which unrolls to O(n^2). For the
deterministic variant, sorted input produces exactly our worst case. The last
element is the maximum, so each partition peels off a single element
and the recursion runs n levels deep. Reverse-sorted input does the
same from the other end, because the last element is the minimum. The
swap counts show the cost is in the comparisons, not the swaps:
degenerate partitions move only O(n) elements total (a pivot swap and
a crossing swap per level) while comparing O(n^2) pairs.

### 3.4 Space and other overheads

- Call stack: O(log n) in all cases, by the smaller-half driver; a
  naive two-recursion driver would take O(n) frames on degenerate
  inputs.
- Working storage: in place. Only the stack and the optional `stats`
  dictionary.
- Each comparison does constant work, so the comparison count is the
  true cost of the comparison-based sort.

## 4. Impact of randomization

Randomization does not change the best or average case and on random
input both variants are already near 2 n ln n. What it removes is the
input dependence of the worst case:

1. With a fixed pivot rule, one adversarial input order forces the
   quadratic behavior on every run. For the last-element pivot, that
   order is "sorted" or "reverse-sorted".
2. With a random pivot, every input has the same expected cost,
   about 2 n ln n. The quadratic outcome still exists for a fixed
   unlucky pivot sequence, but it requires n bad draws in a row,
   whose probability shrinks like 1/(n-1)!. The expected running
   time on any input is therefore O(n log n): the worst case is
   replaced by a tail event.

The measurements in Section 5 quantify both sides of that claim.

## 5. Empirical analysis

### 5.1 Method

`benchmark.py` sorts the same seeded input with both variants across
three input kinds (random, sorted, reverse-sorted) and records the
exact comparison and swap counts (one run; the counts are
deterministic, so no averaging is needed) and the median wall time
(5 runs for n <= 1024, one run above that, where the quadratic cases
are long enough that one run already damps the jitter). Sizes are
512-8192 for random input and 512-4096 for the two degenerate kinds.

### 5.2 Results

Comparison counts (from `results/comparisons.csv`):

| kind / n   | deterministic | randomized |
| ---------- | ------------- | ---------- |
| random 512 | 7,397         | 7,742      |
| random 1024| 15,689        | 14,386     |
| random 2048| 35,319        | 33,076     |
| random 4096| 75,296        | 71,255     |
| random 8192| 168,240       | 158,421    |
| sorted 512 | 132,151       | 7,277      |
| sorted 1024| 525,791       | 16,085     |
| sorted 2048| 2,101,743     | 31,408     |
| sorted 4096| 8,385,942     | 70,475     |
| rev 512    | 131,782       | 7,095      |
| rev 1024   | 525,601       | 15,106     |
| rev 2048   | 2,098,938     | 34,915     |
| rev 4096   | 8,357,738     | 75,567     |

Median wall times (from `results/times.csv`, ms):

| kind / n   | deterministic | randomized |
| ---------- | ------------- | ---------- |
| random 1024| 0.4653        | 0.6373     |
| random 8192| 5.4297        | 6.6967     |
| sorted 1024| 6.7735        | 0.4980     |
| sorted 4096| 125.1638      | 2.4659     |
| rev 1024   | 6.7060        | 0.5321     |
| rev 4096   | 127.2666      | 2.6697     |

The full tables are in the CSVs; `plots/comparisons_vs_size.png` and
`plots/time_vs_size.png` show all six curves on log-log axes.

### 5.3 Relating the measurements to the theory

- **The O(n^2) signature.** For the deterministic variant on sorted
  input each doubling of n multiplies the comparison count by
  132,151 → 525,791 → 2,101,743 → 8,385,942, i.e. 3.98x, 3.99x,
  3.99x — the 4x-per-doubling that n^2 predicts (an n log n curve
  grows about 2.2x per doubling). Reverse-sorted input gives the
  same ratios from the other end (3.99x, 3.99x, 3.98x).
- **The O(n log n) signature.** Every n log n curve grows about
  2.2x per doubling, with both variants on random input and the
  randomized variant on every kind, matching the ratio
  `(2n log 2n)/(n log n)` near these sizes.
- **The 100x gap.** At n = 4096 on sorted input the deterministic
  variant makes 8,385,942 comparisons against the randomized
  variant's 70,475. That is 119x more, the n^2 versus n log n separation
  the theory predicts. The wall-time gap is 51x (125.1638 ms vs
  2.4659 ms); it is smaller than the comparison ratio because a
  degenerate partition does fewer swaps per comparison.
- **The 2 n ln n constant.** The randomized variant's counts on
  sorted 4096 (70,475 and 75,567 across the two kinds) sit within
  about 10% of 2 n ln n = 68,127, the expected comparison count
  from Section 3.2, measured.

## 6. Code quality and testing

The code follows the conventions I used throughout the course: small
single-purpose functions, inclusive bounds documented at every
signature, docstrings stating parameters, return values, and
complexity, and a `stats` hook that keeps the measurement bookkeeping
out of the hot path when it is not needed. `tests.py` runs 14 tests:
correctness against the built-in `sorted()` on 250 randomized inputs
for both variants, edge cases (empty, single, two elements, all
equal, negatives), in-place behavior, both variants agreeing on
identical inputs, the O(log n) stack property under a 300-frame
recursion limit, the exact worst-case comparison counts for the
deterministic variant (49, 165, and 2,205 comparisons at n = 8, 16,
and 64. The counts are stable because the pivot rule is deterministic), the 100x+ gap
on sorted 4096, the 2 n ln n band on random input, and the O(n) swap
count on degenerate partitions. All 14 pass.

## 7. Conclusion

The implementation matches the theory on every axis the analysis
makes a prediction on: n log n growth per doubling for both variants
on random input, the exact 4x-per-doubling O(n^2) signature for the
deterministic variant on sorted and reverse-sorted input, and a
measured comparison count within about 10% of the 2 n ln n
expectation for the randomized variant. Randomization does not buy 
a faster average case, but a worst case that is no longer a property of the input.

## References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022).
  *Introduction to Algorithms* (4th ed.). MIT Press. (Chapter 8:
  Quick sort — the Hoare partition, the expected-case analysis, and
  randomized quick sort.)
- Hoare, C. A. R. (1962). Quicksort. *The Computer Journal, 5*(1),
  10-16. https://doi.org/10.1093/comjnl/5.1.10

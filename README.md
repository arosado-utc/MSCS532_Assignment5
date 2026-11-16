# Assignment 5: Quicksort Algorithm: Implementation, Analysis, and Randomization

For this assignment I implemented quick sort twice in Python: a
deterministic variant whose pivot is always the last element of the
subarray, and a randomized variant whose pivot is a uniformly random
element of the subarray. Both build on the same in-place Hoare
partition, and both can count their own comparisons and swaps, which
is what the empirical comparison below is based on. The bottom line:
on random input the two variants are essentially tied, but on
sorted and reverse-sorted input the deterministic variant falls into
its O(n^2) worst case while the randomized one stays at O(n log n) —
measured here at a 100x+ comparison-count gap at n = 4096.

## How to run

Python 3.8 or higher. matplotlib is only needed to regenerate the
plots.

```bash
python3 quicksort.py   # demo of both variants on sample lists
python3 tests.py       # test suite (14 tests)
python3 benchmark.py   # reruns the sweep, rewrites results/ and plots/
```

## Files

| File                  | Description                                                 |
| --------------------- | ----------------------------------------------------------- |
| `quicksort.py`        | The two variants, the Hoare partition, and the demo         |
| `benchmark.py`        | The sweep harness: comparison/swap counts + median wall time |
| `tests.py`            | Test suite, including the complexity claims                 |
| `results/`            | `comparisons.csv` and `times.csv` — the measured data       |
| `plots/`              | `comparisons_vs_size.png` and `time_vs_size.png`            |

## The two implementations

### The shared partition

Both variants partition with the Hoare scheme rather than Lomuto:
the pivot is swapped to the front of the subarray, then two cursors
walk toward each other — the left one stops on an element `>= pivot`,
the right one on an element `<= pivot` — and the pair is swapped
until they cross. Hoare's split does not isolate the pivot in its
final position; it returns an index `j` such that everything in
`a[lo..j]` is `<= pivot` and everything in `a[j+1..hi]` is `>= pivot`,
and both halves are then sorted recursively.

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

Two properties of this scheme matter for the rest of the report.
First, it does about half as many swaps as Lomuto for the same
partition, because elements move in pairs instead of every `<= pivot`
element being rotated one slot. Second, the cursors each compare an
element against the pivot at most once per partition, which is what
makes the comparison counts below easy to interpret.

The `stats` dictionary is the hook the analysis uses: when it is
passed in, every comparison and every swap increments a counter, so
the benchmark measures the algorithm itself instead of the machine.

### The deterministic variant

`quick_sort(a)` picks the last element of the subarray as the pivot
every time. That is the classic naive choice, and it is exactly the
choice the analysis needs, because its performance depends on the
input order: an ascending list hands the partition the maximum as
pivot every time, so each partition peels off a single element and
the recursion runs n levels deep.

### The randomized variant

`quick_sort_random(a)` picks the pivot uniformly at random from the
subarray, freshly for every partition:

```python
if randomize:
    pivot_index = random.randint(lo, hi)
else:
    pivot_index = hi
```

No input order is a guaranteed worst case anymore, because for any
fixed input the pivot sequence is a random variable; the expected
work is the same on every input.

### The recursion driver

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

The call stack then holds one frame per level of smaller halves,
which is O(log n) even when every partition is maximally unbalanced.
Without this, sorting 10,000 already-sorted elements with a plain
two-recursion driver exceeds Python's default recursion limit — the
test suite checks the sorted-10k case under a 300-frame limit to
pin this down.

## Time and space complexity

### Best case

A partition that splits the subarray into two equal halves runs
`T(n) = 2T(n/2) + O(n)`, which is O(n log n) by the recursion tree:
log n levels, n units of work per level.

### Why the average case is O(n log n)

On a random pivot the split point is uniform, so the expected cost
satisfies `T(n) = (2/n^2) * sum over k of (T(k) + T(n-1-k)) + O(n)`,
whose solution is about 2 n ln n comparisons, i.e. O(n log n) in
expected time. The same analysis works for the deterministic variant
when the input order is random, because a random order makes the last
element just as good a pivot as any random choice: the measured
average over random inputs (below) is within about 15% of 2 n ln n
for both variants, which is exactly the implementation-constant gap
between partition schemes.

### Why the worst case is O(n^2)

The recursion tree degenerates when one side of every partition has
zero elements: then `T(n) = T(n-1) + O(n)`, which unrolls to
`O(n^2)`. For the deterministic variant, sorted and reverse-sorted
input produce exactly this: the last element is the max (or the min),
so the partition peels off one element per level. The swap counts
tell the same story from the other side — degenerate partitions
still only move O(n) elements total (a pivot swap and a crossing swap
per level), so the quadratic cost is in the comparisons, not the
swaps.

### Space and other overheads

- Call stack: O(log n) in all cases, by the smaller-half driver
  above; a naive two-recursion driver would take O(n) frames on the
  degenerate inputs.
- Working storage: the sorts are in place; the only extra memory is
  the stack and the optional `stats` dictionary.
- The comparison count is the true cost in a comparison-based sort:
  each comparison does constant work, and the `stats` counters make
  that explicit.

## What randomization changes

Randomization does not change the best or average case — on random
input both variants are already near 2 n ln n. What it removes is
the *input dependence* of the worst case:

- With a fixed pivot rule, a single adversarial input order
  (sorted, for the last-element pivot) forces the quadratic
  behavior on every run.
- With a random pivot, every input has the same expected cost,
  about 2 n ln n. The quadratic outcome is still possible for a
  fixed sequence of unlucky pivots, but that requires n bad draws in
  a row, whose probability shrinks like 1/(n-1)!, so the expected
  running time on any input is O(n log n).

The empirical section measures both sides of that claim.

## Empirical results

### How it was measured

`benchmark.py` sorts the same seeded input with both variants across
three input kinds — random, sorted, reverse-sorted — and records:

- the exact comparison and swap counts (one run; the counts are
  deterministic, so no averaging is needed), and
- the median wall time (5 runs for n <= 1024, one run above that,
  where the quadratic cases get long enough that one run already
  damps the jitter).

Sizes: 512–8192 for random input, 512–4096 for the two degenerate
kinds — each doubling past that costs about 4x more for the
deterministic variant, and 4096 is already a two-minute run in pure
Python.

### Comparison counts (from `results/comparisons.csv`)

Random input — both variants track n log n:

| n    | deterministic | randomized |
| ---- | ------------ | ---------- |
| 512  | 7,397        | 7,742      |
| 1024 | 15,689       | 14,386     |
| 2048 | 35,319       | 33,076     |
| 4096 | 75,296       | 71,255     |
| 8192 | 168,240      | 158,421    |

Sorted input — the deterministic variant hits the wall:

| n    | deterministic | randomized |
| ---- | ------------- | ---------- |
| 512  | 132,151       | 7,277      |
| 1024 | 525,791       | 16,085     |
| 2048 | 2,101,743     | 31,408     |
| 4096 | 8,385,942     | 70,475     |

Reverse-sorted input — same signature:

| n    | deterministic | randomized |
| ---- | ------------- | ---------- |
| 512  | 131,782       | 7,095      |
| 1024 | 525,601       | 15,106     |
| 2048 | 2,098,938     | 34,915     |
| 4096 | 8,357,738     | 75,567     |

### Wall time (from `results/times.csv`)

| kind / n   | det ms   | rand ms | kind / n     | det ms   | rand ms |
| ---------- | -------- | ------- | ------------ | -------- | ------- |
| random 512 | 0.2285   | 0.3105  | sorted 512   | 1.7627   | 0.2393  |
| random 1024| 0.4653   | 0.6373  | sorted 1024  | 6.7735   | 0.4980  |
| random 2048| 1.1468   | 1.4183  | sorted 2048  | 28.4577  | 1.1342  |
| random 4096| 2.4472   | 3.0336  | sorted 4096  | 125.1638 | 2.4659  |
| random 8192| 5.4297   | 6.6967  | rev 512      | 1.8325   | 0.2650  |
|            |          |         | rev 1024     | 6.7060   | 0.5321  |
|            |          |         | rev 2048     | 29.2809  | 1.2169  |
|            |          |         | rev 4096     | 127.2666 | 2.6697  |

The plots `plots/comparisons_vs_size.png` and
`plots/time_vs_size.png` show the same data on log-log axes.

### Relating the measurements to the theory

- **The O(n^2) signature.** For the deterministic variant on sorted
  input each doubling of n multiplies the comparison count by
  132,151 → 525,791 → 2,101,743 → 8,385,942, i.e. 3.98x, 3.99x,
  3.99x — the 4x-per-doubling that `n^2` predicts (an n log n curve
  would grow about 2.2x per doubling). On reverse-sorted input the
  ratios are 3.99x, 3.99x, 3.98x, the same wall from the other side.
- **The O(n log n) signature.** Every n log n curve — both variants
  on random input, the randomized variant on every kind — grows
  about 2.2x per doubling, which is the n log n ratio
  `(2n log 2n)/(n log n)` evaluated near these sizes.
- **The 100x gap.** At n = 4096 on sorted input the deterministic
  variant makes 8,385,942 comparisons against the randomized
  variant's 70,475 — 119x more, exactly the n^2 versus n log n
  separation the theory predicts, visible in both comparison counts
  and wall time (125.1638 ms vs 2.4659 ms, a 51x wall gap; the wall
  ratio is smaller than the comparison ratio because a degenerate
  partition does fewer swaps per comparison).
- **The 2 n ln n constant.** The randomized variant's counts on
  sorted 4096 (70,475 and 75,567 across the two kinds) sit right on
  2 n ln n = 68,127, within about 10% — the expected comparison
  count from the analysis, measured.

## Design decisions

- **Hoare over Lomuto.** The shared partition is Hoare's because it
  halves the swap count and its two-cursor scans make the
  comparison count transparent; the cost model in the analysis is
  about comparisons, and Hoare keeps the constant small.
- **Last-element pivot for the deterministic variant.** A random
  or median-of-three pivot would hide the worst case, which is the
  whole point of the comparison. The naive choice makes the
  theory's warning measurable.
- **Comparison counts as the primary metric.** Wall time in pure
  Python is noisy at sub-millisecond sizes; the counters are exact,
  so one run of each case is enough to separate n^2 from n log n.
- **Smaller-half recursion.** It costs nothing and keeps the stack
  O(log n) on the very inputs that would otherwise blow the stack.

## References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022).
  *Introduction to Algorithms* (4th ed.). MIT Press. (Chapter 8:
  Quick sort, including the Hoare partition and the expected-case
  analysis.)
- Hoare, C. A. R. (1962). Quicksort. *The Computer Journal, 5*(1),
  10-16. https://doi.org/10.1093/comjnl/5.1.10

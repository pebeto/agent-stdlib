"""Number helpers: summary statistics over a list of numbers."""


def summary(nums):
    """Return count, min, max, mean, and median for a list of numbers."""
    s = sorted(nums)
    n = len(s)
    if n == 0:
        return {"count": 0}
    mid = n // 2
    median = s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2
    return {
        "count": n,
        "min": s[0],
        "max": s[-1],
        "mean": sum(s) / n,
        "median": median,
    }

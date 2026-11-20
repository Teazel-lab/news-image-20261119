"""ILLUS: story id -> fn(w, h) -> inline SVG string. Merges the two parts."""
ILLUS = {}
try:
    from illus_a import ILLUS_PART as _A
    ILLUS.update(_A)
except ImportError:
    pass
try:
    from illus_b import ILLUS_PART as _B
    ILLUS.update(_B)
except ImportError:
    pass

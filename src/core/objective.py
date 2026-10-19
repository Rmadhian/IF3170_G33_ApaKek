from itertools import combinations

# box = (x, y, z, w, l, h)


# panjang irisan di satu sumbu
def _axis_overlap(a0, a_len, b0, b_len):
    return max(0, min(a0 + a_len, b0 + b_len) - max(a0, b0))


# volume irisan dua box
def overlap_volume(a, b):
    dx = _axis_overlap(a[0], a[3], b[0], b[3])
    dy = _axis_overlap(a[1], a[4], b[1], b[4])
    dz = _axis_overlap(a[2], a[5], b[2], b[5])
    return dx * dy * dz


# total overlap semua pasangan paket
def total_overlap(boxes):
    return sum(overlap_volume(a, b) for a, b in combinations(boxes, 2))

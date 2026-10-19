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


# luas irisan alas a dengan atap b
def _contact_area(a, b):
    dx = _axis_overlap(a[0], a[3], b[0], b[3])
    dy = _axis_overlap(a[1], a[4], b[1], b[4])
    return dx * dy


# paket di lantai atau ditopang paket lain
def is_supported(box, boxes):
    if box[2] == 0:
        return True
    for other in boxes:
        if other[2] + other[5] == box[2] and _contact_area(box, other) > 0:
            return True
    return False


# jumlah paket melayang
def floating_count(boxes):
    return sum(1 for b in boxes if not is_supported(b, boxes))


# jumlah paket yang menumpang di atas paket fragile
def fragile_support_count(boxes, fragile):
    count = 0
    for i, below in enumerate(boxes):
        if not fragile[i]:
            continue
        for j, above in enumerate(boxes):
            if i != j and below[2] + below[5] == above[2] and _contact_area(above, below) > 0:
                count += 1
    return count


# volume paket yang keluar dari truk
def out_of_bounds_volume(box, truck_dims):
    inside = overlap_volume(box, (0, 0, 0) + tuple(truck_dims))
    return box[3] * box[4] * box[5] - inside


# total volume tembus dinding
def total_out_of_bounds(boxes, truck_dims):
    return sum(out_of_bounds_volume(b, truck_dims) for b in boxes)


# kelebihan berat di atas kapasitas
def overweight(total_weight, max_capacity):
    return max(0, total_weight - max_capacity)

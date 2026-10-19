from geneticAlgorithm.models import Package

def get_demo_packages():
    return [
        Package("P01", 3, 4, 2, 60, 5, False, 3),
        Package("P02", 2, 2, 2, 35, 3, True, 1),
        Package("P03", 4, 3, 2, 55, 7, False, 2),
        Package("P04", 3, 3, 1, 28, 2, False, 4),
        Package("P05", 2, 4, 2, 42, 4, False, 2),
        Package("P06", 5, 2, 2, 48, 6, True, 1),
        Package("P07", 2, 2, 1, 18, 1, False, 5),
        Package("P08", 4, 2, 2, 39, 5, False, 3),
        Package("P09", 3, 2, 1, 22, 2, False, 2),
        Package("P10", 2, 3, 2, 31, 3, False, 4),
    ]
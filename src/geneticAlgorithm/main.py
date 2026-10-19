from geneticAlgorithm.config import (
    PILOT_POPULATION_SIZE, PILOT_GENERATIONS, REPEATS,
    FIXED_POPULATION_SIZE, GENERATION_VARIANTS,
    FIXED_GENERATIONS, POPULATION_VARIANTS
)

from geneticAlgorithm.demoPackages import get_demo_packages
from geneticAlgorithm.experimentRunner import create_truck, run_one, run_pilot, save_summary

def main():
    packages = get_demo_packages()
    truck = create_truck()

    print("Menjalankan pilot untuk mengukur durasi...")
    _, pilot_seconds = run_pilot(packages, truck, PILOT_POPULATION_SIZE, PILOT_GENERATIONS)
    print(f"Pilot pop={PILOT_POPULATION_SIZE}, gen={PILOT_GENERATIONS}, durasi={pilot_seconds:.3f} detik")
    print("Gunakan durasi pilot untuk menilai apakah parameter eksperimen perlu disesuaikan.")

    rows = []
    for generations in GENERATION_VARIANTS:
        for repeat in range(1, REPEATS + 1):
            seed = 1100 + generations * 10 + repeat
            rows.append(run_one(packages, truck, FIXED_POPULATION_SIZE, generations,
                                seed, "control_population"))

    for population in POPULATION_VARIANTS:
        for repeat in range(1, REPEATS + 1):
            seed = 2200 + population * 10 + repeat
            rows.append(run_one(packages, truck, population, FIXED_GENERATIONS,
                                seed, "control_generations"))

    save_summary(rows)
    print("Selesai. Ringkasan ada di output/summary.csv")

if __name__ == "__main__":
    main()

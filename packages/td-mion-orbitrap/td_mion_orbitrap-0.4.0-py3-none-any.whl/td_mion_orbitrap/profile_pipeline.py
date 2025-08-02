# profile_pipeline.py

import cProfile
import pstats
import yaml
from main import main  # assumes your main.py defines main()

def workload():
    # Only profile one run—point to a minimal config if you like
    main("config.yaml")

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    workload()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(20)

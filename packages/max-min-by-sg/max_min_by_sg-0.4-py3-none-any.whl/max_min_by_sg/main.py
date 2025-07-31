import os
import subprocess
import max_min_by_sg

def ensure_required_files():
    base_path = os.path.dirname(max_min_by_sg.__file__)
    for filename in ["derivatives.txt", "points.txt"]:
        file_path = os.path.join(base_path, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                pass

def main_entry():
    base_path = os.path.dirname(max_min_by_sg.__file__)
    exe_path = os.path.join(base_path, "solving_maxima_minima_for_2_variables.exe")

    ensure_required_files()

    result = subprocess.run([exe_path], cwd=base_path)
    if result.returncode != 0:
        print("Error running the executable.")

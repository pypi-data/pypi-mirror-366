import time

import flag_gen

__about__ = """
This is a challenge problem for pip_install_or_pypi for Databased Hack&Seek 2025.
Most python projects needs `pyproject.toml` for stating dependencies, description, etc. for the project.
Check it out!
This file is the main file, which will run when calling for the project. Check out other files too for more idea about the project.
"""

FLAG="Aks3A0Q2AiMXAyQgAhAkAwQ4AgEIA0YbAiwTAxQGAh8ZAycFAiMvA0NAAicTA0VRAgYpAwdAAiA0AzIGAkhVAyAiAicqA0E4AkkpAzAXAiMbAywtAkgvA0NAAgElAwssAiwvA0gOAh8TAyIGAgkMA103Agk3AyJSAhUAAwlAAg0bA1c3Ahw2Az8eAkg1A1xQAjQpAzMTAg0BAyceAgcAA0YFAgk3A1wcAiwTAwQWAhc0AyweAgY1AxZaAgEVAwoCAiwQAxQGAgIhAzEVAkgKAxUiAi0TAxUDAiASAyYM"

def main():
    print("Databased Hack&Seek 2025")
    print("Problem: pip_install_or_pypi\n\n")
    print("Program starting...\n")
    time.sleep(1)

    process_names = [
        "Initializing",
        "Loading resources",
        "Setting up environment",
        "Connecting to database",
        "Starting services",
        "Configuring settings",
        "Running diagnostics",
        "Finalizing setup",
        "Launching application",
        "Processing flag..."
    ]
    for j in range(10):
        print(process_names[j]+"...")
        for i in range(1000):
            # Progress bar
            progress = (i + 1) / 1000
            filled_length = int(50 * progress)
            bar = '█' * filled_length + '-' * (50 - filled_length)

            print(f"\r🔄 Progress: |{bar}| {progress:.1%} - Process {i + 1:3d}/1000", end='', flush=True)

            if i % 50 == 0:
                time.sleep(0.5)
            else:
                time.sleep(0.1)
        print(f"\n✅ Process {j + 1} completed successfully!\n")

    print("All processes completed successfully!\n")
    print("Generating flag...\n")
    time.sleep(1)
    decoded_flag = flag_gen.decode_flag(FLAG)
    print(f"🎉 Flag generated: {decoded_flag}\n") # Frenzy Flag!

if __name__ == "__main__":
    main()

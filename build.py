import subprocess
import os
import shutil

def build():
    entry_point = os.path.join("src", "main.py")

    dist_path = "dist"

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("OneLifeClimber.spec"):
        os.remove("OneLifeClimber.spec")

    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name=OneLifeClimber",
        f"--add-data=audio:audio",
        f"--add-data=data:data",
        f"--add-data=graphics:graphics",
        entry_point
    ]

    subprocess.run(command, check=True)
    print(f"✅ Build terminé. L'exécutable se trouve dans le dossier '{dist_path}'.")

if __name__ == "__main__":
    build()
    
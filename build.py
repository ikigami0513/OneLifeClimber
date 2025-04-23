import subprocess
import os
import shutil
import sys

def build(target: str) -> None:
    entry_point = os.path.join("src", "main.py")
    dist_path = "dist"

    # Nettoyage des anciens fichiers
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("OneLifeClimber.spec"):
        os.remove("OneLifeClimber.spec")

    # Choix du séparateur selon la plateforme cible
    if target.lower() == "windows":
        sep = ";"
    elif target.lower() == "ubuntu":
        sep = ":"
    else:
        print("❌ Plateforme non supportée. Utilisez 'windows' ou 'ubuntu'.")
        sys.exit(1)

    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name=OneLifeClimber",
        f"--add-data=audio{sep}audio",
        f"--add-data=data{sep}data",
        f"--add-data=graphics{sep}graphics",
        entry_point
    ]

    subprocess.run(command, check=True)
    print(f"✅ Build terminé pour {target}. L'exécutable se trouve dans le dossier '{dist_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python build.py [windows|ubuntu]")
        sys.exit(1)

    target_platform = sys.argv[1]
    build(target_platform)

import os
from dotenv import dotenv_values, load_dotenv

# Charge les variables du fichier .env
env_file_values = dotenv_values(".env")  # dict sans override
load_dotenv(override=False)  # ne modifie pas l'environnement

# Variables d'environnement actuelles
env_runtime_values = {
    "GH_TOKEN": os.getenv("GH_TOKEN"),
    "PYPI_TOKEN": os.getenv("PYPI_TOKEN"),
}

# Comparaison
print("\n🔍 Comparaison des clés GH_TOKEN et PYPI_TOKEN\n")

for key in ["GH_TOKEN", "PYPI_TOKEN"]:
    file_val = env_file_values.get(key)
    env_val = env_runtime_values.get(key)

    if file_val == env_val:
        print(f"✅ {key} est identique dans .env et l'environnement")
    else:
        print(f"❌ {key} est différent !")
        print(f"    .env        : {file_val}")
        print(f"    environnement : {env_val}")

print("\n" + "-" * 60)

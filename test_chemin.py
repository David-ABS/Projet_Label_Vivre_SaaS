import os

print("\n=== 🕵️‍♂️ DÉTECTIVE DE CHEMINS PYTHON ===")

# 1. Où suis-je ? (__file__ représente ce script)
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
print(f"📍 1. Python pense que mon dossier actuel est : \n{dossier_actuel}")

# 2. Quel fichier cherche-t-on ?
nom_fichier = "label_vivre.sqlite"

# 3. La fusion (os.path.join)
chemin_final = os.path.join(dossier_actuel, nom_fichier)
print(f"\n🔗 2. Le chemin exact où Python va chercher la BDD est : \n{chemin_final}")

# 4. Le verdict
print("\n⚖️ 3. Verdict :")
if os.path.exists(chemin_final):
    print("✅ BINGO ! Le fichier existe bien à cet endroit précis. Pandas pourra le lire.")
else:
    print("❌ INTROUVABLE : Il n'y a pas de fichier à ce chemin exact.")
    print("   -> Conséquence : SQLite va créer un fichier vide portant ce nom, et ton application plantera avec un DatabaseError.")
print("=========================================\n")
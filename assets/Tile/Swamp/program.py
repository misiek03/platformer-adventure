import os

folder = "./"  # <- ZMIEŃ na prawidłową ścieżkę

for filename in os.listdir(folder):
    if filename.startswith("Tile_") and filename.endswith(".png"):
        number_part = filename[5:-4]  # wyciąga np. "01" z "Tile_01.png"
        new_name = f"{int(number_part)}.png"  # usuwa zera wiodące
        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)
        os.rename(old_path, new_path)
        print(f"Zmieniono nazwę: {filename} -> {new_name}")
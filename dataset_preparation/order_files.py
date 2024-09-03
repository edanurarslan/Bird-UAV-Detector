# Usage: python order_files.py "folder_path" "label"
# Contributor: Doğa Oytaç

import os
import argparse

def main():

    # Command line parser
    parser = argparse.ArgumentParser(description="Rename files in folder.")
    parser.add_argument("folder_path", type=str, help="The path of the folder.")
    parser.add_argument("label", type=str, help="Label of detected objects.")

    args = parser.parse_args()
    folder_path = args.folder_path
    label = args.label

    txt_count = 0
    jpg_count = 0

    # Rename files
    for file in os.listdir(folder_path):

        if file.endswith(".txt"):
            txt_count += 1
            old = os.path.join(folder_path, file)
            new = os.path.join(folder_path, f"{txt_count}_{label}"+".txt")
            os.rename(old, new)

        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
            jpg_count += 1
            old = os.path.join(folder_path, file)
            new = os.path.join(folder_path, f"{jpg_count}_{label}"+".jpg")
            os.rename(old, new)

if __name__ == "__main__":
    main()
    print("Succesful.")
import os

DANGEROUS_EXTENSIONS = [".pkl", ".bin", ".pt", ".ckpt"]

def check_folder(folder_path):
    safe_files = []

    for filename in os.listdir(folder_path):
        _, extension = os.path.splitext(filename)

        if extension in DANGEROUS_EXTENSIONS:
            raise Exception(f"KHATRA! '{filename}' file refuse ki gayi ({extension} pickle format hai)")

        safe_files.append(filename)

    return safe_files


if __name__ == "__main__":
    os.makedirs("test_folder", exist_ok=True)
    with open("test_folder/config.json", "w") as f:
        f.write("{}")
    with open("test_folder/weights.safetensors", "w") as f:
        f.write("fake data")

    result = check_folder("test_folder")
    print("Safe files mili:", result)

    with open("test_folder/model.pkl", "w") as f:
        f.write("dangerous pickle data")

    try:
        check_folder("test_folder")
        print("GALAT: khatarnak file pakdi nahi gayi!")
    except Exception as e:
        print("SAHI: file refuse ho gayi ->", e)
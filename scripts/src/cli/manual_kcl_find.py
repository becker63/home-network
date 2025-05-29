from fixtures import find_kcl_files, DirEnum

def quick_check():
    print("=== Filtering out FRP_SCHEMA ===")
    out1 = find_kcl_files(filter_fn=lambda kf: kf.dirname != DirEnum.FRP_SCHEMA)
    for file in out1:
        print(file.dirname, file.path)

    print("\n=== No filter (all files) ===")
    out2 = find_kcl_files(filter_fn=lambda kf: True)
    for file in out2:
        print(file.dirname, file.path)

if __name__ == "__main__":
    quick_check()

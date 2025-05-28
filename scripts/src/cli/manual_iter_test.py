from lib.project_iter import process_kcl_files, DirEnum

def quick_check():
    print("=== Filtering out FRP_SCHEMA ===")
    process_kcl_files(filter_fn=lambda kf: kf.dirname != DirEnum.FRP_SCHEMA)

    print("\n=== No filter (all files) ===")
    process_kcl_files(filter_fn=lambda kf: True)

if __name__ == "__main__":
    quick_check()

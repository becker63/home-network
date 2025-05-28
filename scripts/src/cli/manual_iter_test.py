from lib.project_iter import project_filter_enum, DirEnum

def quick_check():
    print("=== Filtering out FRP_SCHEMA ===")
    project_filter_enum(filter_fn=lambda kf: kf.dirname != DirEnum.FRP_SCHEMA)

    print("\n=== No filter (all files) ===")
    project_filter_enum(filter_fn=lambda kf: True)

if __name__ == "__main__":
    quick_check()

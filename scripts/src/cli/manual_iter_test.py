from lib.project_iter import process_kcl_files, DirEnum, KFile
import time
import hashlib

# Our code is currently not supposed to print anything if we dont pass a callback
def nothing_callback(kf: KFile):
    # Use SHA256 hash of the path to generate a consistent pseudo-random delay
    h = hashlib.sha256(str(kf.path).encode()).hexdigest()
    delay = (int(h[:4], 16) % 2000) / 1000.0  # Delay between 0.0 and 2.0 seconds
    time.sleep(delay)

def quick_check():
    process_kcl_files(
        filter_fn=lambda kf: kf.dirname != DirEnum.FRP_SCHEMA,
        callback=nothing_callback,
        title="Filtering out FRP_SCHEMA"
    )

    process_kcl_files(
        callback=nothing_callback,
        title="No filter (all files)"
    )

if __name__ == "__main__":
    quick_check()

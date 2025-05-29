from lib.project_iter import process_kcl_files, DirEnum, KFile
import time
import hashlib
import random


def nothing_callback(kf: KFile) -> None:
    h = hashlib.sha256(str(kf.path).encode()).hexdigest()
    delay = (int(h[:4], 16) % 10000) / 1000.0  # 0.0–2.0s delay
    print("before delay")
    time.sleep(delay)

    print(f"echo Processed {kf.path.name}\ndone in {delay:.2f}s")
    if random.random() < 0.2:  # simulate occasional stderr
        raise RuntimeError(f"Fake error in {kf.path.name}")



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

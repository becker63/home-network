from lib.project_iter import process_kcl_files, DirEnum, KFile
import time
import hashlib
from random import randrange
from lib.helpers import run_command

def nothing_callback(kf: KFile) -> str:
    h = hashlib.sha256(str(kf.path).encode()).hexdigest()
    delay = (int(h[:4], 16) % 5000.0) / 1000.0  # 0.0–2.0s delay
    time.sleep(delay)

    # Build the echo command with the message
    message = f"Processed {kf.path.name}\ndone in {delay:.2f}s"

    # Run the echo command via your helper, which raises CommandError on failure
    output = run_command(["echo", message], kf_name=kf.path.name)

    # Simulate occasional error to test error handling
    if randrange(1, 100) == 2:
        cmd = ["bash", "-c", "sleep 1 && echo 'About to fail...' && exit 1"]
        # run_command(cmd, kf_name=kf.path.name)

    return output



def quick_check():
    process_kcl_files(
        filter_fn=lambda kf: kf.dirname != DirEnum.FRP_SCHEMA,
        callback=nothing_callback,
        title="test"
        #title="Filtering out FRP_SCHEMA"
    )

    process_kcl_files(
        callback=nothing_callback,
        title="test2"
        #title="No filter (all files)"
    )


if __name__ == "__main__":
    quick_check()

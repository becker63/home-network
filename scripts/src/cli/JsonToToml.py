#!/usr/bin/env python3
import sys
import json
import toml

def main():
    try:
        data = json.load(sys.stdin)
        print(toml.dumps(data))
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl-C). Exiting safely.", file=sys.stderr)
        sys.exit(130)  # 128 + SIGINT (2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

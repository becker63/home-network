import argparse

def main():
    parser = argparse.ArgumentParser(description="Test CLI script")

    parser.add_argument("--name", type=str, help="Your name")
    parser.add_argument("--count", type=int, default=1, help="Number of times to repeat")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    for i in range(args.count):
        if args.verbose:
            print(f"[{i+1}] Hello, {args.name or 'world'}!")
        else:
            print(f"Hello, {args.name or 'world'}")

if __name__ == "__main__":
    main()
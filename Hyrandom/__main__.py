import argparse
import sys
from . import token_urlsafe, token_hex, get_current_engine, benchmark

def main():
    parser = argparse.ArgumentParser(
        description="hyrandom - High-performance CSPRNG CLI Tool",
        epilog="Example: hyrandom token --length 64"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- 1. Token Command ---
    token_parser = subparsers.add_parser("token", help="Generate a secure random token")
    token_parser.add_argument("-l", "--length", type=int, default=32, help="Length in bytes (default: 32)")
    token_parser.add_argument("-f", "--format", choices=["urlsafe", "hex"], default="urlsafe", help="Output format")

    # --- 2. Info Command ---
    subparsers.add_parser("info", help="Show the currently active engine and backend")

    # --- 3. Benchmark Command ---
    bench_parser = subparsers.add_parser("bench", help="Run performance benchmark on current machine")
    bench_parser.add_argument("-i", "--iterations", type=int, default=1_000_000, help="Number of iterations")

    args = parser.parse_args()

    # --- Command Execution Logic ---
    if args.command == "token":
        if args.format == "urlsafe":
            print(token_urlsafe(args.length))
        else:
            print(token_hex(args.length))
            
    elif args.command == "info":
        print(f"🔒 Active Engine: {get_current_engine()}")
        
    elif args.command == "bench":
        benchmark(args.iterations)
        
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
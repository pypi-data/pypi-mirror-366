#!/usr/bin/env python3
"""
dpncy CLI
"""
import sys
import argparse
from .core import Dpncy, ConfigManager

def print_header(title):
    """Prints a consistent, pretty header for CLI sections."""
    print("\n" + "="*60)
    print(f"  🚀 {title}")
    print("="*60)

import textwrap

def create_parser():
    """Creates and configures the argument parser."""
    # This formatter_class is key to making our new help text look good.
    # The epilog provides examples of the most important commands.
    parser = argparse.ArgumentParser(
        prog='dpncy',
        description='The intelligent Python package manager that solves dependency hell.',
        formatter_class=argparse.RawTextHelpFormatter, # Prevents argparse from messing up our formatting
        epilog=textwrap.dedent('''\
            
        Common Commands:
          dpncy install <package>   Install a package with downgrade protection.
          dpncy list                See all installed packages and their health.
          dpncy status              Check the health of your multi-version environment.
          dpncy info <package>      Get a detailed dashboard for a specific package.
          dpncy demo                Run the interactive showcase to see the magic.
        ''')
    )
    
    subparsers = parser.add_subparsers(dest='command', help='All available commands:', required=True)

    install_parser = subparsers.add_parser('install', help='Install packages (with downgrade protection)')
    install_parser.add_argument('packages', nargs='+', help='Packages to install (e.g., "requests==2.25.1")')

    info_parser = subparsers.add_parser('info', help='Show detailed package information with interactive version selection')
    info_parser.add_argument('package', help='Package name to inspect')
    info_parser.add_argument('--version', default='active', help='Specific version to inspect')

    list_parser = subparsers.add_parser('list', help='List installed packages')
    list_parser.add_argument('filter', nargs='?', help='Optional filter pattern for package names')

    status_parser = subparsers.add_parser('status', help='Show multi-version system status')

    demo_parser = subparsers.add_parser('demo', help='Run the interactive, automated demo')

    stress_parser = subparsers.add_parser('stress-test', help='Run the ultimate stress test with heavy-duty packages.')

    reset_parser = subparsers.add_parser('reset', help='DELETE and rebuild the dpncy knowledge base in Redis')
    reset_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')

    rebuild_parser = subparsers.add_parser('rebuild-kb', help='Force a full rebuild of the knowledge base without deleting')
    rebuild_parser.add_argument('--force', '-f', action='store_true', help='Ignore cache and force re-processing of all metadata')

    return parser

def main():
    """The main entry point for the CLI."""
    
    if len(sys.argv) == 1:
        cm = ConfigManager()
        if not cm.config_path.exists():
            cm._first_time_setup()
            print("\n" + "="*50)
            print("🚀 Welcome to dpncy! Your setup is complete.")
            print("To see the magic in action, we highly recommend running the demo:")
            print("\n    dpncy demo\n")
            print("="*50)
        else:
            print("👋 Welcome back to dpncy!")
            print("   Run `dpncy status` to see your environment.")
            print("   Run `dpncy demo` for a showcase of features.")
            print("   Run `dpncy --help` for all commands.")
        return 0

    parser = create_parser()
    args = parser.parse_args()

    dpncy = Dpncy()

    try:
        if args.command == 'install':
            return dpncy.smart_install(args.packages)
        elif args.command == 'info':
            return dpncy.show_package_info(args.package, args.version)
        elif args.command == 'list':
            return dpncy.list_packages(args.filter)
        elif args.command == 'status':
            return dpncy.show_multiversion_status()
        elif args.command == 'demo':
            from .demo import run_demo
            return run_demo()
        elif args.command == 'stress-test':
            from . import stress_test
            print_header("DPNCY Ultimate Stress Test")
            print("This test will install, bubble, and test multiple large scientific packages.")
            print("\n⚠️  This will download several hundred MB and may take several minutes.")

            if input("\nProceed with the stress test? (y/n): ").lower() != 'y':
                print("Stress test cancelled.")
                return 0
            
            stress_test.run()
            return 0
        elif args.command == 'reset':
            return dpncy.reset_knowledge_base(force=args.yes)
        elif args.command == 'rebuild-kb':
            if hasattr(dpncy, 'rebuild_knowledge_base'):
                 return dpncy.rebuild_knowledge_base(force=args.force)
            else:
                 print("Error: `rebuild_knowledge_base` method not yet implemented in core.py")
                 return 1
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ An unexpected top-level error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
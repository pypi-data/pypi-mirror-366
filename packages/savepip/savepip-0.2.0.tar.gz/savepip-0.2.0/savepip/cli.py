#!/usr/bin/env python
import argparse
import sys
from .core import DependencySaver
from .memory_manager import MemoryManager

def main():
    parser = argparse.ArgumentParser(description="Install packages and save clean dependencies")
    
    parser.add_argument("command", nargs="?", default="install", 
                      help="Command (install, save, mk-category, use-category, cur-category, ls-category)")
    parser.add_argument("packages", nargs="*", help="Packages to install or category name")
    parser.add_argument("-m", "--manager", choices=["pip", "conda"], default="pip",
                      help="Package manager to use (default: pip)")
    parser.add_argument("-o", "--output", help="Output file for dependencies")
    parser.add_argument("-u", "--upgrade", action="store_true", 
                      help="Upgrade packages if already installed")
    parser.add_argument("-d", "--dev", action="store_true", 
                      help="Save as development dependencies")
    parser.add_argument("-c", "--categories", nargs="*", help="Categories to save dependencies from")
    
    args = parser.parse_args()
    
    if args.command == "install" and not args.packages:
        parser.print_help()
        return False
    
    if args.command not in ["install", "save", "mk-category", "use-category", "cur-category", "ls-category"]:
        args.packages.insert(0, args.command)
        args.command = "install"
    
    memory_manager = MemoryManager()
    
    if args.command == "mk-category":
        if not args.packages:
            print("Please provide a category name.")
            return False
        return memory_manager.create_category(args.packages[0])
    
    if args.command == "use-category":
        if not args.packages:
            print("Please provide a category name.")
            return False
        return memory_manager.use_category(args.packages[0])
    
    if args.command == "cur-category":
        current_category = memory_manager.show_current_category()
        print(f"Current category: {current_category}")
        return True
    
    if args.command == "ls-category":
        categories = memory_manager.list_categories()
        for category, is_current in categories:
            if is_current:
                print(f"* {category}")
            else:
                print(f"  {category}")
        return True
    
    saver = DependencySaver(output_file=args.output, manager=args.manager, memory_manager=memory_manager)
    
    if args.command == "save":
        return saver._save_dependencies(args.dev, args.categories)
    else:  # install command
        return saver.install_and_save(args.packages, args.upgrade, args.dev)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Memory Manager Module

This module provides the MemoryManager class which handles the storage and
retrieval of package dependencies categorized under different categories.
It uses a JSON file to persist the data and ensures a default category is
always present.

Classes:
    MemoryManager

Author: Achraf Mataich
Date: 2025-03-11
"""

import os
import json

class MemoryManager:
    """
    MemoryManager handles the storage and retrieval of package dependencies
    categorized under different categories. It uses a JSON file to persist
    the data and ensures a default category is always present.
    """
    def __init__(self):
        """
        Initializes the MemoryManager by setting up the base directory,
        loading the memory from the JSON file, and ensuring the default
        category exists.
        """
        self.base_dir = self._get_base_dir()
        self.memory_file = os.path.join(self.base_dir, "memory.json")
        self.memory = self._load_memory()
        self._ensure_default_category()

    def _get_base_dir(self):
        """
        Determines the base directory for storing the memory file.
        If a virtual environment is active, it uses the virtual environment's
        directory; otherwise, it uses the user's home directory.
        
        Returns:
            str: The base directory path.
        """
        if os.getenv("VIRTUAL_ENV"):
            return os.path.join(os.getenv("VIRTUAL_ENV"), ".savepip")
        else:
            return os.path.join(os.path.expanduser("~"), ".savepip")

    def _load_memory(self):
        """
        Loads the memory from the JSON file if it exists. If the file does not
        exist, it initializes the memory with default values.
        
        Returns:
            dict: The loaded or initialized memory.
        """
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {"categories": {}, "current_category": None}

    def _save_memory(self):
        """
        Saves the current memory state to the JSON file. Ensures the base
        directory exists before saving.
        """
        os.makedirs(self.base_dir, exist_ok=True)
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    def _ensure_default_category(self):
        """
        Ensures that a default category exists in the memory. If no current
        category is set, it sets the default category as the current category.
        """
        if "default" not in self.memory["categories"]:
            self.memory["categories"]["default"] = []
        if not self.memory["current_category"]:
            self.memory["current_category"] = "default"
        self._save_memory()

    def create_category(self, name):
        """
        Creates a new category with the given name. If the category already
        exists, it prints a message and returns False.
        
        Args:
            name (str): The name of the category to create.
        
        Returns:
            bool: True if the category was created, False otherwise.
        """
        if name in self.memory["categories"]:
            print(f"Category '{name}' already exists.")
            return False
        self.memory["categories"][name] = []
        self._save_memory()
        print(f"Category '{name}' created.")
        return True

    def use_category(self, name):
        """
        Sets the current category to the given name. If the category does not
        exist, it prints a message and returns False.
        
        Args:
            name (str): The name of the category to switch to.
        
        Returns:
            bool: True if the category was switched, False otherwise.
        """
        if name not in self.memory["categories"]:
            print(f"Category '{name}' does not exist.")
            return False
        self.memory["current_category"] = name
        self._save_memory()
        print(f"Switched to category '{name}'.")
        return True

    def add_dependency(self, package):
        """
        Adds a package dependency to the current category. If no category is
        selected, it prints a message and returns False.
        
        Args:
            package (str): The name of the package to add.
        
        Returns:
            bool: True if the package was added, False otherwise.
        """
        category = self.memory["current_category"]
        if not category:
            print("No category selected.")
            return False
        if package not in self.memory["categories"][category]:
            self.memory["categories"][category].append(package)
            self._save_memory()
        return True

    def get_dependencies(self, categories=None):
        """
        Retrieves the list of package dependencies for the specified categories.
        If no categories are specified, it retrieves dependencies for the current
        category.
        
        Args:
            categories (list, optional): The list of categories to retrieve dependencies for.
        
        Returns:
            list: The list of package dependencies.
        """
        if categories is None:
            categories = [self.memory["current_category"]]
        dependencies = set()
        for category in categories:
            if category in self.memory["categories"]:
                dependencies.update(self.memory["categories"][category])
        return list(dependencies)

    def show_current_category(self):
        """
        Returns the name of the current category.
        
        Returns:
            str: The name of the current category.
        """
        return self.memory["current_category"]

    def list_categories(self):
        """
        Lists all categories along with a flag indicating whether each category
        is the current category.
        
        Returns:
            list: A list of tuples containing the category name and a boolean flag.
        """
        categories = self.memory["categories"].keys()
        current_category = self.memory["current_category"]
        return [(category, category == current_category) for category in categories]

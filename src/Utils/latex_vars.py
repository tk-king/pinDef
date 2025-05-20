import os
import re

class LatexVars:
    def __init__(self, latex_folder):
        self.file_path = os.path.join(latex_folder, "vars.tex")
        self.load_file()

    def load_file(self):
        self.params = {}
        self.file_path = self.file_path
        if not self.file_path.endswith(".tex"):
            raise ValueError("File path must end with .tex")
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.params = self._parse_vars(f.read())
        else:
            self.params = {}

    def _parse_vars(self, content):
        pattern = r"\\newcommand{\\([a-zA-Z]+)}{((?:[^{}]*|{.*?})*)}"
        matches = re.findall(pattern, content)
        for command, value in matches:
            self.params[command] = value.replace("\\xspace", "")
        return self.params
    
    def __getitem__(self, key):
        return self.params[key]
    
    def __setitem__(self, key, value):
        # Mapping of digits to their written form
        number_map = {
            "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
            "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine"
        }

        # Replace digits in the key with their written form
        def replace_with_text(match):
            return number_map[match.group(0)]

        key_transformed = re.sub(r"\d", replace_with_text, key)
        key_transformed = key_transformed.replace(".", "")
        value = str(value)
        value = value.replace("{", r"\{").replace("}", r"\}")
        
        # Update the parameter and save
        self.params[key_transformed] = value
        print(f"[LATEXVARS] == Set {key_transformed} to {value}")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.save()
    
    def save(self):
        print("Saving latex vars to", self.file_path)
        with open(self.file_path, "w") as f:
            for key, value in self.params.items():
                f.write(f"\\newcommand{{\\{key}}}{{{value}\\xspace}}\n")


class LatexTable():
    def __init__(self, path: str):
        self.path = path
        self.header = None
        self.rows = []

    def add_header(self, header):
        self.header = header

    def add_row(self, row):
        self.rows.append(row)
        self._save()

    def _save(self):
        with open(self.path, "w") as f:
            # Write table structure
            f.write("\\begin{tabular}{|" + "|".join(["c"] * len(self.header)) + "|}\n")
            f.write("\\hline\n")
            # Write the header
            f.write(" & ".join(self.header) + " \\\\\n")
            f.write("\\hline\n")
            # Write the rows
            for row in self.rows:
                f.write(" & ".join(map(str, row)) + " \\\\\n")
            f.write("\\hline\n")
            f.write("\\end{tabular}\n")
        
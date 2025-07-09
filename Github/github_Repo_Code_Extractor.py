import os
import json
from git import Repo
from collections import defaultdict
import pathlib

"""
Class RepoCodeExtractor is designed to clone a Git repository, extract code files with specified extensions,
read their contents, and export this information to a JSON file. It also supports filtering files by author if specified.
It handles cloning, file reading, author extraction, and JSON export, making it useful for analyzing code repositories.
"""
class RepoCodeExtractor:
    def __init__(self, repo_url, clone_dir=None, output_json=None, code_extensions=None, filter_author=None):
        self.repo_url = repo_url
        self.clone_dir = repo_url.split("/")[-2] + "/repository/" + repo_url.split("/")[-1] if not clone_dir else clone_dir
        self.code_extensions = code_extensions or {
            ".ipynb", ".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".kt", ".swift"
        }
        self.filter_author = filter_author

        self.output_json = repo_url.split("/")[-2] + "/json/"
        if output_json:
            self.output_json += output_json
        elif filter_author:
            self.output_json += repo_url.split("/")[-1] + "_" + "_".join(filter_author.split(" ")) + ".json"
        else:
            self.output_json += repo_url.split("/")[-1] + ".json"

    # Clones the repository if it doesn't exist locally
    def _clone_repo(self):
        if not os.path.exists(self.clone_dir):
            print(f"Clonage du repo depuis {self.repo_url}...")
            try:
                Repo.clone_from(self.repo_url, self.clone_dir)
                print("Repo cloné avec succès.")
            except Exception as e:
                print(f"[!] Échec du clonage : {e}")
                raise e  # ou return False si tu veux le gérer différemment
        else:
            print("Repo déjà cloné localement.")


    # Retrieves all code files in the cloned repository
    def _get_all_code_files(self):
        code_files = []
        for root, _, files in os.walk(self.clone_dir):
            for file in files:
                if any(file.endswith(ext) for ext in self.code_extensions):
                    code_files.append(os.path.join(root, file))
        return code_files

    # Reads the content of each code file and returns a list of dictionaries with file paths and contents
    def _read_files(self, file_paths):
        file_contents = []
        for path in file_paths:
            try:
                with open(path, 'r', encoding="utf-8", errors="ignore") as f:
                    rel_path = os.path.relpath(path, self.clone_dir)
                    content = f.read()
                    file_contents.append({
                        "file": rel_path,
                        "content": content
                    })
            except Exception as e:
                print(f"[!] Erreur lecture {path}: {e}")
        return file_contents

    # Extracts authors for each file based on commit history
    def _get_file_authors(self):
        print("Extraction des auteurs par fichier...")
        repo = Repo(self.clone_dir)
        authors = defaultdict(set)
        for commit in repo.iter_commits():
            for file in commit.stats.files:
                authors[file].add(commit.author.name)
        return {f: list(a) for f, a in authors.items()}

    # Attaches authors to each file in the file data
    def _attach_authors(self, file_data, authors_dict):
        for f in file_data:
            normalized_path = pathlib.Path(f["file"]).as_posix()
            f["authors"] = authors_dict.get(normalized_path, [])
        return file_data

    # Filters files by a specific author if filter_author is set
    def _filter_by_author(self, file_data):
        if not self.filter_author:
            return file_data
        return [f for f in file_data if self.filter_author in f.get("authors", [])]

    # Main method to export the code files and their authors to a JSON file
    def export(self):
        self._clone_repo()
        code_files = self._get_all_code_files()
        print(f"{len(code_files)} fichiers de code détectés.")

        file_data = self._read_files(code_files)
        authors = self._get_file_authors()
        file_data = self._attach_authors(file_data, authors)
        file_data = self._filter_by_author(file_data)

        # 🔧 Création du dossier si manquant
        os.makedirs(os.path.dirname(self.output_json), exist_ok=True)

        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)

        print(f"[✔] Export terminé dans {self.output_json}")


# Example usage:
# if __name__ == "__main__":
#     extractor = RepoCodeExtractor("https://github.com/KentinPaille/ChessStatePrediction")
#     extractor.export()

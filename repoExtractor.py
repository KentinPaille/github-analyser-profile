import os
import json
from git import Repo
from collections import defaultdict
import pathlib

class RepoCodeExtractor:
    def __init__(self, repo_url, clone_dir=None, output_json=None, code_extensions=None):
        self.repo_url = repo_url
        self.clone_dir = repo_url.split("/")[-1] if not clone_dir else clone_dir
        self.output_json = repo_url.split("/")[-1] + ".json" if not output_json else output_json
        self.code_extensions = code_extensions or {
            ".ipynb", ".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".kt", ".swift"
        }

    def clone_repo(self):
        if not os.path.exists(self.clone_dir):
            print(f"Clonage du repo depuis {self.repo_url}...")
            Repo.clone_from(self.repo_url, self.clone_dir)
            print("Repo cloné avec succès.")
        else:
            print("Repo déjà cloné localement.")

    def get_all_code_files(self):
        code_files = []
        for root, _, files in os.walk(self.clone_dir):
            for file in files:
                if any(file.endswith(ext) for ext in self.code_extensions):
                    code_files.append(os.path.join(root, file))
        return code_files

    def read_files(self, file_paths):
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

    def get_file_authors(self):
        print("Extraction des auteurs par fichier...")
        repo = Repo(self.clone_dir)
        authors = defaultdict(set)
        for commit in repo.iter_commits():
            for file in commit.stats.files:
                authors[file].add(commit.author.name)
        return {f: list(a) for f, a in authors.items()}

    def attach_authors(self, file_data, authors_dict):
        for f in file_data:
            normalized_path = pathlib.Path(f["file"]).as_posix()
            f["authors"] = authors_dict.get(normalized_path, [])
        return file_data

    def export(self):
        self.clone_repo()
        code_files = self.get_all_code_files()
        print(f"{len(code_files)} fichiers de code détectés.")

        file_data = self.read_files(code_files)
        authors = self.get_file_authors()
        file_data = self.attach_authors(file_data, authors)

        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)

        print(f"[✔] Export terminé dans {self.output_json}")

if __name__ == "__main__":
    extractor = RepoCodeExtractor("https://github.com/KentinPaille/ChessStatePrediction")
    extractor.export()

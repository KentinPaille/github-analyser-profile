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
        self.clone_dir = repo_url.split("/")[3] + "/repository/" + repo_url.split("/")[4] if not clone_dir else clone_dir
        self.code_extensions = code_extensions or {
            ".ipynb", ".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".kt", ".swift"
        }
        self.filter_author = filter_author

        self.output_json = repo_url.split("/")[3] + "/json/"
        if output_json:
            self.output_json += output_json
        elif filter_author:
            self.output_json += repo_url.split("/")[4] + "_" + "_".join(filter_author.split(" ")) + ".json"
        else:
            self.output_json += repo_url.split("/")[4] + ".json"

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

    # Retrieves authors for each file up to a specific commit
    def _get_file_authors_up_to_commit(self, repo, commit_sha):
        authors = defaultdict(set)
        for commit in repo.iter_commits(rev=commit_sha):
            for file in commit.stats.files:
                authors[file].add(commit.author.name)
        return {f: list(a) for f, a in authors.items()}

    # Exports evenly spaced history states from the repository
    def export_evenly_spaced_history_states(self, snapshot_count=10):
        self._clone_repo()
        repo = Repo(self.clone_dir)
        all_commits = list(repo.iter_commits())
        all_commits.reverse()  # Du plus ancien au plus récent

        if len(all_commits) < snapshot_count:
            print(f"[!] Seulement {len(all_commits)} commits. Tous seront pris.")
            selected_commits = all_commits
        else:
            step = len(all_commits) // snapshot_count
            selected_commits = [all_commits[i * step] for i in range(snapshot_count)]

        history_snapshots = []

        for commit in selected_commits:
            print(f"[→] Snapshot {commit.hexsha[:7]} - {commit.author.name} - {commit.committed_datetime}")
            repo.git.checkout(commit.hexsha)

            # Lecture des fichiers à l'état de ce commit
            code_files = self._get_all_code_files()
            file_data = self._read_files(code_files)

            # Récupération des auteurs jusqu'à CE commit
            authors = self._get_file_authors_up_to_commit(repo, commit.hexsha)
            file_data = self._attach_authors(file_data, authors)
            filtered = self._filter_by_author(file_data)

            history_snapshots.append({
                "commit": commit.hexsha,
                "author": commit.author.name,
                "date": str(commit.committed_datetime),
                "files": filtered
            })

        # Revenir sur la branche principale (main/master)
        try:
            repo.git.checkout("main")
        except:
            repo.git.checkout("master")

        # Sauvegarde dans JSON
        os.makedirs(os.path.dirname(self.output_json), exist_ok=True)
        output_path = self.output_json.replace(".json", ".history.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(history_snapshots, f, indent=2, ensure_ascii=False)

        print(f"[✔] Export de {len(history_snapshots)} snapshots terminé dans {output_path}")




# Example usage:
if __name__ == "__main__":
    extractor = RepoCodeExtractor("https://github.com/KentinPaille/ChessStatePrediction")
    extractor.export_evenly_spaced_history_states()

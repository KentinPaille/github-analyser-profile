import requests

class GithubUserReposFetcher:
    def __init__(self, username):
        self.username = username

    def get_all_repos(self):
        repos = []
        page = 1
        while True:
            url = f"https://api.github.com/users/{self.username}/repos?per_page=100&page={page}"
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Erreur API GitHub: {response.status_code} - {response.text}")
            data = response.json()
            if not data:
                break
            repos.extend([repo['clone_url'] for repo in data])
            page += 1
        return repos

    def get_user_commits(self, username, token=None, max_pages=5):
        headers = {
            "Accept": "application/vnd.github.cloak-preview"
        }
        if token:
            headers["Authorization"] = f"token {token}"

        all_commits = []

        for page in range(1, max_pages + 1):
            
            url = f"https://api.github.com/search/commits?q=author:{username}&per_page=100&page={page}"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"[!] Erreur GitHub API : {response.status_code}")
                break

            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            
            for item in items:
                print(item)
                break
                commit = item["commit"]
                repo_name = item["repository"]["full_name"]
                all_commits.append({
                    "repo": repo_name,
                    "sha": item["sha"],
                    "date": commit["author"]["date"],
                    "message": commit["message"]
                })
                print(all_commits[-1])
            break
        return all_commits

# Example usage:
# if __name__ == "__main__":
#     fetcher = GithubUserReposFetcher("KentinPaille")
#     repos = fetcher.get_all_repos()
#     print(f"Found {len(repos)} repositories for user 'KentinPaille':")

#     commit = fetcher.get_user_commits("KentinPaille")

#     print(f"Found {len(commit)} commits for user 'KentinPaille':")
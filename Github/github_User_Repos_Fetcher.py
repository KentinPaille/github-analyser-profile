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
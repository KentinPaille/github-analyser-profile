from Github.github_User_Repos_Fetcher import GithubUserReposFetcher
from Github.github_Repo_Code_Extractor import RepoCodeExtractor

if __name__ == "__main__":
    username = "KentinPaille"
    fetcher = GithubUserReposFetcher(username)
    repos = fetcher.get_all_repos()

    for repo in repos:
        extractor = RepoCodeExtractor(repo)
        extractor.export()

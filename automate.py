import os
import time
from typing import Dict, List
import logging

import git
import github
import yaml
from github import Github

class GitHubAutomator:
    """A class to automate the Testing of Staging GitHub operations."""

    def __init__(self, access_token: str, base_url: str, username: str, repo_name: str, repo_dir: str):
        """
        Initialize the GitHubAutomator class.

        :param access_token: GitHub access token.
        :param base_url: Base URL for the GitHub instance.
        :param username: GitHub username.
        :param repo_name: Name of the repository.
        :param repo_dir: Local directory for the repository.
        """
        self.github = Github(base_url=base_url, login_or_token=access_token)
        self.user = self.github.get_user(username)
        self.repo_name = repo_name
        self.repo_dir = repo_dir

        # Configure instance-specific logging
        self.logger = logging.getLogger(f'GitHubAutomator_{id(self)}')
        handler_info = logging.FileHandler('info.log')
        handler_error = logging.FileHandler('error.log')
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
        handler_info.setFormatter(formatter)
        handler_error.setFormatter(formatter)
        handler_info.setLevel(logging.INFO)
        handler_error.setLevel(logging.ERROR)
        self.logger.addHandler(handler_info)
        self.logger.addHandler(handler_error)
        self.logger.setLevel(logging.INFO)

    def create_and_initialize_repository(self) -> None:
        """Create a new repository and initialize it both remotely and locally."""
        try:
            self.repo = self.github.get_user().get_repo(self.repo_name)
            self.logger.info(f'Repository {self.repo_name} already exists. Using the existing repository.')
        except github.UnknownObjectException:
            try:
                self.repo = self.github.get_user().create_repo(self.repo_name)
                self.logger.info(f'Repository {self.repo_name} created successfully.')
            except Exception as e:
                self.logger.error(f'Failed to create repository {self.repo_name}. Error: {e}')

        try:
            if not os.path.exists(self.repo_dir):
                os.makedirs(self.repo_dir)
                self.logger.info(f'Directory {self.repo_dir} created successfully.')
        except Exception as e:
            self.logger.error(f'Failed to create directory {self.repo_dir}. Error: {e}')

        try:
            os.chdir(self.repo_dir)
            os.system(f'echo "# {self.repo_name}" >> README.md')
            repo_local = git.Repo.init(self.repo_dir)
            self.logger.info('Local repository initialized successfully.')
        except Exception as e:
            self.logger.error(f'Failed to initialize local repository. Error: {e}')

        try:
            repo_local.git.add('README.md')
            repo_local.git.commit('-m', 'first commit')
            repo_local.git.branch('-M', 'main')
            repo_local.git.remote('add', 'origin', self.repo.clone_url)
            repo_local.git.push('-u', 'origin', 'main')
            self.logger.info('Initial commit pushed to main branch.')
        except Exception as e:
            self.logger.error(f'Failed to push initial commit to main branch. Error: {e}')

    def commit_and_push(self, branch_name: str, file_name: str, commit_message: str) -> None:
        """
        Commit changes to a file and push to a specified branch.

        :param branch_name: Name of the branch to push to.
        :param file_name: Name of the file to commit.
        :param commit_message: Commit message.
        """
        try:
            os.chdir(self.repo_dir)
            repo_local = git.Repo(self.repo_dir)
            repo_local.git.checkout(branch_name)
            with open(file_name, 'a') as f:
                f.write(commit_message + '\n')
            repo_local.git.add(file_name)
            repo_local.git.commit('-m', commit_message)
            repo_local.git.push('--set-upstream', 'origin', branch_name)
            self.logger.info(f'Changes pushed to {branch_name} successfully.')
        except Exception as e:
            self.logger.error(f'Failed to push changes to {branch_name}. Error: {e}')

    def create_and_merge_pull_request(self, head: str, base: str, title: str, body: str) -> None:
        """
        Create and merge a pull request.

        :param head: Source branch for the pull request.
        :param base: Target branch for the pull request.
        :param title: Title of the pull request.
        :param body: Body/description of the pull request.
        """
        try:
            pr = self.repo.create_pull(title=title, body=body, head=head, base=base)
            if pr:
                pr.merge()
                self.logger.info(f'Pull request from {head} to {base} created and merged.')
            else:
                self.logger.error(f'Failed to create or merge pull request from {head} to {base}.')
        except Exception as e:
            self.logger.error(f'Failed to create or merge pull request from {head} to {base}. Error: {e}')

    def create_conflict(self, file_name: str, base_content: str, branch_content: str) -> None:
        """
        Create a conflict in a file between the main branch and a new branch.

        :param file_name: Name of the file to create a conflict in.
        :param base_content: Content for the main branch.
        :param branch_content: Content for the new branch.
        """
        try:
            self.commit_and_push('main', file_name, base_content)
            if 'main' in [ref.name for ref in git.Repo(self.repo_dir).refs]:
                os.chdir(self.repo_dir)
                repo_local = git.Repo(self.repo_dir)
                repo_local.git.checkout('-b', 'conflict-branch')
                with open(file_name, 'w') as f:
                    f.write(branch_content)
                repo_local.git.add(file_name)
                repo_local.git.commit('-m', 'Create conflict')
                repo_local.git.push('--set-upstream', 'origin', 'conflict-branch')
                self.logger.info('Conflict created in CONFLICT.md successfully.')
            else:
                self.logger.error('Failed to push changes to main. Skipping conflict creation.')
        except Exception as e:
            self.logger.error(f'Failed to create conflict in {file_name}. Error: {e}')

    def resolve_conflict(self, file_name: str, resolved_content: str) -> None:
        """
        Resolve a conflict in a file.

        :param file_name: Name of the file with the conflict.
        :param resolved_content: Resolved content for the file.
        """
        try:
            os.chdir(self.repo_dir)
            repo_local = git.Repo(self.repo_dir)
            if 'conflict-branch' in [ref.name for ref in repo_local.refs]:
                repo_local.git.checkout('conflict-branch')
                with open(file_name, 'w') as f:
                    f.write(resolved_content)
                repo_local.git.add(file_name)
                repo_local.git.commit('-m', 'Resolve conflict')
                repo_local.git.push()
                self.logger.info(f'Conflict in {file_name} resolved successfully.')
            else:
                self.logger.error(f'Failed to resolve conflict in {file_name}. "conflict-branch" does not exist.')
        except Exception as e:
            self.logger.error(f'Failed to resolve conflict in {file_name}. Error: {e}')

    def comment_on_pull_request(self, pr_number: int, comment: str) -> None:
        """
        Add a comment to a pull request.

        :param pr_number: Pull request number.
        :param comment: Comment text.
        """
        try:
            pr = self.repo.get_pull(pr_number)
            if pr:
                pr.create_issue_comment(comment)
                self.logger.info(f'Comment added to PR #{pr_number}.')
            else:
                self.logger.error(f'Failed to add comment to PR #{pr_number}.')
        except Exception as e:
            self.logger.error(f'Failed to add comment to PR #{pr_number}. Error: {e}')

    def test_general_git_commands(self) -> None:
        """Test various git commands."""
        try:
            repo_local = git.Repo(self.repo_dir)
            if repo_local:
                self.logger.info(repo_local.git.status())
                self.logger.info(repo_local.git.log('-1'))
                self.logger.info(repo_local.git.show('-1'))
                self.logger.info(repo_local.git.branch('-a'))
                self.logger.info('Git commands tested successfully.')
            else:
                self.logger.error('Failed to test git commands.')
        except Exception as e:
            self.logger.error(f'Failed to test git commands. Error: {e}')

    def test_github_api(self) -> None:
        """Test various GitHub API operations."""
        try:
            if self.repo:
                self.logger.info(self.repo)
                open_prs = self.repo.get_pulls(state='open')
                for pr in open_prs:
                    self.logger.info(pr)
                self.logger.info('GitHub API tested successfully.')
            else:
                self.logger.error('Failed to test GitHub API.')
        except Exception as e:
            self.logger.error(f'Failed to test GitHub API. Error: {e}')

    def create_branches_and_make_changes(self, branches: Dict[str, str]) -> None:
        """
        Create branches, make changes, and push to remote.

        :param branches: Dictionary of branch names and their content.
        """
        try:
            os.chdir(self.repo_dir)
            repo_local = git.Repo(self.repo_dir)
            for idx, (branch, content) in enumerate(branches.items()):
                if branch in [ref.name for ref in repo_local.refs]:
                    repo_local.git.checkout(branch)
                else:
                    repo_local.git.checkout('-b', branch)
                mock_file_name = f'{branch}_mock.txt'
                with open(mock_file_name, 'w') as f:
                    f.write(f'def mock_function_{branch}():\n')
                    f.write(f"    print('This is a mock function from {branch}')\n")
                repo_local.git.add(mock_file_name)
                repo_local.git.commit('-m', f'Added mock function in {branch}')
                repo_local.git.push('--set-upstream', 'origin', branch)
                pr = self.repo.create_pull(title=f'Merge {branch} to main', body=f'Merging changes from {branch}', head=branch, base='main')
                self.comment_on_pull_request(pr.number, f'Reviewing changes from {branch}. Looks good!')
                if idx < len(branches) - 1:
                    pr.merge()
                self.logger.info(f'Branch {branch} created and changes pushed successfully.')
        except Exception as e:
            self.logger.error(f'Failed to create branch or push changes. Error: {e}')

    def delete_repos_with_automation(self) -> None:
        """Delete repositories with 'automation' in their name."""
        try:
            for repo in self.user.get_repos():
                if 'automation' in repo.name.lower():
                    repo.delete()
                    self.logger.info(f'Deleted repository: {repo.name}')
        except Exception as e:
            self.logger.error(f'Failed to delete repositories with "automation" in their name. Error: {e}')

def main() -> None:
    """Main function to execute the GitHub automator."""

    # Load credentials from YAML file
    try:
        with open('configuration.yaml', 'r') as file:
            config = yaml.safe_load(file)

        credentials = config.get('credentials', {})
        ACCESS_TOKEN = credentials.get('access_token', '')
        GITHUB_ENTERPRISE_URL = credentials.get('base_url', '')
        USER_NAME = credentials.get('username', '')
        REPO_NAME = credentials.get('repo_name', '')
        REPO_DIR = credentials.get('repo_dir', '')

        automator = GitHubAutomator(ACCESS_TOKEN, GITHUB_ENTERPRISE_URL, USER_NAME, REPO_NAME, REPO_DIR)
        automator.create_and_initialize_repository()
        automator.commit_and_push('main', 'README.md', 'Second commit')
        automator.create_conflict('CONFLICT.md', 'Base content\n', 'Branch content\n')
        time.sleep(2)
        automator.resolve_conflict('CONFLICT.md', 'Resolved content\n')
        automator.create_and_merge_pull_request('conflict-branch', 'main', 'Merge Conflict Branch', 'Testing conflict resolution')
        automator.test_general_git_commands()
        automator.test_github_api()
        automator.comment_on_pull_request(1, 'This is a test comment on PR #1.')
        branches = {
            'feature-1': 'Changes from feature-1',
            'feature-2': 'Changes from feature-2',
            'feature-3': 'Changes from feature-3'
        }
        automator.create_branches_and_make_changes(branches)
        automator.logger.info('Repository setup and operations completed.')

    except Exception as e:
        automator.logger.error(f'An error occurred: {e}')


if __name__ == '__main__':
    main()
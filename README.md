# GitHub Automator

GitHub Automator is a Python-based tool designed to automate various GitHub operations for easy GitHub Testing, such as creating and initializing repositories, committing and pushing changes, creating branches, creating and merging pull requests, generating conflicts and resolving it, comments on the pull requests, deleting repositories, testing important git commands and more. It is particularly useful for Testing Staging GitHub operations.

## Features

- **Create and Initialize Repository**: Allows for the creation and initialization of a new repository both remotely and locally.
- **Commit and Push**: Commits changes to a file and pushes them to a specified branch.
- **Create and Merge Pull Request**: Creates and merges a pull request between specified branches.
- **Create Conflict**: Creates a conflict in a file between the main branch and a new branch.
- **Resolve Conflict**: Resolves conflicts in a specified file.
- **Comment on Pull Request**: Adds a comment to a specified pull request.
- **Test General Git Commands**: Tests various git commands and prints their outputs.
- **Test GitHub API**: Tests various GitHub API operations and prints their outputs.
- **Create Branches and Make Changes**: Creates specified branches, makes changes, and pushes to remote.
- **Delete Repositories with 'automation' in their name**: Deletes all repositories of the user with 'automation' in their name.

## Logging

GitHub Automator utilizes Python's logging module to log informational messages and error messages. The logging mechanism is configured to output log messages to two separate files:

- `info.log`: This file contains informational messages about the operations performed by the tool, such as successful creation of repositories, successful push of commits, etc.
- `error.log`: This file contains error messages that provide information about any errors or exceptions encountered during the execution of the tool.

- Log Format
The log messages are formatted to include the timestamp, log level (INFO or ERROR), and the log message. Here is an example of a log message format:

- `2023-09-21 12:34:56 [INFO] - Repository MyRepo created successfully.`

## Prerequisites

- Python 3.x (Used: 3.11)
- GitHub Account
- Access Token with the necessary permissions
- `git` and `github` Python packages
- YAML configuration file with necessary credentials

## Setup

1. Clone or download the project repository to your local machine.
2. Install the required dependencies by running the following command:

```python
pip install -r requirements.txt
```

3. Create a `configuration.yaml` file in the project directory and populate it with the required configuration parameters. See the "Configuration" section below for details.

## Configuration

The `configuration.yaml` file contains important parameters for the GitHub Automator. It should have the following structure:

```yaml
credentials:
  access_token: your_github_access_token
  base_url: https://github-example.com/api/v3
  username: your_github_user_name
  repo_name: your_github_new_repository_name
  repo_dir: /path/to/clone/locally/your_github_new_repository_name
```

Replace the placeholder values with your actual GitHub credentials and configuration.

## Usage

Navigate to the project directory and run the following command:

```python
python automate.py
```

## Check Log Files
After running the tool, you can view the generated `info.log` and `error.log` files in the project directory to inspect the informational and error messages.

## Contributing

Contributions to the this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

This project is licensed under the `MIT License`.

## Acknowledgements
- PyGithub for providing the GitHub API Python client.
- GitPython for enabling Python interaction with Git.
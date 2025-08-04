

autovix Deployment Module Documentation
=======================================

Overview
--------
The `autovix` module is designed to automate the cloning, setup, and execution 
of multiple repositories for both backend (API) and frontend (UI) applications.

This configuration-driven automation supports:
- GitHub cloning using username and personal access token.
- Installing dependencies.
- Running projects with a custom command or development server.

Configuration Parameters (json_data)
------------------------------------

1. env_name (string)
   - Name of the environment or project group.
   - Example: "autovix"

2. git_data (object)
   - GitHub credentials to access repositories.
   - Keys:
     - username: GitHub username
     - token: GitHub personal access token
     - org_or_user: GitHub organization or user name

3. base_path (string)
   - Path where repositories will be cloned.
   - Example: "C:/deploy"

4. repositories (list of objects)
   - Each object contains deployment details for a repository.
   - Fields:
     - repo_name (string): Repository name
     - branch (string): Branch to clone
     - folder_name (string): Local folder name
     - is_ui (bool): True if UI app, False if backend
     - port (int): Port to run app
     - run_command (string): Required if is_ui is False

Example Repository Configuration
--------------------------------

Backend App (is_ui = False):
{
    "repo_name": "Aps",
    "branch": "main",
    "folder_name": "Aps",
    "is_ui": false,
    "port": 8000,
    "run_command": "uvicorn main.main:app --port 8005"
}

Frontend App (is_ui = True):
{
    "repo_name": "To-Do-List",
    "branch": "main",
    "folder_name": "To-Do-List",
    "is_ui": true,
    "port": 3001
}

Deployment Logic
----------------
- If `is_ui` is True:
  - Run `npm install` in the project directory.
  - Start the frontend using default scripts.

- If `is_ui` is False:
  - `run_command` is mandatory.
  - Execute backend app using the specified command.

Validation
----------
if not is_ui and not run_command:
    print("Error: 'run_command' is required when 'is_ui' is False.")
    return

Directory Structure After Deployment
------------------------------------
C:/deploy/
├── Aps/
│   └── ... (code and virtual env)
└── To-Do-List/
    └── node_modules/

Security Note
-------------
- Replace "ghp_xxxxxx" with a valid GitHub Personal Access Token.
- Never expose the token publicly.

autovix Configuration JSON - Documentation
==========================================

This JSON configuration is used to control how repositories are cloned, set up, and run by the autovix automation system.

Top-Level Structure:
--------------------
{
    "env_name": "string",          # Name of the environment/project group
    "git_data": {                  # GitHub authentication and organization info
        "username": "string",     # GitHub username
        "token": "string",        # GitHub Personal Access Token (PAT)
        "org_or_user": "string"   # GitHub organization or user
    },
    "base_path": "string",        # Base directory where all repos will be cloned
    "repositories": [             # List of repositories to deploy
        {
            "repo_name": "string",        # Name of the GitHub repository
            "branch": "string",           # Branch to clone
            "folder_name": "string",      # Folder to clone into
            "is_ui": true/false,          # True for frontend, False for backend
            "port": number,               # Port to run the app
            "run_command": "string"       # (Optional) Command to run the backend (required if is_ui is false)
        }
    ]
}

Example:
--------
{
    "env_name": "autovix",
    "git_data": {
        "username": "autovix_user",
        "token": "ghp_xxxxxx",
        "org_or_user": "autovix_user"
    },
    "base_path": "C:/deploy",
    "repositories": [
        {
            "repo_name": "autovix",
            "branch": "main",
            "folder_name": "autovix",
            "is_ui": false,
            "port": 8000,
            "run_command": "uvicorn main.main:app --port 8005"
        },
        {
            "repo_name": "To-Do-List",
            "branch": "main",
            "folder_name": "To-Do-List",
            "is_ui": true,
            "port": 3001
        }
    ]
}

Notes:
------
- If `is_ui` is false, `run_command` must be provided.
- If `is_ui` is true, the system will automatically run `npm install` and use the default frontend server.
- All cloned projects are stored in the directory specified by `base_path`.
"""


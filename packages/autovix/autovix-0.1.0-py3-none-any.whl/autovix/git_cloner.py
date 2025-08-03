

import subprocess
import os
from utils import UiDeployProcess, BackendDeployProcess
import time

class GitAutoCloner:
    def __init__(self):
        self.repo_entries = []

    def create_git_urls(self, json_data):
        self.repo_entries = []
        self.env_name = json_data.get("env_name", "default_env")
        git_data = json_data.get("git_data")
        base_path = json_data.get("base_path")
        repositories = json_data.get("repositories")

        if not git_data or not base_path or not repositories:
            print("Missing required fields: 'git_data', 'base_path', or 'repositories'")
            return

        username = git_data.get("username")
        token = git_data.get("token")
        org_or_user = git_data.get("org_or_user")

        if not username or not token or not org_or_user:
            print("'git_data' must include 'username', 'token', and 'org_or_user'")
            return

        for repo in repositories:
            repo_name = repo.get("repo_name")
            folder_name = repo.get("folder_name", "").strip() or repo_name
            if not repo_name:
                print(f" Skipping entry — 'repo_name' is required: {repo}")
                continue

            repo_url = f"https://{username}:{token}@github.com/{org_or_user}/{repo_name}.git"
            destination_path = self.generate_destination_folder(base_path, folder_name)
            branch = repo.get("branch", "main")
            is_ui = repo.get("is_ui", False)
            port = repo.get("port", 8000)

            self.repo_entries.append({
                "repo_url": repo_url,
                "destination_path": destination_path,
                "branch": branch,
                "is_ui": is_ui,
                "port": port,
                "repo_name": repo_name,
            })

    def generate_destination_folder(self, base_path, folder_name):
        return os.path.abspath(os.path.join(base_path, folder_name))

    def clone_repository(self, entry):
        try:
            print(f"\ Cloning '{entry['repo_url']}' into '{entry['destination_path']}'...")
            subprocess.run(
                ["git", "clone", "--branch", entry["branch"], entry["repo_url"], entry["destination_path"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            print(f" Successfully cloned: {entry['destination_path']}")
            return True
        except subprocess.CalledProcessError as e:
            print(f" Failed to clone {entry['repo_url']}")
            print(f"stderr: {e.stderr.strip()}")
            return False

    def deploy_all_projects(self, json_data):
        self.create_git_urls(json_data)
        time.sleep(1)
        ui_util = UiDeployProcess()
        backend_util = BackendDeployProcess()

        # Create Conda environment once for backend
        backend_env_created = False

        for entry in self.repo_entries:
            if not self.clone_repository(entry):
                time.sleep(3)
                continue  # skip on clone failure

            app_path = entry["destination_path"]
            port = entry["port"]

            if entry["is_ui"]:
                print(f"\ Setting up frontend: {entry['repo_name']}")
                ui_util.install_node_modules(app_path)
                ui_util.startup_frontend_applications(app_path, port)
            else:
                print(f"\ Setting up backend: {entry['repo_name']}")
                if not backend_env_created:
                    backend_util.create_conda_env(self.env_name)
                    backend_env_created = True
                backend_util.install_dependencies(self.env_name, app_path)

                # Auto-detect app_module (optional: you can make it a field)
                app_module = "main:app"  # default assumption
                backend_util.start_uvicorn_server(self.env_name, app_path,port, app_module )




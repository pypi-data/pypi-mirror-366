import subprocess
import os
import sys

class UiDeployProcess:
    def install_node_modules(self, application_path):
        command = f'cd /d {application_path} && npm install' if os.name == 'nt' else f'cd {application_path} && npm install'
        print(f"Running: {command}")
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Node modules installed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error during installation:", e)

    def startup_frontend_applications(self, application_path, port):
        try:
            if os.name == 'nt':
                # Opens a new command prompt window and starts the React app on given port
                command = f'start cmd /k "cd /d {application_path} && set PORT={port} && npm start"'
            else:
                # On Linux/macOS
                command = f'cd "{application_path}" && PORT={port} npm start'
            print(f"Executing: {command}")
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")

class BackendDeployProcess:
    def create_conda_env(self, env_name):
        try:
            print(f"Creating Conda environment: {env_name} with Python {3.12}...")
            subprocess.run(
                ["conda", "create", "--name", env_name, f"python=3.12", "-y"],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
            print(f"Successfully created Conda environment: {env_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while creating Conda environment: {e.stderr}")

    def install_dependencies(self, env_name, application_path):
        try:
            # Search for dependency file in app folder
            possible_files = ["dependencies.txt", "requirements.txt"]
            dep_file = None
            for f in possible_files:
                full_path = os.path.join(application_path, f)
                if os.path.exists(full_path):
                    dep_file = full_path
                    break
            if not dep_file:
                raise FileNotFoundError("No dependency file found in the application folder.")
            
            command = f'conda run -n {env_name} pip install -r "{dep_file}"'
            print(f"Installing dependencies using: {command}")
            subprocess.run(command, shell=True, check=True)
            print("Dependencies installed successfully.")

        except Exception as e:
            print("Error installing dependencies:", e)

    def start_uvicorn_server(self, env_name, application_path, port,app_module=None):
        """
        app_module: should be like 'main:app' (main.py file and app instance)
        """
        try:
            command = f'start cmd /k "cd /d {application_path} && conda activate {env_name} && uvicorn api.main:app --port {port}"'
            print(f"Starting backend server with command: {command}")
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print("Error starting backend server:", e)



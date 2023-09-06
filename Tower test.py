import os
from tower_cli.api import client
from tower_cli.conf import settings

# Set the Tower API credentials and URL
settings.TOWER_HOST = 'https://your-ansible-tower-url/'
settings.TOWER_USERNAME = 'your-username'
settings.TOWER_PASSWORD = 'your-password'
settings.TOWER_VERIFY_SSL = True  # Set to False if SSL certificate validation is not required

# Function to retrieve a list of YAML files associated with projects or templates
def get_yaml_files_associated_with_projects_or_templates():
    # Initialize Tower API client
    api = client()

    # Fetch all projects
    projects = api.projects.list()

    # Fetch all job templates
    job_templates = api.job_templates.list()

    # Initialize a list to store YAML file names
    yaml_files = []

    # Extract YAML file names from projects
    for project in projects:
        project_files = project.get('related', {}).get('unified_job_templates', [])
        for file in project_files:
            if file['type'] == 'project':
                yaml_files.append(file['name'])

    # Extract YAML file names from job templates
    for job_template in job_templates:
        extra_vars = job_template.get('extra_vars', '')
        if '.yaml' in extra_vars or '.yml' in extra_vars:
            yaml_files.append(job_template['name'])

    return yaml_files

if __name__ == "__main__":
    yaml_files = get_yaml_files_associated_with_projects_or_templates()

    if yaml_files:
        print("YAML files associated with projects or templates:")
        for file in yaml_files:
            print(file)
    else:
        print("No YAML files found associated with projects or templates.")

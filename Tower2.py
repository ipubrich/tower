import getpass
import requests
import urllib3

# Disable SSL warnings (only for development/testing)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ansible Tower API endpoint and credentials
tower_url = 'https://your-ansible-tower-url/'
username = input('Enter your Ansible Tower username: ')
password = getpass.getpass('Enter your Ansible Tower password: ')

# Function to retrieve a list of YAML files associated with projects or templates
def get_yaml_files_associated_with_projects_or_templates():
    # Create a session with authentication
    session = requests.Session()
    session.auth = (username, password)

    # Fetch all projects
    projects_url = f'{tower_url}/api/v2/projects/'
    response = session.get(projects_url, verify=False)

    if response.status_code != 200:
        print(f"Failed to fetch projects. Status code: {response.status_code}")
        return []

    projects = response.json()['results']

    # Fetch all job templates
    job_templates_url = f'{tower_url}/api/v2/job_templates/'
    response = session.get(job_templates_url, verify=False)

    if response.status_code != 200:
        print(f"Failed to fetch job templates. Status code: {response.status_code}")
        return []

    job_templates = response.json()['results']

    # Initialize a list to store YAML file names
    yaml_files = []

    # Extract YAML file names from projects
    for project in projects:
        project_files_url = f"{tower_url}/api/v2/projects/{project['id']}/unified_job_templates/"
        response = session.get(project_files_url, verify=False)
        if response.status_code == 200:
            project_files = response.json()
            for file in project_files['results']:
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

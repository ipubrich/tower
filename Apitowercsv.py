import getpass
import requests
import urllib3
import csv

# Disable SSL warnings (only for development/testing)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ansible Tower API endpoint and credentials
tower_url = 'https://your-ansible-tower-url/'
username = input('Enter your Ansible Tower username: ')
password = getpass.getpass('Enter your Ansible Tower password: ')

# Function to retrieve project details
def get_project_details(project):
    return {
        'Project Name': project['name'],
        'Project Stash URL': project['scm_url']
    }

# Function to retrieve template details
def get_template_details(template):
    extra_vars = template.get('extra_vars', '')
    return {
        'Template Name': template['name'],
        'YAML File Associated': extra_vars
    }

# Function to retrieve associations between projects and templates
def get_project_template_associations():
    associations = []

    # Create a session with authentication
    session = requests.Session()
    session.auth = (username, password)

    # Fetch all projects
    projects_url = f'{tower_url}/api/v2/projects/'
    response = session.get(projects_url, verify=False)

    if response.status_code != 200:
        print(f"Failed to fetch projects. Status code: {response.status_code}")
        return associations

    projects = response.json()['results']

    # Fetch all job templates
    job_templates_url = f'{tower_url}/api/v2/job_templates/'
    response = session.get(job_templates_url, verify=False)

    if response.status_code != 200:
        print(f"Failed to fetch job templates. Status code: {response.status_code}")
        return associations

    job_templates = response.json()['results']

    # Extract associations between projects and templates
    for project in projects:
        project_details = get_project_details(project)
        project_id = project['id']

        project_files_url = f"{tower_url}/api/v2/projects/{project_id}/unified_job_templates/"
        response = session.get(project_files_url, verify=False)
        if response.status_code == 200:
            project_files = response.json()
            for file in project_files['results']:
                if file['type'] == 'project':
                    template_id = file['id']
                    template = next((t for t in job_templates if t['id'] == template_id), None)
                    if template:
                        template_details = get_template_details(template)
                        association = {**project_details, **template_details}
                        associations.append(association)

    return associations

if __name__ == "__main__":
    associations = get_project_template_associations()

    if associations:
        # Create a CSV file and write header
        with open('ansible_associations.csv', 'w', newline='') as csvfile:
            fieldnames = ['Project Name', 'Project Stash URL', 'Template Name', 'YAML File Associated']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Write association data to the CSV
            for association in associations:
                writer.writerow(association)

        print("CSV file 'ansible_associations.csv' has been generated.")
    else:
        print("No associations found.")
  

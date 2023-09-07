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

# Function to fetch job templates with pagination
def fetch_job_templates_with_pagination():
    try:
        # Create a session with authentication
        session = requests.Session()
        session.auth = (username, password)

        # Initialize pagination variables
        page = 1
        page_size = 100  # Adjust the page size as needed
        job_templates = []

        while True:
            # Fetch job templates with pagination
            job_templates_url = f'{tower_url}/api/v2/job_templates/?page={page}&page_size={page_size}'
            response = session.get(job_templates_url, verify=False)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch job templates. Status code: {response.status_code}")

            templates_data = response.json()['results']

            if not templates_data:
                break

            job_templates.extend(templates_data)
            page += 1

        return job_templates
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

# Function to fetch project names based on project numbers
def fetch_project_names(project_numbers):
    try:
        # Create a session with authentication
        session = requests.Session()
        session.auth = (username, password)

        project_names = {}

        for project_number in project_numbers:
            # Fetch project details by project number
            project_url = f'{tower_url}/api/v2/projects/{project_number}/'
            response = session.get(project_url, verify=False)

            if response.status_code == 200:
                project_data = response.json()
                project_name = project_data.get('name', 'N/A')
                project_names[project_number] = project_name

        return project_names
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}

# Function to export data to CSV
def export_to_csv(job_templates, project_names):
    try:
        # Create a CSV file and write header
        with open('ansible_template_project.csv', 'w', newline='') as csvfile:
            fieldnames = ['Project Name', 'Project ID', 'Template Name', 'Template ID', 'Playbook Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Write job template data to the CSV
            for template in job_templates:
                template_id = template['id']
                project_id = template['project']
                template_name = template['name']
                playbook_name = template['job_type']

                # Get the project name from project_names dictionary
                project_name = project_names.get(project_id, 'N/A')

                writer.writerow({
                    'Project Name': project_name,
                    'Project ID': project_id,
                    'Template Name': template_name,
                    'Template ID': template_id,
                    'Playbook Name': playbook_name
                })

        print("CSV file 'ansible_template_project.csv' has been generated.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    job_templates = fetch_job_templates_with_pagination()

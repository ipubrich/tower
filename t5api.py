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

# Function to retrieve template details
def get_template_details(template, project_cache):
    # Get the project ID from the template data
    project_id = template.get('project', {}).get('id')

    # Use project_cache to lookup the project name by ID (making an additional API call if necessary)
    if project_id not in project_cache:
        project_name = lookup_project_name_by_id(project_id)
        project_cache[project_id] = project_name
    else:
        project_name = project_cache[project_id]

    return {
        'Template Name': template['name'],
        'Playbook Name': template['job_type'],
        'Project Number': project_id,
        'Project Name': project_name
    }

# Function to retrieve project name by ID
def lookup_project_name_by_id(project_id):
    try:
        # Create a session with authentication
        session = requests.Session()
        session.auth = (username, password)

        # Fetch project details by ID
        project_url = f'{tower_url}/api/v2/projects/{project_id}/'
        response = session.get(project_url, verify=False)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch project details. Status code: {response.status_code}")

        project_data = response.json()
        project_name = project_data.get('name', 'N/A')

        return project_name
    except Exception as e:
        print(f"Error: {str(e)}")
        return 'N/A'

# Function to retrieve job templates and export to CSV
def get_and_export_job_templates_to_csv():
    try:
        # Create a session with authentication
        session = requests.Session()
        session.auth = (username, password)

        # Initialize project cache
        project_cache = {}

        # Initialize pagination variables
        page = 1
        page_size = 100  # Adjust the page size as needed

        # Create a CSV file and write header
        with open('ansible_job_templates.csv', 'w', newline='') as csvfile:
            fieldnames = ['Template Name', 'Playbook Name', 'Project Number', 'Project Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            while True:
                # Fetch job templates with pagination
                job_templates_url = f'{tower_url}/api/v2/job_templates/?page={page}&page_size={page_size}'
                response = session.get(job_templates_url, verify=False)

                if response.status_code != 200:
                    raise Exception(f"Failed to fetch job templates. Status code: {response.status_code}")

                job_templates = response.json()['results']

                if not job_templates:
                    break

                # Write job template data to the CSV
                for template in job_templates:
                    template_details = get_template_details(template, project_cache)
                    writer.writerow(template_details)

                page += 1

        print("CSV file 'ansible_job_templates.csv' has been generated.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    get_and_export_job_templates_to_csv()

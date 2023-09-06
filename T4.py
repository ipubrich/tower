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
def get_template_details(template):
    return {
        'Template Name': template['name'],
        'Playbook Name': template['job_type'],
        'Project Name': template.get('project', {}).get('name', 'N/A')
    }

# Function to retrieve job templates and export to CSV
def get_and_export_job_templates_to_csv():
    try:
        # Create a session with authentication
        session = requests.Session()
        session.auth = (username, password)

        # Fetch all job templates
        job_templates_url = f'{tower_url}/api/v2/job_templates/'
        response = session.get(job_templates_url, verify=False)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch job templates. Status code: {response.status_code}")

        job_templates = response.json()['results']

        if not job_templates:
            print("No job templates found.")
            return

        # Create a CSV file and write header
        with open('ansible_job_templates.csv', 'w', newline='') as csvfile:
            fieldnames = ['Template Name', 'Playbook Name', 'Project Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Write job template data to the CSV
            for template in job_templates:
                template_details = get_template_details(template)
                writer.writerow(template_details)

        print("CSV file 'ansible_job_templates.csv' has been generated.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    get_and_export_job_templates_to_csv()
      

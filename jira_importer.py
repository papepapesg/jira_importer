#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
import yaml
from atlassian import Jira
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('jira_import.log')
    ]
)
logger = logging.getLogger(__name__)

class JiraImporter:
    """Class to handle Jira epic and story imports."""
    
    def __init__(self, config_file: str):
        """Initialize the JiraImporter with configuration."""
        self.config = self._load_config(config_file)
        self.jira = self._init_jira_client()

    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            sys.exit(1)

    def _init_jira_client(self) -> Jira:
        """Initialize Jira client with configuration."""
        try:
            jira_config = self.config.get('jira', {})
            url = f"https://{jira_config['url']}"
            logger.info(f"Connecting to Jira at: {url}")
            
            return Jira(
                url=url,
                username=jira_config['username'],
                password=jira_config['api_token']
            )
        except Exception as e:
            logger.error(f"Error initializing Jira client: {e}")
            sys.exit(1)

    def _load_stories(self, stories_file: str) -> Dict:
        """Load stories from JSON file."""
        try:
            with open(stories_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading stories file: {e}")
            sys.exit(1)

    def _create_epic(self, epic_data: Dict) -> Optional[str]:
        """Create an epic in Jira and return its key."""
        try:
            # Check for existing epic with same summary
            jql = f'project = {self.config["jira"]["project_key"]} AND issuetype = {self.config["jira"]["epic_type_id"]} AND summary ~ "{epic_data["summary"]}"'
            existing_epics = self.jira.jql(jql)
            
            if existing_epics.get('issues'):
                epic_key = existing_epics['issues'][0]['key']
                logger.info(f"Found existing epic: {epic_key}")
                return epic_key

            # Create new epic
            epic = {
                'project': {'key': self.config['jira']['project_key']},
                'summary': epic_data['summary'],
                'description': epic_data.get('description', ''),
                'issuetype': {'id': self.config['jira']['epic_type_id']}
            }
            
            response = self.jira.create_issue(fields=epic)
            epic_key = response['key']
            logger.info(f"Created epic: {epic_key}")
            return epic_key
            
        except Exception as e:
            logger.error(f"Error creating epic: {e}")
            return None

    def _create_story(self, story_data: Dict, epic_key: Optional[str] = None) -> bool:
        """Create a story in Jira and optionally link it to an epic."""
        try:
            # Check for existing story with same summary
            jql = f'project = {self.config["jira"]["project_key"]} AND issuetype = {self.config["jira"]["story_type_id"]} AND summary ~ "{story_data["summary"]}"'
            existing_stories = self.jira.jql(jql)
            
            if existing_stories.get('issues'):
                logger.info(f"Story already exists: {existing_stories['issues'][0]['key']}")
                return True

            # Create new story
            story = {
                'project': {'key': self.config['jira']['project_key']},
                'summary': story_data['summary'],
                'description': story_data.get('description', ''),
                'issuetype': {'id': self.config['jira']['story_type_id']}
            }
            
            # Add epic link if provided
            if epic_key:
                story['customfield_10014'] = epic_key  # Epic Link field
                
            response = self.jira.create_issue(fields=story)
            logger.info(f"Created story: {response['key']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating story: {e}")
            return False

    def import_stories(self, stories_file: str) -> None:
        """Import all epics and stories from the JSON file."""
        data = self._load_stories(stories_file)
        
        for epic_data in data.get('epics', []):
            epic_key = self._create_epic(epic_data)
            if epic_key:
                for story_data in epic_data.get('stories', []):
                    self._create_story(story_data, epic_key)

    def print_metadata(self):
        """Print all relevant Jira metadata for configuration."""
        try:
            # Get and print projects
            projects = self.jira.projects()
            print("\n=== Available Projects ===")
            print("Project Key\tName\tID")
            print("-" * 50)
            for project in projects:
                print(f"{project['key']}\t{project['name']}\t{project['id']}")

            # If project key is specified, get more details
            if 'project_key' in self.config.get('jira', {}):
                project_key = self.config['jira']['project_key']
                project = next((p for p in projects if p['key'] == project_key), None)
                
                if project:
                    # Get issue types for the project
                    print(f"\n=== Issue Types for Project {project_key} ===")
                    print("ID\tName\tSubtask")
                    print("-" * 50)
                    
                    # Get issue types using REST API directly
                    server_url = self.config['jira']['url']
                    if not server_url.startswith('http'):
                        server_url = f"https://{server_url}"
                    
                    issue_types_url = f"{server_url}/rest/api/2/issuetype"
                    response = self.jira._session.get(issue_types_url)
                    if response.status_code == 200:
                        issue_types = response.json()
                        for issue_type in issue_types:
                            print(f"{issue_type['id']}\t{issue_type['name']}\t{issue_type.get('subtask', False)}")
                    else:
                        logger.warning(f"Could not fetch issue types: {response.status_code} - {response.text}")

                    # Get and print fields
                    print("\n=== Available Fields ===")
                    print("ID\tName\tType")
                    print("-" * 50)
                    fields = self.jira.get_all_fields()
                    for field in fields:
                        field_schema = field.get('schema', {})
                        field_type = field_schema.get('type', 'N/A') if field_schema else 'N/A'
                        print(f"{field['id']}\t{field['name']}\t{field_type}")

        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            sys.exit(1)

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python jira_importer.py config.yaml [stories.json]")
        print("       python jira_importer.py config.yaml --metadata")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Import stories into Jira')
    parser.add_argument('config', help='Path to config YAML file')
    parser.add_argument('stories', nargs='?', help='Path to stories JSON file')
    parser.add_argument('--metadata', action='store_true', help='Print Jira metadata')
    
    args = parser.parse_args()
    
    importer = JiraImporter(args.config)
    
    if args.metadata:
        importer.print_metadata()
    elif args.stories:
        importer.import_stories(args.stories)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()

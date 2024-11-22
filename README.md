# Jira Story Import Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/atlassian-python-api.svg)](https://badge.fury.io/py/atlassian-python-api)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-no-red.svg)](https://github.com/papepapesg/jira_importer/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/papepapesg/jira_importer.svg)](https://github.com/papepapesg/jira_importer/issues/)

A Python-based tool for automating the import of epics and user stories into Jira projects.

## Features

- Import epics and stories from JSON files
- Prevent duplicate issues using smart detection
- Configurable issue types and fields
- Comprehensive logging
- Metadata inspection for easy configuration
- Support for multiple Jira projects

## Prerequisites

- Python 3.6+
- Jira account with API token
- Appropriate permissions in your Jira project

## Installation

1. Clone this repository:
```bash
git clone https://github.com/papepapesg/jira_importer.git
cd jira_importer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `config.yaml.example` to `config.yaml`:
```bash
cp config.yaml.example config.yaml
```

2. Edit `config.yaml` with your Jira details:
```yaml
jira:
  url: your-instance.atlassian.net
  username: your-email@example.com
  api_token: your-api-token
  project_key: YOUR_PROJECT
  epic_type_id: "10000"
  story_type_id: "10004"
```

To get your API token:
1. Log in to https://id.atlassian.com
2. Go to Security → Create and manage API tokens
3. Create a new token and copy it

## Usage

1. Prepare your JSON file with epics and stories (see `sample_stories.json` for format)

2. Get your Jira project's metadata (issue type IDs, etc.):
```bash
python jira_importer.py config.yaml --metadata
```

This will show you:
- All available projects
- Issue types and their IDs for your project
- Available fields and their types

3. Update your `config.yaml` with the correct issue type IDs from step 2

4. Run the import:
```bash
python jira_importer.py config.yaml your_stories.json
```

## JSON Format

Your stories file should follow this format:
```json
{
  "epics": [
    {
      "summary": "Epic Title",
      "description": "Epic Description",
      "stories": [
        {
          "summary": "Story Title",
          "description": "Story Description"
        }
      ]
    }
  ]
}
```

See `sample_stories.json` for a complete example.

## Error Handling

The script includes comprehensive error handling:
- Validates JSON format
- Checks for required fields
- Prevents duplicate issues
- Logs all operations and errors

## Logging

Logs are written to:
- Console (INFO level and above)
- `jira_import.log` (DEBUG level and above)

## Troubleshooting

1. **Duplicate Issues**: The script checks for existing issues with the same summary. If found, it skips creation.

2. **Authentication Errors**: 
   - Verify your API token
   - Check your username and Jira URL
   - Ensure you have appropriate permissions

3. **Issue Type Errors**:
   - Run the `--metadata` command to get correct issue type IDs
   - Update config.yaml with the correct IDs

## Security Notes

- Store your API token securely
- Don't commit config.yaml with credentials
- Use environment variables for sensitive data (future feature)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please use the issue tracker.

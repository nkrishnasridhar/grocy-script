# Data Collection Script

This script monitors resource utilization (CPU and RAM) of a PHP process while making requests to a Grocy API.

## Prerequisites

- Python 3.x
- pip package manager

## Installation

1. Clone this repository
2. Install required Python packages:
   ```
   pip install requests psutil
   ```

## Configuration

Create a `.env` file in the project root with your API key:
```
API_KEY=your_grocy_api_key_here
```

## Usage

Run the script:
```
python resource_utilization_script.py
```

The script will:
- Find a PHP process running on localhost:8000
- Make 100 requests to various Grocy API endpoints
- Monitor CPU and RAM usage during each request
- Display peak and average resource utilization

## Output

The script prints:
- Per-request CPU usage, RAM usage, and HTTP status code
- Final statistics: peak and average CPU/RAM across all requests
# Data Collection Script

This script monitors resource utilization (CPU and RAM) of the locally running Grocy PHP process while making requests to a Grocy API.

## How to run

1. Go to the [Grocy GitHub repo](https://github.com/grocy/grocy) and download the latest release
2. Unzip and run command `php –S localhost:8000 –t public` in the project root
3. In a new terminal, run the script
```
python resource_utilization_script.py > output.txt
```

The script will:
- Find a PHP process running on localhost:8000
- Make 100 requests to various Grocy API endpoints
- Monitor CPU and RAM usage during each request
- Display peak and average resource utilization

## Output

The script outputs:
- Per-request CPU usage, RAM usage, and HTTP status code
- Final statistics: peak and average CPU/RAM across all requests
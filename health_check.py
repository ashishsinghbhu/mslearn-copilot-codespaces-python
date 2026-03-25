import requests
import sys


def main():
    url = "http://localhost:8000/health"
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.ConnectionError:
        print(f"Error: Could not connect to {url}")
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Request to {url} timed out")
        sys.exit(1)


if __name__ == "__main__":
    main()

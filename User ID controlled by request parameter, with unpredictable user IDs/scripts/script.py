import requests
import sys
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {http : "127.0.0.1:8080", https : "127.0.0.1:8080"}







def main():
    if len(sys.argv) != 2:
        print("(+)Usage: %s <url>: " % sys.argv[0])
        print("(+)Example: %s www.example.com: " % sys.argv[0])
        sys.exit(-1)

    url = sys.argv[1]
    



if __name__ == '__main__':
        main()
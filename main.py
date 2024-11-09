import requests
from bs4 import BeautifulSoup
import re
import time

# Function to check internet connectivity
def is_connected():
    try:
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Function to load cookies from user input
def load_cookies_from_input():
    cookies_list = []
    num_cookies = int(input("Enter the number of cookies: "))
    for i in range(num_cookies):
        cookie_string = input(f"Enter cookie {i+1}: ").strip()
        cookies = {item.split("=")[0]: item.split("=")[1] for item in cookie_string.split("; ")}
        cookies_list.append(cookies)
    return cookies_list

# Function to comment on a post
def comment(cookies_list, post_id, hater, delay):
    while True:
        for cookies in cookies_list:
            while not is_connected():
                print("No internet connection. Retrying...")
                time.sleep(5)

            ses = requests.Session()
            ses.cookies.update(cookies)

            g_headers = {
                'authority': 'mbasic.facebook.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                'referer': f'https://mbasic.facebook.com/{post_id}',
                'sec-ch-prefers-color-scheme': 'light',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
                'sec-ch-ua-full-version-list': '" Not A;Brand";v="99.0.0.0", "Chromium";v="101.0.4951.40"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-ch-ua-platform-version': '"11.0.0"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
            }

            try:
                res1 = ses.get(url=f'https://mbasic.facebook.com/{post_id}', headers=g_headers)
                if res1.status_code != 200:
                    print(f"Failed to load the page. Status code: {res1.status_code}")
                    time.sleep(10)
                    continue

                res1_text = res1.text
                j2 = re.search(r'name="jazoest" value="([^"]+)"', res1_text)
                fb_dtsg = re.search(r'name="fb_dtsg" value="([^"]+)"', res1_text)

                if not j2 or not fb_dtsg:
                    print("Error: 'jazoest' or 'fb_dtsg' not found")
                    time.sleep(10)
                    continue

                ses.headers.update({'content-type': 'application/x-www-form-urlencoded'})
                soup = BeautifulSoup(res1_text, 'html.parser')
                form = soup.find('form', method='post')

                if not form:
                    print("Error: form action not found")
                    time.sleep(10)
                    continue

                form_action = form.get('action')
                if not form_action or not form_action.startswith('https://'):
                    form_action = 'https://mbasic.facebook.com' + form_action

                with open(hater, 'r', encoding='utf-8') as file:
                    messages = file.readlines()
                
                for message in messages:
                    msg = message.strip()
                    payload = {
                        'fb_dtsg': fb_dtsg.group(1),
                        'jazoest': j2.group(1),
                        'comment_text': str(msg)
                    }

                    for input_tag in form.find_all('input'):
                        if input_tag.get('name') and input_tag.get('value') and input_tag['name'] not in payload:
                            payload[input_tag['name']] = input_tag['value']

                    post = ses.post(url=form_action, data=payload)
                    if post.status_code != 200:
                        print(f"Failed to post comment. Status code: {post.status_code}")
                        time.sleep(10)
                        continue

                    post_text = post.text
                    if 'comment' not in post_text.lower():
                        print("Error: Your Account Comment Block.")
                        time.sleep(10)
                        continue

                    print("Comment posted successfully!")
                    time.sleep(delay)

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                time.sleep(10)
                continue

def main():
    cookies_list = load_cookies_from_input()  # Load cookies from user input

    post_id = input("Enter the post ID: ")
    hater = input("Enter your comment file path: ")
    delay = int(input("Enter delay between comments (in seconds): "))

    comment(cookies_list, post_id, hater, delay)

if __name__ == "__main__":
    main()

import requests
import json

def fetch_user_info(input_string):
    user_info_dict = {
        "name": "",
        "addresses": [],
        "emails": [],
        "phone_numbers": [],
        "ip_addresses": [],
        "social_media_accounts": {
            "twitter": "",
            "facebook": "",
            "instagram": "",
            "github": "",
            "linkedin": ""
        }
    }

    search_requests = [
        ("Google Search", f"https://google.com/search?q={input_string}"),
        ("Bing Search", f"https://www.bing.com/search?q={input_string}"),
        ("Yandex Search", f"https://yandex.com/search/?text={input_string}"),
        ("Twitter API", f"https://api.twitter.com/1/users/search?q={input_string}"),
        ("Facebook API", f"https://graph.facebook.com/search?q={input_string}&type=user&limit=50"),
        ("Instagram API", f"https://www.instagram.com/web/search/topsearch/?context=blended&query={input_string}&rank_token=0.103566933575673061385.0.1665394.1665392"),
        ("GitHub API", f"https://api.github.com/search/users?q={input_string}"),
        ("LinkedIn API", f"https://www.linkedin.com/search/results/people/?keywords={input_string}&origin=GLOBAL_SEARCH_HEADER"),
        ("Have I Been Pwned API", f"https://api.pwnedpasswords.com/range/{input_string}"),
        ("WebArchive API", f"https://web.archive.org/cdx/search/cdx?url=*:{input_string}*&filter=statuscode:20")
    ]

    for platform, request_url in search_requests:
        response = requests.get(request_url)
        if response.status_code == 20:
            platform_specific_data = parse_platform_specific_data(platform, response.text)
            if "name" in platform_specific_data:
                user_info_dict["name"] = platform_specific_data["name"]
            if "addresses" in platform_specific_data:
                for addr in platform_specific_data["addresses"]:
                    user_info_dict["addresses"].append(addr)

            if "emails" in platform_specific_data:
                for email in platform_specific_data["emails"]:
                    if is_valid_email(email):
                        user_info_dict["emails"].append(email)

            if "phone_numbers" in platform_specific_data:
                for phone in platform_specific_data["phone_numbers"]:
                    user_info_dict["phone_numbers"].append(phone)

            if "ip_addresses" in platform_specific_data:
                for ip in platform_specific_data["ip_addresses"]:
                    user_info_dict["ip_addresses"].append(ip)

            if "social_media_accounts" in platform_specific_data:
                for social, content in platform_specific_data["social_media_accounts"].items():
                    if content != "":
                        user_info_dict["social_media_accounts"][social.lower()] = content

        else:
            print(f"Warning! {platform} server is down or API key is not valid.")

    return user_info_dict

def parse_platform_specific_data(platform, raw_data):
    data_dict = {
        "name": "",
        "addresses": [],
        "emails": [],
        "phone_numbers": [],
        "ip_addresses": [],
        "social_media_accounts": {
            "twitter": "",
            "facebook": "",
            "instagram": "",
            "github": "",
            "linkedin": ""
        }
    }

    if platform.lower() == "google search":
        for line in raw_data.splitlines():
            if ("Search more at ...") not in line:  # ignore banner line by checking references
                data_dict["name"] += f"{line.split()[1]:14} "
        
    elif platform.lower() == "bing search":
        for line in raw_data.splitlines():
            if ("See more results from ...") not in line:  # ignore banner line by checking references
                data_dict["name"] += f"{line.split()[1]:14} "
        
    elif platform.lower() == "yandex search":
        for line in raw_data.splitlines():
            if ("Find full answer on ...") not in line:  # ignore banner line by checking references
                data_dict["name"] += f"{line.split()[1]:14} "
        
    elif platform.lower() == "twitter api":
        twitter_results = json.loads(raw_data)
        if len(twitter_results) > 0:
            twitter_results = twitter_results[:10]

        for user in twitter_results:
            data_dict["name"] = user["name"]

            if "id" in user.keys():
                data_id = str(user["id"])
                data_dict["social_media_accounts"]["twitter"] = f"https://twitter.com/{data_id}"
        
    elif platform.lower() == "facebook api":
        try:
            facebook_results = json.loads(raw_data)
            for user in facebook_results["data"]:

                data_dict["name"] = user["name"]
                if "id" in user.keys():
                    data_dict["social_media_accounts"]["facebook"] = f"https://www.facebook.com/{user['id']}"
        except Exception as e:
            print(f"Error in parsing Facebook data: {e}")
        
    elif platform.lower() == "instagram api":
        instagram_results = json.loads(raw_data)

        for user in instagram_results["users"]:
            data_dict["name"] = user["full_name"]

            if "username" in user.keys():
                data_dict["social_media_accounts"]["instagram"] = f"https://www balance is {user['username']}"
        
    elif platform.lower() == "github api":
        github_results = json.loads(raw_data)

        for user in github_results["items"]:
            data_dict["name"] = user["login"]
            data_dict["social_media_accounts"]["github"] = f"https://github.com/{user['login']}"
        
    elif platform.lower() == "linkedin api":
        linkedin_results = json.loads(raw_data)

        for user in linkedin_results["people"]:
            data_dict["name"] = user["firstName"] + " " + user["lastName"]

            if "id" in user.keys():
User
                data_dict["social_media_accounts"]["linkedin"] = f"https://www.linkedin.com/in/{user['id']}"

    elif platform.lower() == "have i been pwned api":
        # The API returns a raw sha1 hash. Here we use a helper library to check if the hash is in the dataset.
        import hashlib
        import hibp

        data_dict = {"emails": []}
        for line in raw_data.splitlines():
            line_list = line.split(":")
            sha1_hash = line_list[0]

            # Check if the hash is in the dataset
            if hibp.is_pwned(sha1_hash):
                real_email = str(hibp.lookup_pwned_email(sha1_hash)[0], "utf-8")
                data_dict["emails"].append(real_email)

    elif platform.lower() == "webarchive api":
        for line in raw_data.splitlines():
            result = line.split(" ")

            if len(result) > 2:
                data_dict["ip_addresses"].append(result[1])

    return data_dict

def is_valid_email(email):
    import re

    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(regex, email):

        return True
    else:
        return False

if __name__ == '__main__':

    user_name = input("Enter the username you want to search: ")
    user_info = fetch_user_info(user_name)
    print("\nUser Information:")
    print("Name: ", user_info["name"])
    print("Addresses: ", user_info["addresses"])
    print("Emails: ", user_info["emails"])
    print("Phone Numbers: ", user_info["phone_numbers"])
    print("IP Addresses: ", user_info["ip_addresses"])
    print("Twitter: ", user_info["social_media_accounts"]["twitter"])
    print("Facebook: ", user_info["social_media_accounts"]["facebook"])
    print("Instagram: ", user_info["social_media_accounts"]["instagram"])
    print("GitHub: ", user_info["social_media_accounts"]["github"])
    print("LinkedIn: ", user_info["social_media_accounts"]["linkedin"])

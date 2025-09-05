import json
import re
import requests
from datetime import datetime
URL = "mts-prism.com"
PORT = 8082

# Please do NOT share this information anywhere, unless you want your team to be cooked.
TEAM_API_CODE = "6598d4de054fbbf9268bd461c2b446ca"


# @cyrus or @myguysai on Discord if you need an API key


def send_get_request(path):
    """
    Sends a HTTP GET request to the server.
    Returns:
        (success?, error or message)
    """
    headers = {"X-API-Code": TEAM_API_CODE}
    response = requests.get(f"http://{URL}:{PORT}/{path}", headers=headers)

    # Check whether there was an error sent from the server.
    # 200 is the HTTP Success status code, so we do not expect any
    # other response code.
    if response.status_code != 200:
        return (
            False,
            f"Error - something went wrong when requesting [CODE: {response.status_code}]: {response.text}",
        )
    return True, response.text


def send_post_request(path, data=None):
    """
    Sends a HTTP POST request to the server.
    Pass in the POST data to data, to send some message.
    Returns:
         (success?, error or message)
    """
    headers = {"X-API-Code": TEAM_API_CODE, "Content-Type": "application/json"}

    # Convert the data from python dictionary to JSON string,
    # which is the expected format to be passed
    data = json.dumps(data)
    response = requests.post(f"http://{URL}:{PORT}/{path}", data=data, headers=headers)

    # Check whether there was an error sent from the server.
    # 200 is the HTTP Success status code, so we do not expect any
    # other response code.
    if response.status_code != 200:
        return (
            False,
            f"Error - something went wrong when requesting [CODE: {response.status_code}]: {response.text}",
        )
    return True, response.text


def get_context():
    """
    Query the challenge server to request for a client to design a portfolio for.
    Returns:
        (success?, error or message)
    """
    return send_get_request("/request")


def get_my_current_information():
    """
    Query your team information.
    Returns:
        (success?, error or message)
    """
    return send_get_request("/info")


#################


def normalize_date(date_str):
    try:
        # Try standard YYYY-MM-DD format first
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Remove ordinal suffixes: st, nd, rd, th
    date_str_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

    try:
        # Try parsing cleaned natural language format
        return datetime.strptime(date_str_clean, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Unsupported date format: {date_str}")


def context_to_tuple(context):

    context_dict = json.loads(context)
    message = context_dict.get("message", "")
    # Extract name (first name + last name)
    name_match = re.match(r"([A-Z][a-z]+ [A-Z][a-z]+)", message)
    name = name_match.group(1) if name_match else ""

    # Extract age
    age_match = re.search(r"(\d+)(?:-?\s*)years?(?:-?\s*)old", message)
    age = int(age_match.group(1)) if age_match else None

    # Extract budget
    budget_match = re.search(r"budget of \$([\d,]+)", message)
    budget = int(budget_match.group(1).replace(",", "")) if budget_match else None

    # Extract investment dates
    pattern = r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}(?:st|nd|rd|th)?,\s\d{4})|(\d{4}-\d{2}-\d{2})"

    matches = re.findall(pattern, message)

    # Flatten and filter out empty strings
    dates = [date for tup in matches for date in tup if date]

    start_date = dates[0] if len(dates) > 0 else None
    end_date = dates[1] if len(dates) > 1 else None
    start_date = normalize_date(start_date)
    end_date = normalize_date(end_date)

    # Gender (optional, we'll use 'Unknown' here for simplicity)

    gender_match = re.search(r"\b(he|she|him|her)\b", message, re.IGNORECASE)

    if gender_match:
        pronoun = gender_match.group(0).lower()
        if pronoun in ["he", "him"]:
            gender = "male"
        elif pronoun in ["she", "her"]:
            gender = "female"
    else:
        gender = "Unknown"


    # this extracts salary
    sal_match = re.search(r"(?i)(?:salary|income|pay|wage)[^\d]*(\d+)", message, re.IGNORECASE)
    if sal_match:
        salary = sal_match.group(1)
    else:
        salary = None
    result = (name, age, gender, budget, salary, start_date, end_date)
    print("Extracted tuple:", result)
    return result


##########


# def send_portfolio(weighted_stocks):
#     """
#     Send portfolio stocks to the server for evaluation.
#     Returns:
#         (success?, error or megssage)
#     """
#     data = [
#         {"ticker": weighted_stock[0], "quantity": weighted_stock[1]}
#         for weighted_stock in weighted_stocks
#     ]
#     return send_post_request("/submit", data=data)

success, information = get_my_current_information()
if not success:
    print(f"Error: {information}")
print(f"Team information: ", information)

success, context = get_context()
if not success:
    print(f"Error: {context}")
print(f"Context provided: ", context)
context_to_tuple(context)
# Maybe do something with the context to generate this?
portfolio = [("AAPL", 1), ("MSFT", 1), ("NVDA", 1), ("PFE", 1)]

success, response = send_post_request("/submit", portfolio)

if not success:
    print(f"Error: {response}")
print(f"Evaluation response: ", response)


# function tuple containing from context age, gender, budget, start, salary
#  Extracted tuple: ('Joe Lee', 53, 'Male', 5856, datetime.date(2010, 8, 14), datetime.date(2011, 6, 21), None)
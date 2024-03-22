import requests

def send_post_request(data_type: str) -> dict:
    """
    Sends a POST request to the workato assistant function endpoint with specified data.

    :param data_type: The value to be sent in the request body under the key 'type'.
    :return: The JSON response as a dictionary.
    """
    url = 'https://apim.workato.com/jayc0/workato_assistant_function'
    headers = {
        'API-TOKEN': 'af1d16385d51a386e715e3867b747a928c048bd3b9c7f03f5bc61aa606368e03',
        'Content-Type': 'application/json'
    }
    data = {'type': data_type}
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Example usage
# response = send_post_request('failed')
# print(response)

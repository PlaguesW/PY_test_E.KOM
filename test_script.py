import requests

def test_get_form(url, form_data):
    response = requests.post(url, data=form_data)
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Response (status {response.status_code}): {response.json()}")

if __name__ == "__main__":
    url = "http://127.0.0.1:8080/get_form"

    # Test request for "MyForm"
    form_data_1 = {
        "user_name": "Ivan Ivanov",
        "lead_email": "ivan@example.com",
        "order_date": "2024.12.01"
    }
    print("Test 1: Matching 'MyForm'")
    test_get_form(url, form_data_1)
    print()

    # Test request for "Order Form"
    form_data_2 = {
        "contact_email": "contact@info.fr",
        "contact_phone": "+7 123 456 78 90"
    }
    print("Test 2: Matching 'Order Form'")
    test_get_form(url, form_data_2)
    print()

    # Test request with invalid data
    form_data_3 = {
        "some_field": "some_value",
        "another_field": "2021-11-31"
    }
    print("Test 3: No matching template")
    test_get_form(url, form_data_3)
    print()

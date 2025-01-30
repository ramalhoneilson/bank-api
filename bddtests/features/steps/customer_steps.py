# environment.py
from behave import given, when, then
from fastapi.testclient import TestClient
from api.main import api
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def before_all(context):
    """Initialize FastAPI test client before all tests"""
    context.client = TestClient(api)


@given('I provide valid customer data')
def step_valid_customer_data(context):
    context.customer_data = {
        "customer_name": "John Doe"
    }
    logger.debug(f"Valid customer data: {context.customer_data}")


@given('I provide invalid customer data')
def step_invalid_customer_data(context):
    context.customer_data = {
        "customer_name": ""
    }
    logger.debug(f"Invalid customer data: {context.customer_data}")


@when('I send a POST request to "{endpoint}" with the customer data')
def step_send_post_request(context, endpoint):
    logger.debug(f"Sending POST request to {endpoint} with data: {context.customer_data}")
    context.response = context.client.post(
        endpoint,
        json=context.customer_data
    )
    logger.debug(f"Response status: {context.response.status_code}")
    try:
        response_body = context.response.json()
        logger.debug(f"Response body: {response_body}")
    except Exception as e:
        logger.debug(f"Could not parse response body: {e}")

# Note: This step is redundant since it's the same as the above step
# Remove this step and update your feature file to use just one step
# @when('I send a POST request to "{endpoint}" with the invalid customer data')
# def step_send_invalid_post_request(context, endpoint):
#     ...


@then('the response status code should be {status_code:d}')
def step_check_status_code(context, status_code):
    response_body = context.response.json() if context.response.content else "No response body"
    assert context.response.status_code == int(status_code), \
        f"Expected status code {status_code} but got {context.response.status_code}. Response body: {response_body}"


@then('the response should contain the newly created customer details')
def step_check_customer_details(context):
    response_data = context.response.json()
    assert "id" in response_data, "Response should contain customer ID"
    assert "customer_name" in response_data, "Response should contain customer_name"
    assert response_data["customer_name"] == context.customer_data["customer_name"], \
        "Response customer_name should match input customer_name"


@then('the response should contain an error message')
def step_check_error_message(context):
    response_data = context.response.json()
    logger.debug(f"Error response: {response_data}")
    assert "detail" in response_data, "Response should contain error detail"
    assert isinstance(response_data["detail"], str), "Error detail should be a string"
    assert len(response_data["detail"]) > 0, "Error detail should not be empty"

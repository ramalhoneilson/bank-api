import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from api.main import app
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

scenarios('../features/create_customer.feature')


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def context():
    class Context:
        pass
    return Context()


@given('I provide valid customer data')
def valid_customer_data(context):
    context.customer_data = {
        "customer_name": "John Doe"
    }
    logger.debug(f"Valid customer data: {context.customer_data}")


@given('I provide invalid customer data')
def invalid_customer_data(context):
    context.customer_data = {
        "customer_name": ""
    }
    logger.debug(f"Invalid customer data: {context.customer_data}")


@when(parsers.parse('I send a POST request to "{endpoint}" with the customer data'))
def send_post_request(client, context, endpoint):
    logger.debug(f"Sending POST request to {endpoint} with data: {context.customer_data}")
    context.response = client.post(
        endpoint,
        json=context.customer_data
    )
    logger.debug(f"Response status: {context.response.status_code}")
    try:
        response_body = context.response.json()
        logger.debug(f"Response body: {response_body}")
    except Exception as e:
        logger.debug(f"Could not parse response body: {e}")


@when(parsers.parse('I send a POST request to "{endpoint}" with the invalid customer data'))
def send_post_request(client, context, endpoint):
    logger.debug(f"Sending POST request to {endpoint} invalid with data: {context.customer_data}")
    context.response = client.post(
        endpoint,
        json=context.customer_data
    )
    logger.debug(f"Response status: {context.response.status_code}")
    try:
        response_body = context.response.json()
        logger.debug(f"Response body: {response_body}")
    except Exception as e:
        logger.debug(f"Could not parse response body: {e}")

@then(parsers.parse('the response status code should be {status_code:d}'))
def check_status_code(context, status_code):
    response_body = context.response.json() if context.response.content else "No response body"
    assert context.response.status_code == status_code, \
        f"Expected status code {status_code} but got {context.response.status_code}. Response body: {response_body}"


@then('the response should contain the newly created customer details')
def check_customer_details(context):
    response_data = context.response.json()
    assert "id" in response_data, "Response should contain customer ID"
    assert "customer_name" in response_data, "Response should contain customer_name"
    assert response_data["customer_name"] == context.customer_data["customer_name"], \
        "Response customer_name should match input customer_name"


@then('the response should contain an error message')
def check_error_message(context):
    response_data = context.response.json()
    logger.debug(f"Error response: {response_data}")
    assert "detail" in response_data, "Response should contain error detail"
    assert isinstance(response_data["detail"], str), "Error detail should be a string"
    assert len(response_data["detail"]) > 0, "Error detail should not be empty"

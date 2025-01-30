from behave import given, when, then
from fastapi.testclient import TestClient
import logging

logger = logging.getLogger(__name__)


@given('I provide valid administrative entity data')
def step_valid_entity_data(context):
    context.entity_data = {
        "tax_id": "123456789",
        "corporate_name": "Test Corporation"
    }
    logger.debug(f"Valid entity data: {context.entity_data}")


@given('I provide invalid administrative entity data')
def step_invalid_entity_data(context):
    context.entity_data = {
        "tax_id": "",
        "corporate_name": ""
    }
    logger.debug(f"Invalid entity data: {context.entity_data}")


@given('there are existing administrative entities')
def step_existing_entities(context):
    test_data = {
        "tax_id": "123456789",
        "corporate_name": "Test Corp"
    }
    response = context.client.post("/api/v1/administrative_entity", json=test_data)
    assert response.status_code == 200
    context.test_entity = response.json()


@given('there is an existing administrative entity with id "{entity_id}"')
def step_existing_entity(context, entity_id):
    if not hasattr(context, 'test_entity'):
        test_data = {
            "tax_id": "123456789",
            "corporate_name": "Test Corp"
        }
        response = context.client.post("/api/v1/administrative_entity", json=test_data)
        assert response.status_code == 200
        context.test_entity = response.json()
    context.entity_id = entity_id


@given('there is no administrative entity with id "{entity_id}"')
def step_non_existent_entity(context, entity_id):
    context.entity_id = entity_id


@when('I send a POST request to "{endpoint}" with the entity data')
def step_send_post_request(context, endpoint):
    logger.debug(f"Sending POST request to {endpoint} with data: {context.entity_data}")
    context.response = context.client.post(endpoint, json=context.entity_data)
    log_response(context.response)


@when('I send a POST request to "{endpoint}" with the invalid entity data')
def step_send_invalid_post_request(context, endpoint):
    logger.debug(f"Sending POST request to {endpoint} with invalid data: {context.entity_data}")
    context.response = context.client.post(endpoint, json=context.entity_data)
    log_response(context.response)


def log_response(response):
    logger.debug(f"Response status: {response.status_code}")
    try:
        response_body = response.json()
        logger.debug(f"Response body: {response_body}")
    except Exception as e:
        logger.debug(f"Could not parse response body: {e}")


@then('the response status code should be {status_code:d}')
def step_check_status_code(context, status_code):
    response_body = context.response.json() if context.response.content else "No response body"
    assert context.response.status_code == int(status_code), \
        f"Expected status code {status_code} but got {context.response.status_code}. Response body: {response_body}"


@then('the response should contain the created entity details')
def step_check_entity_details(context):
    response_data = context.response.json()
    assert "tax_id" in response_data, "Response should contain tax_id"
    assert "corporate_name" in response_data, "Response should contain corporate_name"
    assert "id" in response_data, "Response should contain id"
    assert response_data["tax_id"] == context.entity_data["tax_id"], \
        "Response tax_id should match input tax_id"
    assert response_data["corporate_name"] == context.entity_data["corporate_name"], \
        "Response corporate_name should match input corporate_name"


@then('the response should contain a list of entities')
def step_check_entity_list(context):
    response_data = context.response.json()
    assert isinstance(response_data, list), "Response should be a list"
    if len(response_data) > 0:
        assert "id" in response_data[0], "Entity should contain id"
        assert "tax_id" in response_data[0], "Entity should contain tax_id"
        assert "corporate_name" in response_data[0], "Entity should contain corporate_name"


@then('the response should contain the entity details')
def step_check_specific_entity_details(context):
    response_data = context.response.json()
    assert "tax_id" in response_data, "Response should contain tax_id"


@then('the response should contain an administrative entity error message')
def step_check_entity_error_message(context):
    response_data = context.response.json()
    logger.debug(f"Error response: {response_data}")
    assert "detail" in response_data, "Response should contain error detail"
    assert isinstance(response_data["detail"], str), "Error detail should be a string"
    assert len(response_data["detail"]) > 0, "Error detail should not be empty"

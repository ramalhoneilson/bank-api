from behave import when
import logging

logger = logging.getLogger(__name__)


@when('I send a GET request to "{endpoint}"')
def step_send_get_request(context, endpoint):
    """
    Generic step for sending GET requests.
    Handles both static endpoints and those with parameters.
    """
    logger.debug(f"Sending GET request to {endpoint}")
    context.response = context.client.get(endpoint)
    try:
        response_body = context.response.json()
        logger.debug(f"Response body: {response_body}")
    except Exception as e:
        logger.debug(f"Could not parse response body: {e}")

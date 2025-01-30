Feature: Administrative Entity Management
    As a system user
    I want to manage administrative entities
    So that I can maintain corporate information in the system

    Scenario: Successfully create a new administrative entity
        Given I provide valid administrative entity data
        When I send a POST request to "/api/v1/administrative_entity" with the entity data
        Then the response status code should be 200
        And the response should contain the created entity details

    Scenario: Fail to create an administrative entity with invalid data
        Given I provide invalid administrative entity data
        When I send a POST request to "/api/v1/administrative_entity" with the invalid entity data
        Then the response status code should be 400
        And the response should contain an administrative entity error message

    Scenario: Successfully retrieve all administrative entities
        Given there are existing administrative entities
        When I send a GET request to "/api/v1/administrative-entities"
        Then the response status code should be 200
        And the response should contain a list of entities

    Scenario: Successfully retrieve a specific administrative entity
        Given there is an existing administrative entity with id "1"
        When I send a GET request to "/api/v1/administrative_entity/1"
        Then the response status code should be 200
        And the response should contain the entity details

    Scenario: Fail to retrieve a non-existent administrative entity
        Given there is no administrative entity with id "999"
        When I send a GET request to "/api/v1/administrative_entities/999"
        Then the response status code should be 404
        And the response should contain an administrative entity error message

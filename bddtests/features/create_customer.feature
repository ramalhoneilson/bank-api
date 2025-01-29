Feature: Create a New Customer
    As a bank employee
    I want to create a new customer
    So that the customer can use the bank's services

    Scenario: Successfully create a new customer
        Given I provide valid customer data
        When I send a POST request to "/api/v1/customers" with the customer data
        Then the response status code should be 200
        And the response should contain the newly created customer details
        
    Scenario: Fail to create a customer with the invalid customer data
        Given I provide invalid customer data
        When I send a POST request to "/api/v1/customers" with the invalid customer data
        Then the response status code should be 400
        And the response should contain an error message
Feature: Transaction Management

    Scenario: Deposit Funds Successfully
        Given I have a user with an account balance of 100
        And I have cash holding account with balance of 10000
        When I make a deposit with amount "50"
        Then the response status code should be 200
        And the response should contain the deposit transaction details
        And the user account balance should be 150
        And the cash holding account balance should be 9950

    # Scenario: Deposit Funds - Account Not Found
    #     Given I have cash holding account with balance of 10000
    #     When I make a deposit with amount "50"
    #     Then the response status code should be 404
    #     And the response should contain an "Account not found" error message

    # Scenario: Withdraw Funds Successfully
    #     Given I have a user with an account balance of 100
    #     When I make a withdraw with amount "50"
    #     Then the response status code should be 200
    #     And the response should contain the withdrawal transaction details
    #     And the user account balance should be 50

    # Scenario: Withdraw Funds - Insufficient Funds
    #     Given I have a user with an account balance of 100
    #     When I make a withdraw with amount "150"
    #     Then the response status code should be 400
    #     And the response should contain an "Insufficient funds" error message

    # Scenario: Withdraw Funds - Account Not Found
    #     Given I have a user with an account balance of 100
    #     When I make a withdraw with amount "50"
    #     Then the response status code should be 404
    #     And the response should contain an "Account not found" error message

    # Scenario: Transfer Funds Successfully
    #     Given I have a source account with a balance of 100 and a destination account with balance of 50
    #     When I make a transfer with amount "50", source_account_id "1", and destination_account_id "2"
    #     Then the response status code should be 200
    #     And the response should contain the transfer transaction details
    #     And the user account balance should be 50
    #     And the second user account balance should be 100

    # Scenario: Transfer Funds - Insufficient Funds
    #     Given I have a source account with a balance of 100 and a destination account with balance of 50
    #     When I make a transfer with amount "150", source_account_id "1", and destination_account_id "2"
    #     Then the response status code should be 400
    #     And the response should contain an "Insufficient funds" error message

    # Scenario: Transfer Funds - Account Not Found
    #     Given I have a source account with a balance of 100 and a destination account with balance of 50
    #     When I make a transfer with amount "50", source_account_id "999", and destination_account_id "2"
    #     Then the response status code should be 404
    #     And the response should contain an "Account not found" error message

    # Scenario: Get Transactions for Account
    #     Given I have a user account with some transactions
    #     When I send a GET request to "/api/v1/transactions/1"
    #     Then the response status code should be 200
    #     And the response should contain a list of transactions for account 1
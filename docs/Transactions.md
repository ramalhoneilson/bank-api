# Example of transactions

#### **Accounts Table**
| id  | account_number | balance | type           | status | customer_id |
|-----|----------------|---------|----------------|--------|-------------|
| 1   | 1234444        | 1000.00 | USER           | ACTIVE | 1           |
| 2   | CASH_HOLD      | 5000.00 | ADMINISTRATIVE | ACTIVE | NULL        |
| 3   | CASH_DISBURSE  | 2000.00 | ADMINISTRATIVE | ACTIVE | NULL        |

#### **Transactions Table**
| id  | amount | timestamp           | transaction_type | source_account_id | destination_account_id |
|-----|--------|---------------------|------------------|-------------------|------------------------|
| 1   | 100.00 | 2023-10-01 12:00:00 | DEPOSIT          | 2                 | 1                      |
| 2   | 50.00  | 2023-10-01 12:05:00 | WITHDRAW         | 1                 | 3                      |

 # Extras
 - Implementation of Administrative accounts for better reporting and tracibility
 - Implementation of the Withdraw operation
 - For simplicity, we will work with Euro only.

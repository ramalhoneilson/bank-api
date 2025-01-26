class InsufficientFundsError(Exception):
    """The user does not have enough money in the account."""

    def __init__(self, message="Insufficient funds in the account."):
        self.message = message
        super().__init__(self.message)


class AccountNotFoundError(Exception):
    """when an account does ntt exist."""

    def __init__(self, message="Account not found."):
        self.message = message
        super().__init__(self.message)

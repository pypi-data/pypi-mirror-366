"""
Accounts resource handler for NetBird API.
"""

from typing import Any, Dict, List

from ..models import AccountSettings
from .base import BaseResource


class AccountsResource(BaseResource):
    """Handler for NetBird accounts API endpoints.

    Provides methods to manage NetBird accounts including listing,
    updating settings, and account deletion.
    """

    def list(self) -> List[Dict[str, Any]]:
        """List all accounts.

        Returns a list of accounts. Always returns a list of one account
        as users can only access their own account.

        Returns:
            List of account dictionaries

        Example:
            >>> accounts = client.accounts.list()
            >>> print(f"Account ID: {accounts[0].id}")
        """
        data = self.client.get("accounts")
        return self._parse_list_response(data)

    def update(self, account_id: str, settings: AccountSettings) -> Dict[str, Any]:
        """Update account settings.

        Args:
            account_id: Unique identifier of the account
            settings: Account settings to update

        Returns:
            Updated account dictionary

        Example:
            >>> settings = AccountSettings(
            ...     peer_login_expiration_enabled=True,
            ...     peer_login_expiration=3600
            ... )
            >>> account = client.accounts.update("account-id", settings)
        """
        data = self.client.put(
            f"accounts/{account_id}",
            data={"settings": settings.model_dump(exclude_unset=True)},
        )
        return self._parse_response(data)

    def delete(self, account_id: str) -> None:
        """Delete an account.

        Deletes an account and all its resources. Only account owners
        can delete accounts.

        Args:
            account_id: Unique identifier of the account

        Example:
            >>> client.accounts.delete("account-id")
        """
        self.client.delete(f"accounts/{account_id}")

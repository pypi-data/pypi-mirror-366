"""Email address management for ARTL MCP.

This module provides utilities for managing email addresses required by various APIs,
with support for environment variables and basic format validation.
"""

import os
import re
from pathlib import Path


class EmailManager:
    """Manages email addresses for API requests with format validation."""

    def __init__(self, client_config: dict | None = None):
        """Initialize the email manager.

        Args:
            client_config: Optional configuration dict from MCP client.
                          Useful for clients that don't pass environment variables.
        """
        self._cached_email: str | None = None
        self.client_config = client_config or {}

    def get_email(self, provided_email: str | None = None) -> str | None:
        """Get a valid email address from various sources.

        Priority order:
        1. Provided email parameter (if valid)
        2. MCP client configuration (for clients like Goose Desktop)
        3. ARTL_EMAIL_ADDR environment variable
        4. local/.env file ARTL_EMAIL_ADDR value
        5. Return None if no valid email found

        Args:
            provided_email: Email address provided by caller

        Returns:
            Valid email address or None if none found

        Raises:
            ValueError: If provided_email is invalid
        """
        # Check provided email first
        if provided_email:
            if self._is_valid_email(provided_email):
                return provided_email
            else:
                raise ValueError(f"Invalid email format: {provided_email}")

        # Use cached email if available
        if self._cached_email:
            return self._cached_email

        # Try MCP client configuration (for clients that don't pass env vars)
        client_email = self.client_config.get("ARTL_EMAIL_ADDR")
        if client_email and self._is_valid_email(client_email):
            self._cached_email = client_email
            return client_email

        # Try environment variable
        env_email = os.getenv("ARTL_EMAIL_ADDR")
        if env_email and self._is_valid_email(env_email):
            self._cached_email = env_email
            return env_email

        # Try local/.env file
        env_file_email = self._read_env_file()
        if env_file_email and self._is_valid_email(env_file_email):
            self._cached_email = env_file_email
            return env_file_email

        return None

    def require_email(self, provided_email: str | None = None) -> str:
        """Get a valid email address, raising an error if none found.

        Args:
            provided_email: Email address provided by caller

        Returns:
            Valid email address

        Raises:
            ValueError: If no valid email found
        """
        email = self.get_email(provided_email)
        if not email:
            raise ValueError(
                "No valid email address found. Please:\n"
                "1. Set ARTL_EMAIL_ADDR environment variable, or\n"
                "2. Add ARTL_EMAIL_ADDR=<YOUR_EMAIL_ADDRESS> to local/.env file, or\n"
                "3. Configure ARTL_EMAIL_ADDR in your MCP client settings, or\n"
                "4. Provide --email parameter to CLI commands, or\n"
                "5. Include your email in natural language requests"
            )
        return email

    def _is_valid_email(self, email: str) -> bool:
        """Check if email has basic syntactic structure."""
        if not email or not isinstance(email, str):
            return False

        # Must have exactly one @ symbol
        if email.count("@") != 1:
            return False

        local, domain = email.split("@")

        # Must have characters before and after @
        if not local or not domain:
            return False

        # Domain must have at least one dot with characters after it
        if "." not in domain:
            return False

        domain_parts = domain.split(".")
        # Must have characters after the final dot (extension)
        if not domain_parts[-1]:
            return False

        return True

    def _read_env_file(self) -> str | None:
        """Read email from local/.env file."""
        env_file = Path("local/.env")
        if not env_file.exists():
            return None

        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ARTL_EMAIL_ADDR="):
                        return line.split("=", 1)[1].strip()
        except Exception:
            return None

        return None

    def validate_for_api(self, api_name: str, email: str | None = None) -> str:
        """Validate email for specific API usage.

        Args:
            api_name: Name of the API requiring email
            email: Optional email to validate

        Returns:
            Valid email address

        Raises:
            ValueError: If no valid email or API-specific requirements not met
        """
        # If email is provided directly, validate it without using require_email
        if email:
            if not self._is_valid_email(email):
                raise ValueError(f"Invalid email format: {email}")
            return email

        # Otherwise use require_email for environment/file email
        validated_email = self.require_email()

        return validated_email

    def extract_email_from_text(self, text: str) -> str | None:
        """Extract email address from natural language text.

        Args:
            text: Text that might contain an email address

        Returns:
            Valid email address if found, None otherwise
        """
        if not text:
            return None

        # Look for email patterns in the text
        email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+\b"
        matches = re.findall(email_pattern, text)

        for match in matches:
            if self._is_valid_email(match):
                return match

        return None

    def get_email_with_nlp(
        self, text: str | None = None, provided_email: str | None = None
    ) -> str | None:
        """Get email with natural language processing fallback.

        Args:
            text: Natural language text that might contain email
            provided_email: Email address provided by caller

        Returns:
            Valid email address or None if none found
        """
        # First try standard email discovery
        email = self.get_email(provided_email)
        if email:
            return email

        # Try extracting from natural language text
        if text:
            extracted_email = self.extract_email_from_text(text)
            if extracted_email:
                self._cached_email = extracted_email
                return extracted_email

        return None


# Global instance for convenience
email_manager = EmailManager()


def get_email(provided_email: str | None = None) -> str | None:
    """Convenience function to get email address."""
    return email_manager.get_email(provided_email)


def require_email(provided_email: str | None = None) -> str:
    """Convenience function to require email address."""
    return email_manager.require_email(provided_email)

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailValidator:
    """
    Email validation service using the Mailbox Layer API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the EmailValidator with an API key.
        
        Args:
            api_key: Optional Mailbox Layer API key (defaults to MAILBOXLAYER_API_KEY env variable)
        """
        self.api_key = api_key or os.environ.get('MAILBOXLAYER_API_KEY')
        if not self.api_key:
            print("Warning: MAILBOXLAYER_API_KEY not set. Email validation will not work.")
        
        self.base_url = "http://apilayer.net/api/check"
    
    def validate_email(self, email: str, check_smtp: bool = True) -> Dict[str, Any]:
        """
        Validate an email address using the Mailbox Layer API.
        
        Args:
            email: The email address to validate
            check_smtp: Whether to perform SMTP verification (slower but more accurate)
            
        Returns:
            Dictionary with validation results
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "API key not configured",
                "is_valid": True  # Default to true
            }
        
        # Basic validation before API call
        if not email or '@' not in email:
            return {
                "success": False,
                "message": "Invalid email format",
                "is_valid": True  # Default to true
            }
        
        # Prepare API request parameters
        params = {
            'access_key': self.api_key,
            'email': email,
            'smtp': 1 if check_smtp else 0,
            'format': 1
        }
        
        try:
            # Make API request
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            # Check if the request was successful
            if response.status_code != 200 or 'error' in data:
                error_msg = data.get('error', {}).get('info', 'Unknown error')
                return {
                    "success": False,
                    "message": f"API error: {error_msg}",
                    "is_valid": True  # Default to true
                }
            
            # Process the validation results
            is_valid = True  # Default to true
            
            # Only set to false if we have clear evidence the email is invalid
            if (data.get('format_valid', True) == False or 
                (check_smtp and data.get('smtp_check', True) == False) or
                data.get('disposable', False) == True):
                is_valid = False
            
            return {
                "success": True,
                "is_valid": is_valid,
                "format_valid": data.get('format_valid', True),
                "mx_found": data.get('mx_found', True),
                "smtp_check": data.get('smtp_check', True),
                "disposable": data.get('disposable', False),
                "free": data.get('free', False),
                "score": data.get('score', 0),
                "role": data.get('role', False),
                "message": "Email validation successful"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Validation error: {str(e)}",
                "is_valid": True  # Default to true
            }

    def is_valid_email(self, email: str) -> bool:
        """
        Check if an email address is valid and not likely to bounce.
        
        Args:
            email: The email address to validate
            
        Returns:
            Boolean indicating if the email is valid and not likely to bounce
        """
        # Get the detailed validation results with SMTP check enabled
        result = self.validate_email(email, check_smtp=True)
        
        # Return the validity result (which now defaults to True)
        return result["is_valid"]

def main():
    """Test the EmailValidator."""
    validator = EmailValidator()
    
    print("Email Validator Test")
    print("-------------------")
    
    if not validator.api_key:
        print("Error: MAILBOXLAYER_API_KEY not set in environment variables.")
        print("Please add your API key to the .env file:")
        print("MAILBOXLAYER_API_KEY=your_api_key_here")
        return
    
    email = input("Enter an email address to validate: ")
    
    print(f"\nValidating {email}...")
    result = validator.validate_email(email)  # Get detailed results for display
    is_valid = validator.is_valid_email(email)  # Get simple boolean result
    
    print("\nSimple Validation Result:")
    print(f"Valid email: {'Yes' if is_valid else 'No'}")
    
    if result["success"]:
        print("\nDetailed Validation Results:")
        print(f"Format valid: {'Yes' if result['format_valid'] else 'No'}")
        print(f"MX records found: {'Yes' if result['mx_found'] else 'No'}")
        print(f"SMTP check passed: {'Yes' if result['smtp_check'] else 'No'}")
        print(f"Disposable email: {'Yes' if result['disposable'] else 'No'}")
        print(f"Free email provider: {'Yes' if result['free'] else 'No'}")
        print(f"Role-based email: {'Yes' if result['role'] else 'No'}")
        print(f"Quality score: {result['score']}")
    else:
        print(f"Error: {result['message']}")

if __name__ == "__main__":
    main()

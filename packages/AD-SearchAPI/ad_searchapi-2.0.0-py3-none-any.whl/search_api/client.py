import json
import re
import gzip
import io
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin
from dataclasses import asdict

import phonenumbers
import requests
from cachetools import TTLCache
from dateutil.parser import parse
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session, Response
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

from .exceptions import (
    AuthenticationError,
    InsufficientBalanceError,
    RateLimitError,
    SearchAPIError,
    ServerError,
    NetworkError,
    TimeoutError,
    ConfigurationError,
    ValidationError,
)
from .models import (
    Address,
    BalanceInfo,
    DomainSearchResult,
    EmailSearchResult,
    Person,
    PhoneNumber,
    PhoneSearchResult,
    SearchAPIConfig,
    PhoneFormat,
    SearchType,
    AccessLog,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SearchAPI:
    """
    A comprehensive client for the Search API with enhanced error handling,
    balance checking, and improved data processing.
    """
    
    def __init__(self, api_key: str = None, config: SearchAPIConfig = None):
        """
        Initialize the Search API client.
        
        Args:
            api_key: API key for authentication
            config: Configuration object with advanced settings
        """
        if config is None:
            if api_key is None:
                raise ConfigurationError("Either api_key or config must be provided")
            config = SearchAPIConfig(api_key=api_key)
        
        self.config = config
        self.session = self._create_session()
        self.cache = self._create_cache()
        self._balance_cache = None
        self._balance_cache_time = None
        
        # Constants for data processing
        self.MAJOR_DOMAINS = {
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com",
            "icloud.com", "live.com", "msn.com", "comcast.net", "me.com",
            "mac.com", "att.net", "verizon.net", "protonmail.com", "zoho.com",
            "yandex.com", "mail.com", "gmx.com", "rocketmail.com", "yahoo.co.uk",
            "btinternet.com", "bellsouth.net",
        }
        
        self.STREET_TYPE_MAP = {
            "st": "Street", "ave": "Avenue", "blvd": "Boulevard", "rd": "Road",
            "ln": "Lane", "dr": "Drive", "ct": "Court", "ter": "Terrace",
            "pl": "Place", "way": "Way", "pkwy": "Parkway", "cir": "Circle",
            "sq": "Square", "hwy": "Highway", "bend": "Bend", "cove": "Cove",
        }
        
        self.STATE_ABBREVIATIONS = {
            "al": "AL", "ak": "AK", "az": "AZ", "ar": "AR", "ca": "CA",
            "co": "CO", "ct": "CT", "de": "DE", "fl": "FL", "ga": "GA",
            "hi": "HI", "id": "ID", "il": "IL", "in": "IN", "ia": "IA",
            "ks": "KS", "ky": "KY", "la": "LA", "me": "ME", "md": "MD",
            "ma": "MA", "mi": "MI", "mn": "MN", "ms": "MS", "mo": "MO",
            "mt": "MT", "ne": "NE", "nv": "NV", "nh": "NH", "nj": "NJ",
            "nm": "NM", "ny": "NY", "nc": "NC", "nd": "ND", "oh": "OH",
            "ok": "OK", "or": "OR", "pa": "PA", "ri": "RI", "sc": "SC",
            "sd": "SD", "tn": "TN", "tx": "TX", "ut": "UT", "vt": "VT",
            "va": "VA", "wa": "WA", "wv": "WV", "wi": "WI", "wy": "WY",
        }
    
    def _create_session(self) -> Session:
        """Create and configure the HTTP session."""
        session = Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1,
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        
        # Configure proxy if provided
        if self.config.proxy:
            session.proxies.update(self.config.proxy)
        
        return session
    
    def _create_cache(self) -> Optional[TTLCache]:
        """Create cache if enabled."""
        if self.config.enable_caching:
            return TTLCache(maxsize=self.config.max_cache_size, ttl=self.config.cache_ttl)
        return None
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove common separators and spaces
        cleaned_phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
        
        # Check if it starts with + (international format)
        if cleaned_phone.startswith("+"):
            # International format: +[country code][number]
            if len(cleaned_phone) >= 10:  # At least country code + 7 digits
                return True
        
        # Check if it's a US number without country code (10 digits)
        if len(cleaned_phone) == 10 and cleaned_phone.isdigit():
            return True
        
        # Check if it's a US number with country code (11 digits starting with 1)
        if len(cleaned_phone) == 11 and cleaned_phone.startswith("1") and cleaned_phone.isdigit():
            return True
        
        return False
    
    def _validate_domain(self, domain: str) -> bool:
        """Validate domain format."""
        if not domain or not isinstance(domain, str):
            return False
        
        # Basic domain validation
        domain = domain.lower().strip()
        
        # Check for valid characters
        if not domain.replace(".", "").replace("-", "").isalnum():
            return False
        
        # Check for at least one dot
        if "." not in domain:
            return False
        
        # Check that it doesn't start or end with dot
        if domain.startswith(".") or domain.endswith("."):
            return False
        
        # Check for valid TLD (at least 2 characters after last dot)
        parts = domain.split(".")
        if len(parts) < 2 or len(parts[-1]) < 2:
            return False
        
        # Check that each part is not empty and doesn't start/end with hyphen
        for part in parts:
            if not part or part.startswith("-") or part.endswith("-"):
                return False
        
        return True
    
    def _check_balance(self, required_credits: int = 1) -> None:
        """Check if account has sufficient balance for the operation."""
        try:
            balance_info = self.get_balance()
            if balance_info.current_balance < required_credits:
                raise InsufficientBalanceError(
                    f"Insufficient balance. Current: {balance_info.current_balance}, Required: {required_credits}",
                    current_balance=balance_info.current_balance,
                    required_credits=required_credits
                )
        except InsufficientBalanceError:
            # Re-raise the exception
            raise
        except Exception as e:
            # Log other errors but don't fail the operation
            if self.config.debug_mode:
                logger.warning(f"Could not verify balance: {e}")
    
    def get_balance(self) -> BalanceInfo:
        """
        Get current account balance using the correct API endpoint.
        
        Returns:
            BalanceInfo object with current balance details
            
        Raises:
            SearchAPIError: If balance check fails
        """
        # Check cache first
        if self._balance_cache and self._balance_cache_time:
            cache_age = (datetime.now() - self._balance_cache_time).total_seconds()
            if cache_age < 300:  # 5 minutes cache
                return self._balance_cache
        
        try:
            # Use the correct API endpoint for balance
            balance_url = f"{self.config.base_url}?action=get_balance&api_key={self.config.api_key}"
            
            if self.config.debug_mode:
                logger.debug(f"Making balance request to: {balance_url}")
            
            response = self.session.get(balance_url, timeout=self.config.timeout)
            
            if response.status_code != 200:
                raise ServerError(f"Balance request failed: {response.status_code}", status_code=response.status_code)
            
            response_data = self._parse_response(response)
            
            if "balance" not in response_data:
                raise ServerError("Invalid balance response from server")
            
            balance_info = BalanceInfo(
                current_balance=float(response_data["balance"]),
                currency="USD",  # Default currency
                last_updated=datetime.now(),
                credit_cost_per_search=1.0  # Default cost per search
            )
            
            # Update cache
            self._balance_cache = balance_info
            self._balance_cache_time = datetime.now()
            
            return balance_info
            
        except Exception as e:
            if isinstance(e, SearchAPIError):
                raise
            raise SearchAPIError(f"Failed to get balance: {str(e)}")
    
    def get_access_logs(self) -> List[AccessLog]:
        """
        Get access logs using the correct API endpoint.
        
        Returns:
            List of AccessLog objects with access information
            
        Raises:
            SearchAPIError: If access logs retrieval fails
        """
        try:
            # Use the correct API endpoint for access logs
            logs_url = f"{self.config.base_url}?action=get_access_logs&api_key={self.config.api_key}"
            
            if self.config.debug_mode:
                logger.debug(f"Making access logs request to: {logs_url}")
            
            response = self.session.get(logs_url, timeout=self.config.timeout)
            
            if response.status_code != 200:
                raise ServerError(f"Access logs request failed: {response.status_code}", status_code=response.status_code)
            
            response_data = self._parse_response(response)
            
            if "logs" not in response_data:
                raise ServerError("Invalid access logs response from server")
            
            access_logs = []
            for log_entry in response_data["logs"]:
                access_log = AccessLog(
                    ip_address=log_entry.get("ip_address", ""),
                    last_accessed=parse(log_entry["last_accessed"]) if log_entry.get("last_accessed") else None,
                    user_agent=log_entry.get("user_agent"),
                    endpoint=log_entry.get("endpoint"),
                    method=log_entry.get("method"),
                    status_code=log_entry.get("status_code"),
                    response_time=log_entry.get("response_time"),
                )
                access_logs.append(access_log)
            
            return access_logs
            
        except Exception as e:
            if isinstance(e, SearchAPIError):
                raise
            raise SearchAPIError(f"Failed to get access logs: {str(e)}")
    
    def _make_request(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to the Search API.
        
        Args:
            params: Request parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            Various SearchAPIError subclasses based on the error
        """
        if params is None:
            params = {}
        
        # Add API key to params
        params["key"] = self.config.api_key
        
        try:
            if self.config.debug_mode:
                logger.debug(f"Making request to {self.config.base_url} with params: {params}")
            
            response = self.session.post(
                self.config.base_url,
                data=params,
                timeout=self.config.timeout
            )
            
            if self.config.debug_mode:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Handle different response status codes
            if response.status_code == 200:
                return self._parse_response(response)
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key", status_code=401)
            elif response.status_code == 402:
                raise InsufficientBalanceError("Insufficient balance", status_code=402)
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", status_code=429)
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {response.status_code}", status_code=response.status_code)
            else:
                raise SearchAPIError(f"Request failed: {response.status_code}", status_code=response.status_code)
                
        except Timeout:
            raise TimeoutError("Request timed out")
        except ConnectionError:
            raise NetworkError("Network connection error")
        except RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}")
        except Exception as e:
            raise SearchAPIError(f"Unexpected error: {str(e)}")
    
    def _parse_response(self, response: Response) -> Dict[str, Any]:
        """
        Parse API response and handle various content encodings.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed response data
            
        Raises:
            ServerError: If response parsing fails
        """
        try:
            content = response.content
            content_encoding = response.headers.get("content-encoding", "").lower()
            
            # Handle different content encodings
            if content_encoding == "gzip":
                content = gzip.decompress(content)
            elif content_encoding == "br" and BROTLI_AVAILABLE:
                content = brotli.decompress(content)
            elif content_encoding == "deflate":
                import zlib
                content = zlib.decompress(content)
            
            # Try to parse as JSON
            try:
                return json.loads(content.decode("utf-8"))
            except json.JSONDecodeError:
                # Try to parse as plain text
                text_content = content.decode("utf-8")
                
                # Check for error messages in plain text
                if "error" in text_content.lower():
                    error_msg = text_content.strip()
                    if "insufficient" in error_msg.lower() and "balance" in error_msg.lower():
                        raise InsufficientBalanceError(error_msg, status_code=402)
                    elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                        raise AuthenticationError(error_msg, status_code=401)
                    elif "rate limit" in error_msg.lower():
                        raise RateLimitError(error_msg, status_code=429)
                    else:
                        raise ServerError(error_msg)
                
                # If it's not an error, try to parse as key-value pairs
                try:
                    return dict(line.split("=", 1) for line in text_content.splitlines() if "=" in line)
                except Exception:
                    raise ServerError("Unable to parse response")
                    
        except Exception as e:
            if isinstance(e, SearchAPIError):
                raise
            raise ServerError(f"Failed to parse response: {str(e)}")
    
    def _format_address(self, address_str: str) -> str:
        """Format address string for better readability."""
        if not address_str:
            return ""
        
        # Normalize street types
        for abbrev, full in self.STREET_TYPE_MAP.items():
            pattern = rf'\b{abbrev}\b'
            address_str = re.sub(pattern, full, address_str, flags=re.IGNORECASE)
        
        # Normalize state abbreviations
        for abbrev, full in self.STATE_ABBREVIATIONS.items():
            pattern = rf'\b{abbrev}\b'
            address_str = re.sub(pattern, full, address_str, flags=re.IGNORECASE)
        
        return address_str.strip()
    
    def _parse_address(self, address_data: Union[str, Dict]) -> Address:
        """Parse address data into Address object."""
        if isinstance(address_data, str):
            address_str = self._format_address(address_data)
            return Address(street=address_str)
        
        if isinstance(address_data, dict):
            # Handle the actual API response structure
            if "address" in address_data:
                # This is the structured format with property details
                street = address_data.get("address", "")
                zestimate = address_data.get("zestimate")
                zpid = address_data.get("zpid")
                
                # Parse property details if available
                property_details = address_data.get("property_details", {})
                bedrooms = property_details.get("bedrooms")
                bathrooms = property_details.get("bathrooms")
                living_area = property_details.get("living_area")
                home_status = property_details.get("home_status")
                
                return Address(
                    street=self._format_address(street),
                    city=property_details.get("city"),
                    state=property_details.get("state"),
                    postal_code=property_details.get("zipcode"),
                    country=None,
                    zestimate=Decimal(str(zestimate)) if zestimate else None,
                    zpid=zpid,
                    bedrooms=bedrooms,
                    bathrooms=bathrooms,
                    living_area=living_area,
                    home_status=home_status,
                )
            else:
                # Fallback for other dictionary formats
                return Address(
                    street=self._format_address(address_data.get("street", "")),
                    city=address_data.get("city"),
                    state=address_data.get("state"),
                    postal_code=address_data.get("postal_code"),
                    country=address_data.get("country"),
                    zestimate=Decimal(str(address_data["zestimate"])) if address_data.get("zestimate") else None,
                    zpid=address_data.get("zpid"),
                    bedrooms=address_data.get("bedrooms"),
                    bathrooms=address_data.get("bathrooms"),
                    living_area=address_data.get("living_area"),
                    home_status=address_data.get("home_status"),
                    last_known_date=parse(address_data["last_known"]).date() if address_data.get("last_known") else None,
                )
        
        return Address(street="")
    
    def _parse_phone_number(self, phone_data: Union[str, Dict], phone_format: str = "international") -> PhoneNumber:
        """Parse phone number data into PhoneNumber object."""
        if isinstance(phone_data, str):
            number = phone_data
            # Clean up the number
            number = number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
            
            # Ensure proper international format
            if number.startswith("1") and len(number) == 11:
                number = "+" + number
            elif not number.startswith("+"):
                number = "+1" + number
            
            return PhoneNumber(
                number=number,
                is_valid=True,
                phone_type="MOBILE",
                carrier=None,
            )
        
        if isinstance(phone_data, dict):
            number = phone_data.get("number", "")
            # Clean up the number
            number = number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
            
            # Ensure proper international format
            if number.startswith("1") and len(number) == 11:
                number = "+" + number
            elif not number.startswith("+"):
                number = "+1" + number
            
            return PhoneNumber(
                number=number,
                country_code=phone_data.get("country_code", "US"),
                is_valid=phone_data.get("is_valid", True),
                phone_type=phone_data.get("phone_type"),
                carrier=phone_data.get("carrier"),
            )
        
        return PhoneNumber(number="")
    
    def _parse_person(self, person_data: Dict) -> Person:
        """Parse person data into Person object."""
        return Person(
            name=person_data.get("name"),
            dob=parse(person_data["dob"]).date() if person_data.get("dob") else None,
            age=person_data.get("age"),
        )
    
    def search_email(
        self, 
        email: str, 
        include_house_value: bool = False, 
        include_extra_info: bool = False, 
        phone_format: str = "international"
    ) -> EmailSearchResult:
        """
        Search for information by email address.
        
        Args:
            email: Email address to search for
            include_house_value: Whether to include property value information
            include_extra_info: Whether to include additional information
            phone_format: Format for phone numbers (international, national, e164)
            
        Returns:
            EmailSearchResult with search results
            
        Raises:
            ValidationError: If email is invalid
            InsufficientBalanceError: If account has insufficient balance
            SearchAPIError: For other API errors
        """
        # Validate input
        if not self._validate_email(email):
            raise ValidationError(f"Invalid email format: {email}")
        
        # Check balance before making request
        self._check_balance(required_credits=1)
        
        # Check cache
        cache_key = f"email:{email}:{include_house_value}:{include_extra_info}:{phone_format}"
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Prepare request parameters
        params = {
            "type": "email",
            "email": email,
        }
        
        if include_house_value:
            params["include_house_value"] = "1"
        if include_extra_info:
            params["include_extra_info"] = "1"
        
        # Make request
        response_data = self._make_request(params)
        
        # Parse response
        result = self._parse_email_response(response_data, email, phone_format)
        
        # Cache result
        if self.cache:
            self.cache[cache_key] = result
        
        return result
    
    def _parse_email_response(self, response_data: Dict, email: str, phone_format: str) -> EmailSearchResult:
        """Parse email search response."""
        # Extract person information
        person = None
        if "name" in response_data or "dob" in response_data:
            person = Person(
                name=response_data.get("name"),
                dob=parse(response_data["dob"]).date() if response_data.get("dob") else None,
                age=response_data.get("age"),
            )
        
        # Parse addresses
        addresses = []
        if "addresses" in response_data:
            address_data = response_data["addresses"]
            if isinstance(address_data, list):
                addresses = [self._parse_address(addr) for addr in address_data]
            else:
                addresses = [self._parse_address(address_data)]
        
        # Parse phone numbers
        phone_numbers = []
        if "numbers" in response_data:
            phone_data = response_data["numbers"]
            if isinstance(phone_data, list):
                phone_numbers = [self._parse_phone_number(phone, phone_format) for phone in phone_data]
            else:
                phone_numbers = [self._parse_phone_number(phone_data, phone_format)]
        
        # Parse additional emails
        emails = []
        if "emails" in response_data:
            emails = response_data["emails"] if isinstance(response_data["emails"], list) else [response_data["emails"]]
        
        return EmailSearchResult(
            email=email,
            person=person,
            addresses=addresses,
            phone_numbers=phone_numbers,
            emails=emails,
            search_timestamp=datetime.now(),
            total_results=len(addresses) + len(phone_numbers),
            search_cost=response_data.get("cost", 1.0),
            email_valid=response_data.get("email_valid", True),
            email_type=response_data.get("email_type"),
        )
    
    def search_phone(
        self, 
        phone: str, 
        include_house_value: bool = False, 
        include_extra_info: bool = False, 
        phone_format: str = "international"
    ) -> List[PhoneSearchResult]:
        """
        Search for information by phone number.
        
        Args:
            phone: Phone number to search for
            include_house_value: Whether to include property value information
            include_extra_info: Whether to include additional information
            phone_format: Format for phone numbers (international, national, e164)
            
        Returns:
            List of PhoneSearchResult objects
            
        Raises:
            ValidationError: If phone number is invalid
            InsufficientBalanceError: If account has insufficient balance
            SearchAPIError: For other API errors
        """
        # Validate input
        if not self._validate_phone(phone):
            raise ValidationError(f"Invalid phone number format: {phone}")
        
        # Check balance before making request
        self._check_balance(required_credits=1)
        
        # Check cache
        cache_key = f"phone:{phone}:{include_house_value}:{include_extra_info}:{phone_format}"
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Prepare request parameters
        params = {
            "type": "phone",
            "phone": phone,
        }
        
        if include_house_value:
            params["include_house_value"] = "1"
        if include_extra_info:
            params["include_extra_info"] = "1"
        
        # Make request
        response_data = self._make_request(params)
        
        # Parse response
        results = self._parse_phone_response(response_data, phone, phone_format)
        
        # Cache result
        if self.cache:
            self.cache[cache_key] = results
        
        return results
    
    def _parse_phone_response(self, response_data: Dict, phone: str, phone_format: str) -> List[PhoneSearchResult]:
        """Parse phone search response."""
        results = []
        
        # Handle multiple results
        if "results" in response_data and isinstance(response_data["results"], list):
            for result_data in response_data["results"]:
                results.append(self._parse_single_phone_result(result_data, phone, phone_format))
        else:
            # Single result
            results.append(self._parse_single_phone_result(response_data, phone, phone_format))
        
        return results
    
    def _parse_single_phone_result(self, result_data: Dict, phone: str, phone_format: str) -> PhoneSearchResult:
        """Parse single phone search result."""
        # Parse person information
        person = None
        if "name" in result_data or "dob" in result_data:
            person = Person(
                name=result_data.get("name"),
                dob=parse(result_data["dob"]).date() if result_data.get("dob") else None,
                age=result_data.get("age"),
            )
        
        # Parse addresses
        addresses = []
        if "addresses" in result_data:
            address_data = result_data["addresses"]
            if isinstance(address_data, list):
                addresses = [self._parse_address(addr) for addr in address_data]
            else:
                addresses = [self._parse_address(address_data)]
        
        # Parse phone numbers
        phone_numbers = []
        if "numbers" in result_data:
            phone_data = result_data["numbers"]
            if isinstance(phone_data, list):
                phone_numbers = [self._parse_phone_number(phone_num, phone_format) for phone_num in phone_data]
            else:
                phone_numbers = [self._parse_phone_number(phone_data, phone_format)]
        
        # Parse additional emails
        emails = []
        if "emails" in result_data:
            emails = result_data["emails"] if isinstance(result_data["emails"], list) else [result_data["emails"]]
        
        return PhoneSearchResult(
            phone=self._parse_phone_number(phone, phone_format),
            person=person,
            addresses=addresses,
            phone_numbers=phone_numbers,
            emails=emails,
            search_timestamp=datetime.now(),
            total_results=len(addresses) + len(phone_numbers),
            search_cost=result_data.get("cost", 1.0),
        )
    
    def search_domain(self, domain: str) -> DomainSearchResult:
        """
        Search for information by domain.
        
        Args:
            domain: Domain to search for
            
        Returns:
            DomainSearchResult with search results
            
        Raises:
            ValidationError: If domain is invalid
            InsufficientBalanceError: If account has insufficient balance
            SearchAPIError: For other API errors
        """
        # Validate input
        if not self._validate_domain(domain):
            raise ValidationError(f"Invalid domain format: {domain}")
        
        # Check balance before making request
        self._check_balance(required_credits=1)
        
        # Check cache
        cache_key = f"domain:{domain}"
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Prepare request parameters
        params = {
            "type": "domain",
            "domain": domain,
        }
        
        # Make request
        response_data = self._make_request(params)
        
        # Parse response
        result = self._parse_domain_response(response_data, domain)
        
        # Cache result
        if self.cache:
            self.cache[cache_key] = result
        
        return result
    
    def _parse_domain_response(self, response_data: Dict, domain: str) -> DomainSearchResult:
        """Parse domain search response."""
        results = []
        
        if "results" in response_data and isinstance(response_data["results"], list):
            for result_data in response_data["results"]:
                email_result = EmailSearchResult(
                    email=result_data.get("email", ""),
                    person=Person(name=result_data.get("name")) if result_data.get("name") else None,
                    addresses=[self._parse_address(addr) for addr in result_data.get("addresses", [])],
                    phone_numbers=[self._parse_phone_number(phone) for phone in result_data.get("numbers", [])],
                    emails=result_data.get("emails", []),
                    search_timestamp=datetime.now(),
                    total_results=len(result_data.get("addresses", [])) + len(result_data.get("numbers", [])),
                    search_cost=result_data.get("cost", 1.0),
                    email_valid=result_data.get("email_valid", True),
                    email_type=result_data.get("email_type"),
                )
                results.append(email_result)
        
        return DomainSearchResult(
            domain=domain,
            results=results,
            total_results=len(results),
            domain_valid=response_data.get("domain_valid", True),
            search_cost=response_data.get("cost", 1.0),
        )
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        if self.cache:
            self.cache.clear()
        self._balance_cache = None
        self._balance_cache_time = None
    
    def close(self) -> None:
        """Close the client and clean up resources."""
        self.session.close()
        self.clear_cache()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
import logging
import phonenumbers
from phonenumbers import PhoneNumberFormat, PhoneNumberType
from phonenumbers.carrier import name_for_number

logger = logging.getLogger("app.utils.phone")


class PhoneValidator:
    """
    Industrial-Grade Telephone Validation & Normalization Engine.
    Powered by Google's libphonenumbers to strictly enforce E.164 compliance 
    and verify legitimate Tanzanian cellular carrier blocks.
    """

    @staticmethod
    def validate_and_normalize_tz_number(raw_phone: str) -> str | None:
        """
        Deeply inspects an incoming string sequence. 
        Validates structure syntax and formats into strict E.164 code (+255XXXXXXXXX).
        Returns None if the phone line is structurally illegitimate or fake.
        """
        if not raw_phone:
            return None

        try:
            # Step A: Parse the incoming string using Tanzania ('TZ') as the default country context block
            # This allows Google's engine to automatically map local formats (07..., 06...) correctly
            parsed_number = phonenumbers.parse(raw_phone.strip(), "TZ")

            # Step B: Strict Verification Guard
            # Checks if the number matches legitimate cellular length and operator patterns for Tanzania
            if not phonenumbers.is_valid_number(parsed_number):
                logger.warning(f"Phone verification pipeline rejected structurally invalid number layout: {raw_phone}")
                return None

            # Step C: Hard Type Isolation
            # Enforces that the incoming line is strictly a MOBILE cellular phone block.
            # Disallows landlines, premium toll-free numbers, or fake VoIP lines from entering our pool.
            number_type = phonenumbers.number_type(parsed_number)
            if number_type not in [PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE]:
                logger.warning(f"Phone verification pipeline rejected non-cellular connection type structural format: {raw_phone}")
                return None

            # Step D: Final Formatting Normalization
            # Compiles the parsed tokens into a single clean international standard string (+255XXXXXXXXX)
            clean_e164_string = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
            return clean_e164_string

        except Exception as e:
            # Intercept decoding failures gracefully to keep background application threads operational
            logger.error(f"Unexpected internal failure inside library number parsing sequence: {str(e)}")
            return None

    @staticmethod
    def extract_tanzanian_carrier(clean_phone: str) -> str:
        """
        Utility lookup helper. Identifies active Tanzanian network operators 
        (e.g., 'Vodacom', 'Airtel', 'Tigo', 'Halotel', 'TTCL') directly from the normalized E.164 line.
        """
        try:
            parsed_number = phonenumbers.parse(clean_phone, "TZ")
            # Pulls English carrier identifier tags registered on international blocks
            carrier_name = name_for_number(parsed_number, "en")
            return carrier_name if carrier_name else "Unknown Carrier"
        except Exception:
            return "Unknown Carrier"

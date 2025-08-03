import sys
from hanifx.core import validator, carrier, region, google, whatsapp, telegram, facebook, breach
from hanifx.utils import renderer, spinner

def main():
    if len(sys.argv) != 2:
        print("Usage: hanifx <phone_number>")
        sys.exit(1)

    number = sys.argv[1]

    print("[hanifx] 🔍 Validating number...")
    spinner.spinner("Checking format")
    parsed = validator.parse_number(number)
    if not parsed:
        print("❌ Invalid phone number!")
        sys.exit(1)

    spinner.spinner("Detecting carrier and region")
    carrier_name = carrier.get_carrier(number)
    region_name = region.get_region(number)

    spinner.spinner("Running OSINT checks")
    whatsapp_status = whatsapp.check(number)
    telegram_status = telegram.check(number)
    facebook_url = facebook.search_url(number)
    google_results = google.scrape(number)
    breach_info = breach.check(number)

    result = {
        "Country": parsed["country"],
        "Carrier": carrier_name,
        "Region": region_name,
        "WhatsApp": whatsapp_status,
        "Telegram": telegram_status,
        "Facebook Search URL": facebook_url,
        "Google Results": google_results,
        "Breach Info": breach_info
    }

    renderer.display(result)

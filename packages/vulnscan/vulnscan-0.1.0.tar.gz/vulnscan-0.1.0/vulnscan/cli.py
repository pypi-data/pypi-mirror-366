import argparse
from . import pdf


def main():
    parser = argparse.ArgumentParser(
        description="Run VulnScan on a target URL")
    parser.add_argument('--url', type=str,
                        help='Target URL to scan', required=True)

    # Add subcommands for each scan
    parser.add_argument(
        '--scan',
        type=str,
        choices=[
            "all", "port_scan", "domain_enum", "fingerprint", "sql_injection",
            "xss", "csrf", "ssl", "geolocation", "directory_enum",
            "vuln_scan", "spider", "report", "headers", "dns_lookup"
        ],
        default="all",
        help="Specify the scan to run (default: all)"
    )

    args = parser.parse_args()

    url = args.url
    scan = args.scan

    if scan == "all":
        pdf.run_scan(url)
    elif scan == "port_scan":
        pdf.port_scan(url)
    elif scan == "domain_enum":
        pdf.domain_enumeration(url)
    elif scan == "fingerprint":
        pdf.fingerprint(url)
    elif scan == "sql_injection":
        pdf.sql_injection_test(url)
    elif scan == "xss":
        pdf.xss_test(url)
    elif scan == "csrf":
        pdf.csrf_test(url)
    elif scan == "ssl":
        pdf.ssl_tls_check(url)
    elif scan == "geolocation":
        pdf.find_geolocation(url)
    elif scan == "directory_enum":
        pdf.directory_enumeration(url)
    elif scan == "vuln_scan":
        pdf.vulnerability_scan(url)
    elif scan == "spider":
        pdf.spider_website(url)
    elif scan == "report":
        pdf.generate_report(url)
    elif scan == "headers":
        pdf.http_headers_check(url)
    elif scan == "dns_lookup":
        pdf.dns_lookup(url)
    else:
        print("Invalid scan type selected.")

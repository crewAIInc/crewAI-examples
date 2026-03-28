"""Run the KYB Compliance Verification Crew."""

from kyb_compliance_crew.crew import KybComplianceCrew


def run():
    """Run a KYB check on a Swedish company (Spotify AB)."""
    inputs = {
        "company_id": "556703-7485",
        "company_name": "Spotify AB",
        "country": "SE",
    }
    result = KybComplianceCrew().crew().kickoff(inputs=inputs)
    print("\n" + "=" * 60)
    print("KYB VERIFICATION REPORT")
    print("=" * 60)
    print(result)

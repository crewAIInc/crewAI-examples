from trulens.dashboard import run_dashboard
from trulens.core import TruSession

session = TruSession()

run_dashboard(session=session)

if __name__ == "__main__":
    run_dashboard()

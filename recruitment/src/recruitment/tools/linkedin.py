from crewai_tools import BaseTool

from .client import Client as LinkedinClient


class LinkedInTool(BaseTool):
    name: str = "Retrieve LinkedIn profiles"
    description: str = (
        "Retrieve LinkedIn profiles given a list of skills. Comma separated"
    )

    def _run(self, skills: str) -> str:
        linkedin_client = LinkedinClient()
        people = linkedin_client.find_people(skills)
        people = self._format_publications_to_text(people)
        linkedin_client.close()
        return people

    def _format_publications_to_text(self, people):
        result = ["\n".join([
            "Person Profile",
            "-------------",
            p['name'],
            p['position'],
            p['location']
        ]) for p in people]
        result = "\n\n".join(result)

        return result

from textwrap import dedent
from crewai import Task

class Tasks():
		def research_company_culture_task(self, agent, company_description, company_domain):
				return Task(
						description=dedent(f"""\
								Analyze the provided company website and the hiring manager's company's domain {company_domain}, description: "{company_description}". Focus on understanding the company's culture, values, and mission. Identify unique selling points and specific projects or achievements highlighted on the site.
								Compile a report summarizing these insights, specifically how they can be leveraged in a job posting to attract the right candidates."""),
						expected_output=dedent("""\
								A comprehensive report detailing the company's culture, values, and mission, along with specific selling points relevant to the job role. Suggestions on incorporating these insights into the job posting should be included."""),
						agent=agent
				)

		def research_role_requirements_task(self, agent, hiring_needs):
				return Task(
						description=dedent(f"""\
								Based on the hiring manager's needs: "{hiring_needs}", identify the key skills, experiences, and qualities the ideal candidate should possess for the role. Consider the company's current projects, its competitive landscape, and industry trends. Prepare a list of recommended job requirements and qualifications that align with the company's needs and values."""),
						expected_output=dedent("""\
								A list of recommended skills, experiences, and qualities for the ideal candidate, aligned with the company's culture, ongoing projects, and the specific role's requirements."""),
						agent=agent
				)

		def draft_job_posting_task(self, agent, company_description, hiring_needs, specific_benefits):
				return Task(
						description=dedent(f"""\
								Draft a job posting for the role described by the hiring manager: "{hiring_needs}". Use the insights on "{company_description}" to start with a compelling introduction, followed by a detailed role description, responsibilities, and required skills and qualifications. Ensure the tone aligns with the company's culture and incorporate any unique benefits or opportunities offered by the company.
								Specfic benefits: "{specific_benefits}"""),
						expected_output=dedent("""\
								A detailed, engaging job posting that includes an introduction, role description, responsibilities, requirements, and unique company benefits. The tone should resonate with the company's culture and values, aimed at attracting the right candidates."""),
						agent=agent
				)

		def review_and_edit_job_posting_task(self, agent, hiring_needs):
				return Task(
						description=dedent(f"""\
								Review the draft job posting for the role: "{hiring_needs}". Check for clarity, engagement, grammatical accuracy, and alignment with the company's culture and values. Edit and refine the content, ensuring it speaks directly to the desired candidates and accurately reflects the role's unique benefits and opportunities. Provide feedback for any necessary revisions."""),
						expected_output=dedent("""\
								A polished, error-free job posting that is clear, engaging, and perfectly aligned with the company's culture and values. Feedback on potential improvements and final approval for publishing. Formated in markdown."""),
						agent=agent,
						output_file="job_posting.md"
				)

		def industry_analysis_task(self, agent, company_domain, company_description):
				return Task(
						description=dedent(f"""\
								Conduct an in-depth analysis of the industry related to the company's domain: "{company_domain}". Investigate current trends, challenges, and opportunities within the industry, utilizing market reports, recent developments, and expert opinions. Assess how these factors could impact the role being hired for and the overall attractiveness of the position to potential candidates.
								Consider how the company's position within this industry and its response to these trends could be leveraged to attract top talent. Include in your report how the role contributes to addressing industry challenges or seizing opportunities."""),
						expected_output=dedent("""\
								A detailed analysis report that identifies major industry trends, challenges, and opportunities relevant to the company's domain and the specific job role. This report should provide strategic insights on positioning the job role and the company as an attractive choice for potential candidates."""),
						agent=agent
				)

import sys
from job_posting.crew import JobPostingCrew

def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'company_domain':'careers.wbd.com',
        'company_description': "Warner Bros. Discovery is a premier global media and entertainment company, offering audiences the world’s most differentiated and complete portfolio of content, brands and franchises across television, film, sports, news, streaming and gaming. We're home to the world’s best storytellers, creating world-class products for consumers",
        'hiring_needs': 'Production Assistant, for a TV production set in Los Angeles in June 2025',
        'specific_benefits':'Weekly Pay, Employee Meals, healthcare',
    }
    JobPostingCrew().crew().kickoff(inputs=inputs)



def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'company_domain':'careers.wbd.com',
        'company_description': "Warner Bros. Discovery is a premier global media and entertainment company, offering audiences the world’s most differentiated and complete portfolio of content, brands and franchises across television, film, sports, news, streaming and gaming. We're home to the world’s best storytellers, creating world-class products for consumers",
        'hiring_needs': 'Production Assistant, for a TV production set in Los Angeles in June 2025',
        'specific_benefits':'Weekly Pay, Employee Meals, healthcare',
    }
    try:
        JobPostingCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

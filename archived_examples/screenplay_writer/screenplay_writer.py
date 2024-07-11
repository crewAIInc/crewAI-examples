'''
Example script to automatically write a screenplay from a newsgroup post using agents with Crew.ai (https://github.com/joaomdmoura/crewAI)
You can also try it out with a personal email with many replies back and forth and see it turn into a movie script.
Demonstrates:
- multiple API endpoints (offical Mistral, Together.ai, Anyscale)
- running single tasks: spam detection and scoring
- running a crew to create a screenplay from a newsgroup post by first analyzing the text, creating a dialogue and ultimately formatting it
Additional endpoints requirements:
  pip install langchain_mistralai
  pip install langchain-together
Author: Toon Beerten (toon@neontreebot.be)
License: MIT
'''
import os
import re
from crewai import Agent, Task, Crew, Process
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chat_models import openai
#endpoint specific imports
import langchain_mistralai
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.llms import Together
from langchain_community.chat_models import ChatAnyscale


## Choose here which API endpoint to use, uncomment only one:
# Official Mistral: benefit of having access to mistral-medium
# Together.ai: lots of models to choose from
# Anyscale: cheapest at the time of writing
#endpoint = 'mistral_official'
#endpoint = 'togetherai'
endpoint = 'mistral_official'

#put you API keys here
mistral_key = ''
togetherai_key = ''
anyscale_key = ''

#model choice: i already have good results with mistralai/Mistral-7B-Instruct-v0.2

if endpoint == 'mistral_official':
  mixtral=ChatMistralAI(mistral_api_key=mistral_key, model="mistral-tiny",temperature=0.6)
elif endpoint == 'togetherai':
  #i get timeouts using Together() , so i use ChatOpenAI() instead
  #mixtral = Together(model="mistralai/Mistral-7B-Instruct-v0.2", together_api_key=togetherai_key ) #or mistralai/Mixtral-8x7B-Instruct-v0.1
  mixtral= openai.ChatOpenAI(base_url="https://api.together.xyz/v1", api_key=togetherai_key, temperature=0.5,  model="mistralai/Mistral-7B-Instruct-v0.2")
elif endpoint == 'anyscale':
  mixtral = ChatAnyscale(model='mistralai/Mistral-7B-Instruct-v0.1',  api_key=anyscale_key,  streaming=False)
 

## Define Agents
spamfilter = Agent(
  role='spamfilter',
  goal='''Decide whether a text is spam or not.''',
  backstory='You are an expert spam filter with years of experience. You DETEST advertisements, newsletters and vulgar language.',
  llm=mixtral,
  verbose=True,
  allow_delegation=False
)

analyst = Agent(
  role='analyse',
  goal='''You will distill all arguments from all discussion members. Identify who said what. You can reword what they said as long as the main discussion points remain.''',
  backstory='You are an expert discussion analyst.',
  llm=mixtral,
  verbose=True,
  allow_delegation=False
)

scriptwriter = Agent(
  role='scriptwriter',
  goal='Turn a conversation into a movie script. Only write the dialogue parts. Do not start the sentence with an action. Do not specify situational descriptions. Do not write parentheticals.',
  backstory='''You are an expert on writing natural sounding movie script dialogues. You only focus on the text part and you HATE directional notes.''',
  llm=mixtral,
  verbose=True,
  allow_delegation=False

)

formatter = Agent(
  role='formatter',
  goal='''Format the text as asked. Leave out actions from discussion members that happen between brackets, eg (smiling).''',
  backstory='You are an expert text formatter.',
  llm=mixtral,
  verbose=True,
  allow_delegation=False
)

scorer = Agent(
  role='scorer',
  goal='''You score a dialogue assessing various aspects of the exchange between the participants using a 1-10 scale, where 1 is the lowest performance and 10 is the highest:
  Scale:
  1-3: Poor - The dialogue has significant issues that prevent effective communication.
  4-6: Average - The dialogue has some good points but also has notable weaknesses.
  7-9: Good - The dialogue is mostly effective with minor issues.
  10: Excellent - The dialogue is exemplary in achieving its purpose with no apparent issues.
  Factors to Consider:
  Clarity: How clear is the exchange? Are the statements and responses easy to understand?
  Relevance: Do the responses stay on topic and contribute to the conversation's purpose?
  Conciseness: Is the dialogue free of unnecessary information or redundancy?
  Politeness: Are the participants respectful and considerate in their interaction?
  Engagement: Do the participants seem interested and actively involved in the dialogue?
  Flow: Is there a natural progression of ideas and responses? Are there awkward pauses or interruptions?
  Coherence: Does the dialogue make logical sense as a whole?
  Responsiveness: Do the participants address each other's points adequately?
  Language Use: Is the grammar, vocabulary, and syntax appropriate for the context of the dialogue?
  Emotional Intelligence: Are the participants aware of and sensitive to the emotional tone of the dialogue?
  ''',
  backstory='You are an expert at scoring conversations on a scale of 1 to 10.',
  llm=mixtral,
  verbose=True,
  allow_delegation=False
)


#this is one example of a public post in the newsgroup alt.atheism
#try it out yourself by replacing this with your own email thread or text or ...
discussion = '''From: keith@cco.caltech.edu (Keith Allan Schneider)
Subject: Re: <Political Atheists?
Organization: California Institute of Technology, Pasadena
Lines: 50
NNTP-Posting-Host: punisher.caltech.edu

bobbe@vice.ICO.TEK.COM (Robert Beauchaine) writes:

>>I think that about 70% (or so) people approve of the
>>death penalty, even realizing all of its shortcomings.  Doesn't this make
>>it reasonable?  Or are *you* the sole judge of reasonability?
>Aside from revenge, what merits do you find in capital punishment?

Are we talking about me, or the majority of the people that support it?
Anyway, I think that "revenge" or "fairness" is why most people are in
favor of the punishment.  If a murderer is going to be punished, people
that think that he should "get what he deserves."  Most people wouldn't
think it would be fair for the murderer to live, while his victim died.

>Revenge?  Petty and pathetic.

Perhaps you think that it is petty and pathetic, but your views are in the
minority.

>We have a local televised hot topic talk show that very recently
>did a segment on capital punishment.  Each and every advocate of
>the use of this portion of our system of "jurisprudence" cited the
>main reason for supporting it:  "That bastard deserved it".  True
>human compassion, forgiveness, and sympathy.

Where are we required to have compassion, forgiveness, and sympathy?  If
someone wrongs me, I will take great lengths to make sure that his advantage
is removed, or a similar situation is forced upon him.  If someone kills
another, then we can apply the golden rule and kill this person in turn.
Is not our entire moral system based on such a concept?

Or, are you stating that human life is sacred, somehow, and that it should
never be violated?  This would sound like some sort of religious view.
 
>>I mean, how reasonable is imprisonment, really, when you think about it?
>>Sure, the person could be released if found innocent, but you still
>>can't undo the imiprisonment that was served.  Perhaps we shouldn't
>>imprision people if we could watch them closely instead.  The cost would
>>probably be similar, especially if we just implanted some sort of
>>electronic device.
>Would you rather be alive in prison or dead in the chair?  

Once a criminal has committed a murder, his desires are irrelevant.

And, you still have not answered my question.  If you are concerned about
the death penalty due to the possibility of the execution of an innocent,
then why isn't this same concern shared with imprisonment.  Shouldn't we,
by your logic, administer as minimum as punishment as possible, to avoid
violating the liberty or happiness of an innocent person?

keith
'''

# Filter out spam and vulgar posts
task0 = Task(description='Read the following newsgroup post. If this contains vulgar language reply with STOP . If this is spam reply with STOP.\n### NEWGROUP POST:\n' + discussion, agent=spamfilter)
result = task0.execute()
if "STOP" in result:
    #stop here and proceed to next post
    print('This spam message will be filtered out')

# process post with a crew of agents, ultimately delivering a well formatted dialogue
task1 = Task(description='Analyse in much detail the following discussion:\n### DISCUSSION:\n' + discussion, agent=analyst)
task2 = Task(description='Create a dialogue heavy screenplay from the discussion, between two persons. Do NOT write parentheticals. Leave out wrylies. You MUST SKIP directional notes.', agent=scriptwriter)
task3 = Task(description='''Format the script exactly like this:
  ## (person 1):
  (first text line from person 1)
             
  ## (person 2):
  (first text line from person 2)
             
  ## (person 1):
  (second text line from person 1)
             
  ## (person 2):
  (second text line from person 2)
  
  ''', agent=formatter)
crew = Crew(
  agents=[analyst, scriptwriter,formatter],
  tasks=[task1, task2, task3],
  verbose=2, # Crew verbose more will let you know what tasks are being worked on, you can set it to 1 or 2 to different logging levels
  process=Process.sequential # Sequential process will have tasks executed one after the other and the outcome of the previous one is passed as extra content into this next.
)
result = crew.kickoff()

#get rid of directions and actions between brackets, eg: (smiling)
result = re.sub(r'\(.*?\)', '', result)

print('===================== end result from crew ===================================')
print(result)
print('===================== score ==================================================')
task4 = Task(description='Read the following dialogue. Then score the script on a scale of 1 to 10. Only give the score as a number, nothing else. Do not give an explanation.\n'+result, agent=scorer)
score = task4.execute()
score = score.split('\n')[0]  #sometimes an explanation comes after score, ignore
print(f'Scoring the dialogue as: {score}/10')
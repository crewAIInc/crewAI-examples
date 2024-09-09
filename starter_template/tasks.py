from crewai import Task
from textwrap import dedent

class ScriptTasks:
    def select_background(self, agent, background_list):
        return Task(description=dedent(f"""
            Carefully review the provided background list and select the 
            most suitable backgrounds for the script's scenes.
            Make sure that each background complements the emotional tone 
            of the characters and the storyline, and enhances the narrative.

            Pay special attention to how the background can influence 
            character interactions and help set the mood for key moments in 
            the script.

            Your final decision must be a detailed report explaining why you 
            selected each background for the respective scenes.

            Background options: {', '.join(background_list)}
        """),
        agent=agent
        )

    def select_characters(self, agent, character_list):
        return Task(description=dedent(f"""
            Analyze the provided character list and select the characters 
            that best fit the storyline and emotional progression of the script.

            You should take into account character relationships, conflicts, 
            and how their personalities contribute to the story's arc.

            Your final answer MUST include a justification for each character 
            selected, explaining how they drive the plot and why their traits 
            align with the story’s themes.

            Character options: {', '.join([char['name'] for char in character_list])}
        """),
        agent=agent
        )

    def create_storyline(self, agent, characters):
        return Task(description=dedent(f"""
            Using the selected characters, create a compelling storyline 
            that ties together their individual arcs and interactions. The 
            storyline should have a clear beginning, middle, and end, and should 
            focus on the emotional journey of the characters.

            Make sure the plot feels cohesive and logical, with a central conflict 
            that is resolved by the end.

            Your final answer MUST include a brief outline of the main plot points, 
            character interactions, and how the selected backgrounds and settings 
            will influence the scenes.

            Selected characters: {', '.join(characters.keys())}
        """),
        agent=agent
        )

    def write_dialogue(self, agent, storyline, characters, background):
        return Task(description=dedent(f"""
            Write engaging and realistic dialogues that reflect the personalities 
            and emotional states of the selected characters. The dialogue should 
            also consider the selected background and setting for each scene, and 
            the progression of the storyline.

            Focus on making the conversations feel natural, while driving the plot 
            forward and revealing key character emotions.

            Your final answer MUST include dialogue for each scene along with actions 
            and expressions that fit the tone of the scenes.

            Storyline: {storyline}
            Characters: {', '.join(characters.keys())}
            Background: {background}
        """),
        agent=agent
        )

    def oversee_script(self, agent, storyline, dialogue):
        return Task(description=dedent(f"""
            As the director, your task is to review the entire script, including 
            the storyline and dialogues. Ensure that the tone, pacing, and character 
            arcs are consistent throughout the script.

            Look for any plot holes or inconsistencies, and provide feedback to 
            ensure that the script flows smoothly. Make sure the selected backgrounds, 
            characters, and actions align well with the overall vision.

            Your final output MUST be a cohesive script that reflects a well-rounded 
            and engaging narrative with all parts working in harmony.

            Storyline: {storyline}
            Dialogue: {dialogue}
        """),
        agent=agent
        )

    def __tip_section(self):
        return "If you deliver an excellent script, your team will receive accolades and recognition!"

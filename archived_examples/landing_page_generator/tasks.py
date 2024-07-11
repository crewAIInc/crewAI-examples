from textwrap import dedent


class TaskPrompts():
  def expand():
    return dedent("""
      THIS IS A GREAT IDEA! Analyze and expand it 
      by conducting a comprehensive research.
  
      Final answer MUST be a comprehensive idea report 
      detailing why this is a great idea, the value 
      proposition, unique selling points, why people should 
      care about it and distinguishing features. 
  
       IDEA: 
      ----------
      {idea}
    """)

  def refine_idea():
    return dedent("""
      Expand idea report with a Why, How, and What 
      messaging strategy using the Golden Circle 
      Communication technique, based on the idea report.
      
      Your final answer MUST be the updated complete 
      comprehensive idea report with WHY, HOW, WHAT, 
      a core message, key features and supporting arguments.
      
      YOU MUST RETURN THE COMPLETE IDEA REPORT AND 
      THE DETAILS, You'll get a $100 tip if you do your best work!
    """)

  def choose_template():
    return dedent("""
      Learn the templates options choose and copy 
      the one that suits the idea bellow the best, 
      YOU MUST COPY, and then YOU MUST read the src/component 
      in the directory you just copied, to decide what 
      component files should be updated to make the 
      landing page about the idea bellow.
      
      - YOU MUST READ THE DIRECTORY BEFORE CHOOSING THE FILES.      
      - YOU MUST NOT UPDATE any Pricing components.
      - YOU MUST UPDATE ONLY the 4 most important components.
      
      Your final answer MUST be ONLY a JSON array of 
      components full file paths that need to be updated.

      IDEA 
      ----------
      {idea}
    """)

  def update_page():
    return dedent("""
      READ the ./[chosen_template]/src/app/page.jsx OR
      ./[chosen_template]/src/app/(main)/page.jsx (main with the parenthesis) 
      to learn its content and then write an updated 
      version to the filesystem that removes any 
      section related components that are not in our 
      list from the returns. Keep the imports.
      
      Final answer MUST BE ONLY a valid json list with 
      the full path of each of the components we will be 
      using, the same way you got them.

      RULES
      -----
      - NEVER ADD A FINAL DOT to the file content.
      - NEVER WRITE \\n (newlines as string) on the file, just the code.
      - NEVER FORGET TO CLOSE THE FINAL BRACKET (}}) in the file.
      - NEVER USE COMPONENTS THAT ARE NOT IMPORTED.
      - ALL COMPONENTS USED SHOULD BE IMPORTED, don't make up components.
      - Save the file as with `.jsx` extension.
      - Return the same valid JSON list of the components your got.

      You'll get a $100 tip if you follow all the rules!

      Also update any necessary text to reflect this landing page
      is about the idea bellow.
      
      IDEA 
      ----------
      {idea}
    """)

  def component_content():
    return dedent("""
      A engineer will update the {component} (code bellow),
      return a list of good options of texts to replace 
      EACH INDIVIDUAL existing text on the component, 
      the suggestion MUST be based on the idea bellow, 
      and also MUST be similar in length with the original 
      text, we need to replace ALL TEXT.
      
      NEVER USE Apostrophes for contraction! You'll get a $100 
      tip if you do your best work!

      IDEA 
      -----
      {expanded_idea}
  
      REACT COMPONENT CONTENT
      -----
      {file_content}
    """)

  def update_component():
    return dedent("""
      YOU MUST USE the tool to write an updated 
      version of the react component to the file 
      system in the following path: {component} 
      replacing the text content with the suggestions 
      provided.
      
      You only modify the text content, you don't add 
      or remove any components.
      
      You first write the file then your final answer 
      MUST be the updated component content.

      RULES
      -----
      - Remove all the links, this should be single page landing page.
      - Don't make up images, videos, gifs, icons, logos, etc.
      - keep the same style and tailwind classes.
      - MUST HAVE `'use client'` at the be beginning of the code.
      - href in buttons, links, NavLinks, and navigations should be `#`.
      - NEVER WRITE \\n (newlines as string) on the file, just the code.
      - NEVER FORGET TO CLOSE THE FINAL BRACKET (}}) in the file.
      - Keep the same component imports and don't use new components.
      - NEVER USE COMPONENTS THAT ARE NOT IMPORTED.
      - ALL COMPONENTS USED SHOULD BE IMPORTED, don't make up components.
      - Save the file as with `.jsx` extension.

      If you follow the rules I'll give you a $100 tip!!! 
      MY LIFE DEPEND ON YOU FOLLOWING IT!
  
      CONTENT TO BE UPDATED
      -----
      {file_content}
    """)

  def qa_component():
    return dedent("""
      Check the React component code to make sure 
      it's valid and abide by the rules bellow, 
      if it doesn't then write the correct version to 
      the file system using the write file tool into 
      the following path: {component}.
    
      Your final answer should be a confirmation that 
      the component is valid and abides by the rules and if
      you had to write an updated version to the file system.

      RULES
      -----
      - NEVER USE Apostrophes for contraction!
      - ALL COMPONENTS USED SHOULD BE IMPORTED.
      - MUST HAVE `'use client'` at the be beginning of the code.
      - href in buttons, links, NavLinks, and navigations should be `#`.
      - NEVER WRITE \\n (newlines as string) on the file, just the code.
      - NEVER FORGET TO CLOSE THE FINAL BRACKET (}}) in the file.
      - NEVER USE COMPONENTS THAT ARE NOT IMPORTED.
      - ALL COMPONENTS USED SHOULD BE IMPORTED, don't make up components.
      - Always use `export function` for the component class.

      You'll get a $100 tip if you follow all the rules!
    """)

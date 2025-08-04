import os
import shutil
from textwrap import dedent

from crew import LandingPageCrew


if __name__ == "__main__":
  print("Welcome to Idea Generator")
  print(dedent("""
  ! YOU MUST FORK THIS BEFORE USING IT !
  """))

  print(dedent("""
      Disclaimer: This will use gpt-4 unless you changed it 
      not to, and by doing so it will cost you money (~2-9 USD).
      The full run might take around ~10-45m. Enjoy your time back.\n\n
    """
  ))
  idea = input("# Describe what is your idea:\n\n")
  
  if not os.path.exists("./workdir"):
    os.mkdir("./workdir")

  if len(os.listdir("./templates")) == 0:
    print(
      dedent("""
      !!! NO TEMPLATES FOUND !!!
      ! YOU MUST FORK THIS BEFORE USING IT !
      
      Templates are not included as they are Tailwind templates. 
      Place Tailwind individual template folders in `./templates`, 
      if you have a license you can download them at
      https://tailwindui.com/templates, their references are at
      `config/templates.json`.
      
      This was not tested this with other templates, 
      prompts in `tasks.py` might require some changes 
      for that to work.
      
      !!! STOPPING EXECUTION !!!
      """)
    )
    exit()

  crew = LandingPageCrew(idea)
  crew.run()
  zip_file = "workdir"
  shutil.make_archive(zip_file, 'zip', 'workdir')
  shutil.rmtree('workdir')
  print("\n\n")
  print("==========================================")
  print("DONE!")
  print(f"You can download the project at ./{zip_file}.zip")
  print("==========================================")

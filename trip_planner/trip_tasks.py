from crewai import Task
from textwrap import dedent
from datetime import date


class TripTasks():

  def identify_task(self, agent, origin, cities, interests, range):
    return Task(description=dedent(f"""
      Analyze and select the best city for the trip based 
      on specific criteria such as weather patterns, seasonal
      events, and travel costs. This task involves comparing
      multiple cities, considering factors like current weather
      conditions, upcoming cultural or seasonal events, and
      overall travel expenses. 

      Your final answer must be a detailed
      report on the chosen city, and everything you found out
      about it, including the actual flight costs, weather 
      forecast and attractions.
      {self.__tip_section()}

      Traveling from: {origin}
      City Options: {cities}
      Trip Date: {range}
      Traveler Interests: {interests}
      """
),
      expected_output =f"""
      After careful analysis and consideration of your preferences and requirements, 
      I have selected Paris as the best city for your upcoming trip. Here are the details:

      Flight Costs:
      - Round-trip ticket from {origin} to Paris: $500
      - Estimated accommodation cost: $100 per night

      Weather Forecast:
      - Average temperature during your trip: 18°C (64°F)
      - Mostly sunny with occasional clouds

      Attractions:
      1. Eiffel Tower: A must-visit iconic landmark offering breathtaking views of the city.
      2. Louvre Museum: Home to thousands of works of art, including the Mona Lisa.
      3. Notre-Dame Cathedral: A masterpiece of French Gothic architecture.

      Cultural Events:
      - Paris Fashion Week: Scheduled during your trip dates, offering a glimpse into the latest trends in fashion.

      Feel free to make any necessary changes to this structure.
      """,
      agent = agent, 
      async_execution = False

    )

  def gather_task(self, agent, origin, interests, range, context):
    return Task(description=dedent(f"""
        As a local expert on this city, you must compile an 
        in-depth guide for someone traveling there and wanting 
        to have THE BEST trip ever!
        Gather information about key attractions, local customs,
        special events, and daily activity recommendations.
        Find the best spots to go to, the kind of place only a
        local would know.
        This guide should provide a thorough overview of what 
        the city has to offer, including hidden gems, cultural
        hotspots, must-visit landmarks, weather forecasts, and
        high-level costs.

        The final answer must be a comprehensive city guide, 
        rich in cultural insights and practical tips, 
        tailored to enhance the travel experience.
        {self.__tip_section()}

        Trip Date: {range}
        Traveling from: {origin}
        Traveler Interests: {interests}
        """
        ),
        expected_output=f"""
          Key Attractions:
        - Eiffel Tower: Iconic landmark offering stunning views of the city.
        - Louvre Museum: Home to famous works of art like the Mona Lisa.
        - Notre-Dame Cathedral: Magnificent example of French Gothic architecture.

        Local Customs:
        - Embrace the French greeting of kissing on the cheeks.
        - Respect dining etiquette, such as keeping your hands on the table.

        Special Events:
        - Bastille Day Parade: Experience French national pride on July 14th.
        - Paris Fashion Week: Witness the latest trends in fashion.

        Daily Activity Recommendations:
        - Morning: Enjoy a croissant and coffee at a local café.
        - Afternoon: Explore the charming streets of Montmartre.
        - Evening: Indulge in a gourmet dinner overlooking the Seine River.

        Best Spots:
        - Le Marais: Discover trendy boutiques and cozy cafés.
        - Canal Saint-Martin: Relax by the water with a picnic.

        Hidden Gems:
        - Shakespeare and Company Bookstore: Literary haven near Notre-Dame.

        Weather Forecast:
        - Average temperature during your trip: 20°C (68°F)
        - Mostly sunny with occasional showers.

        High-Level Costs:
        - Accommodation: $150 per night (average)
        - Dining: $30-$50 per meal (average)

        Feel free to make any necessary changes to this structure.
        """,
        agent=agent,
        context = context,
        async_execution=False)

  def plan_task(self, agent, origin, interests, range, context):
    return Task(description=dedent(f"""
          Expand this guide into a full 7-day travel itinerary with detailed
          per-day plans including weather forecasts, places to eat, packing suggestions
          and a budget breakdown.

          You MUST suggest actual places to visit, actual hotels to stay
          and actual restaurants to go to.

          This itinerary should cover all aspects of the trip,
          from arrival to departure, integrating the city guide information with
          practical travel logistics.

          Your final answer MUST be a complete expanded travel plan, formatted as
          markdown, encompassing a daily schedule, anticipated weather conditions, recommended clothings
          items to pack, and a detailed budget ensuring THE BEST TRIP EVER. Be specific
          and give reasons why you picked a specific place, what makes the place special.

          {self.__tip_selection()}

          Trip Date: {range}
          Traveling from: {origin}
          Traveler Interests: {interests}
          """
          ),
          expected_output=f"""

        **Day 1: Arrival and Exploration**
        - Morning: Arrival at Charles de Gaulle Airport and transfer to Hotel Le Meurice.
        - Afternoon: Visit the iconic Eiffel Tower for panoramic views of Paris.
        - Evening: Enjoy a traditional French dinner at Le Relais de l'Entrecôte.

        **Weather Forecast:**
        - Average temperature: 22°C (72°F)
        - Sunny with clear skies

        **Packing Suggestions:**
        - Lightweight clothing, comfortable shoes
        - Camera for capturing breathtaking views

        **Budget Breakdown:**
        - Hotel: $250 per night
        - Dinner: $50 per person

        **Day 2: Cultural Immersion**
        - Morning: Breakfast at Café de Flore, a historic café frequented by artists and writers.
        - Afternoon: Explore the Louvre Museum, home to the famous Mona Lisa.
        - Evening: Attend a performance at the Palais Garnier, the renowned opera house.

        **Weather Forecast:**
        - Average temperature: 20°C (68°F)
        - Partly cloudy with a chance of light rain

        **Packing Suggestions:**
        - Umbrella, comfortable walking shoes
        - Dressier attire for the opera

        **Budget Breakdown:**
        - Breakfast: $20 per person
        - Museum entrance fee: $20 per person
        - Opera ticket: $100 per person

        **Total Cost Compilation per person
        - ####

        Feel free to make any necessary changes to this structure.
        """,
context = context,
agent=agent)

  def __tip_section(self):
    return "If you do your BEST WORK, I'll tip you $100!"

from flask import Flask, render_template_string
import os

app = Flask(__name__)

EXAMPLES = {
    "flows": [
        {
            "name": "Content Creator Flow",
            "path": "flows/content_creator_flow",
            "description": "Multi-crew content generation system for blogs, LinkedIn posts, and research reports.",
            "level": "Advanced",
        },
        {
            "name": "Email Auto Responder Flow",
            "path": "flows/email_auto_responder_flow",
            "description": "Automated email monitoring and response generation.",
            "level": "Intermediate",
        },
        {
            "name": "Lead Score Flow",
            "path": "flows/lead-score-flow",
            "description": "Lead qualification with human-in-the-loop review.",
            "level": "Advanced",
        },
        {
            "name": "Meeting Assistant Flow",
            "path": "flows/meeting_assistant_flow",
            "description": "Meeting notes processing with Trello/Slack integration.",
            "level": "Intermediate",
        },
        {
            "name": "Self Evaluation Loop Flow",
            "path": "flows/self_evaluation_loop_flow",
            "description": "Iterative content improvement with self-review.",
            "level": "Intermediate",
        },
        {
            "name": "Write a Book with Flows",
            "path": "flows/write_a_book_with_flows",
            "description": "Automated book writing with parallel chapter generation.",
            "level": "Advanced",
        },
    ],
    "crews": [
        {
            "name": "Game Builder Crew",
            "path": "crews/game-builder-crew",
            "description": "Multi-agent team that designs and builds Python games.",
            "level": "Intermediate",
        },
        {
            "name": "Instagram Post",
            "path": "crews/instagram_post",
            "description": "Creative social media content generation.",
            "level": "Beginner",
        },
        {
            "name": "Landing Page Generator",
            "path": "crews/landing_page_generator",
            "description": "Full landing page creation from concepts.",
            "level": "Intermediate",
        },
        {
            "name": "Marketing Strategy",
            "path": "crews/marketing_strategy",
            "description": "Comprehensive marketing campaign development.",
            "level": "Intermediate",
        },
        {
            "name": "Screenplay Writer",
            "path": "crews/screenplay_writer",
            "description": "Convert text/emails into screenplay format.",
            "level": "Beginner",
        },
        {
            "name": "Job Posting",
            "path": "crews/job-posting",
            "description": "Automated job description creation.",
            "level": "Beginner",
        },
        {
            "name": "Prep for a Meeting",
            "path": "crews/prep-for-a-meeting",
            "description": "Meeting preparation research and strategy.",
            "level": "Beginner",
        },
        {
            "name": "Recruitment",
            "path": "crews/recruitment",
            "description": "Automated candidate sourcing and evaluation.",
            "level": "Intermediate",
        },
        {
            "name": "Stock Analysis",
            "path": "crews/stock_analysis",
            "description": "Financial analysis with SEC data integration.",
            "level": "Intermediate",
        },
        {
            "name": "Industry Agents",
            "path": "crews/industry-agents",
            "description": "Industry-specific agent implementations.",
            "level": "Intermediate",
        },
        {
            "name": "Match Profile to Positions",
            "path": "crews/match_profile_to_positions",
            "description": "CV-to-job matching with vector search.",
            "level": "Advanced",
        },
        {
            "name": "Meta Quest Knowledge",
            "path": "crews/meta_quest_knowledge",
            "description": "PDF-based Q&A system.",
            "level": "Intermediate",
        },
        {
            "name": "Markdown Validator",
            "path": "crews/markdown_validator",
            "description": "Automated markdown validation and correction.",
            "level": "Beginner",
        },
        {
            "name": "Surprise Trip",
            "path": "crews/surprise_trip",
            "description": "Personalized surprise travel planning.",
            "level": "Beginner",
        },
        {
            "name": "Trip Planner",
            "path": "crews/trip_planner",
            "description": "Destination comparison and itinerary optimization.",
            "level": "Beginner",
        },
        {
            "name": "Starter Template",
            "path": "crews/starter_template",
            "description": "Basic template for new CrewAI projects.",
            "level": "Beginner",
        },
    ],
    "integrations": [
        {
            "name": "CrewAI-LangGraph",
            "path": "integrations/CrewAI-LangGraph",
            "description": "Integration with LangGraph framework.",
            "level": "Advanced",
        },
        {
            "name": "Azure Model",
            "path": "integrations/azure_model",
            "description": "Using CrewAI with Azure OpenAI.",
            "level": "Intermediate",
        },
        {
            "name": "NVIDIA Models",
            "path": "integrations/nvidia_models",
            "description": "Integration with NVIDIA's AI ecosystem.",
            "level": "Advanced",
        },
    ],
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CrewAI Full Examples</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0f0f0f;
      color: #e8e8e8;
      min-height: 100vh;
    }

    header {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      padding: 48px 24px 40px;
      text-align: center;
      border-bottom: 1px solid #ffffff10;
    }

    .logo {
      font-size: 2.8rem;
      font-weight: 800;
      letter-spacing: -1px;
      background: linear-gradient(90deg, #e94560, #f5a623);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    header p {
      margin-top: 10px;
      font-size: 1.05rem;
      color: #a0a0b0;
      max-width: 560px;
      margin-left: auto;
      margin-right: auto;
    }

    .badge-row {
      margin-top: 20px;
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
    }

    .badge {
      background: #ffffff12;
      border: 1px solid #ffffff18;
      border-radius: 20px;
      padding: 4px 14px;
      font-size: 0.8rem;
      color: #c0c0d0;
    }

    main {
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 24px 60px;
    }

    .section-title {
      font-size: 1.4rem;
      font-weight: 700;
      margin-bottom: 20px;
      margin-top: 40px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #f0f0f0;
    }

    .section-title:first-child { margin-top: 0; }

    .section-title .icon { font-size: 1.3rem; }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }

    .card {
      background: #1a1a2a;
      border: 1px solid #ffffff10;
      border-radius: 12px;
      padding: 20px;
      transition: border-color 0.2s, transform 0.2s;
    }

    .card:hover {
      border-color: #e94560a0;
      transform: translateY(-2px);
    }

    .card-name {
      font-size: 1rem;
      font-weight: 600;
      color: #f0f0f0;
      margin-bottom: 8px;
    }

    .card-desc {
      font-size: 0.87rem;
      color: #909090;
      line-height: 1.5;
    }

    .card-footer {
      margin-top: 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .level {
      font-size: 0.75rem;
      padding: 3px 10px;
      border-radius: 20px;
      font-weight: 600;
    }

    .level-Beginner     { background: #1a3a1a; color: #4caf50; border: 1px solid #4caf5040; }
    .level-Intermediate { background: #2a2a1a; color: #f5a623; border: 1px solid #f5a62340; }
    .level-Advanced     { background: #2a1a1a; color: #e94560; border: 1px solid #e9456040; }

    .card-path {
      font-size: 0.72rem;
      color: #505060;
      font-family: monospace;
    }

    .stats {
      display: flex;
      gap: 24px;
      justify-content: center;
      margin-top: 24px;
      flex-wrap: wrap;
    }

    .stat {
      text-align: center;
    }

    .stat-num {
      font-size: 2rem;
      font-weight: 800;
      background: linear-gradient(90deg, #e94560, #f5a623);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .stat-label {
      font-size: 0.8rem;
      color: #707080;
      margin-top: 2px;
    }

    footer {
      text-align: center;
      padding: 24px;
      border-top: 1px solid #ffffff08;
      color: #404050;
      font-size: 0.82rem;
    }

    footer a { color: #e94560; text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header>
    <div class="logo">CrewAI Full Examples</div>
    <p>A comprehensive collection of production-ready applications built with the CrewAI framework for orchestrating autonomous AI agents.</p>
    <div class="badge-row">
      <span class="badge">CrewAI v0.152.0</span>
      <span class="badge">Python 3.10–3.12</span>
      <span class="badge">uv package manager</span>
    </div>
    <div class="stats">
      <div class="stat">
        <div class="stat-num">{{ flows|length }}</div>
        <div class="stat-label">Flows</div>
      </div>
      <div class="stat">
        <div class="stat-num">{{ crews|length }}</div>
        <div class="stat-label">Crews</div>
      </div>
      <div class="stat">
        <div class="stat-num">{{ integrations|length }}</div>
        <div class="stat-label">Integrations</div>
      </div>
    </div>
  </header>

  <main>
    <div class="section-title"><span class="icon">🌊</span> Flows</div>
    <div class="grid">
      {% for ex in flows %}
      <div class="card">
        <div class="card-name">{{ ex.name }}</div>
        <div class="card-desc">{{ ex.description }}</div>
        <div class="card-footer">
          <span class="level level-{{ ex.level }}">{{ ex.level }}</span>
          <span class="card-path">{{ ex.path }}</span>
        </div>
      </div>
      {% endfor %}
    </div>

    <div class="section-title"><span class="icon">👥</span> Crews</div>
    <div class="grid">
      {% for ex in crews %}
      <div class="card">
        <div class="card-name">{{ ex.name }}</div>
        <div class="card-desc">{{ ex.description }}</div>
        <div class="card-footer">
          <span class="level level-{{ ex.level }}">{{ ex.level }}</span>
          <span class="card-path">{{ ex.path }}</span>
        </div>
      </div>
      {% endfor %}
    </div>

    <div class="section-title"><span class="icon">🔌</span> Integrations</div>
    <div class="grid">
      {% for ex in integrations %}
      <div class="card">
        <div class="card-name">{{ ex.name }}</div>
        <div class="card-desc">{{ ex.description }}</div>
        <div class="card-footer">
          <span class="level level-{{ ex.level }}">{{ ex.level }}</span>
          <span class="card-path">{{ ex.path }}</span>
        </div>
      </div>
      {% endfor %}
    </div>
  </main>

  <footer>
    Built with <a href="https://github.com/crewAIInc/crewAI" target="_blank">CrewAI</a> &mdash;
    <a href="https://docs.crewai.com" target="_blank">Documentation</a> &mdash;
    <a href="https://github.com/crewAIInc/crewAI-examples" target="_blank">GitHub</a>
  </footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        flows=EXAMPLES["flows"],
        crews=EXAMPLES["crews"],
        integrations=EXAMPLES["integrations"],
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

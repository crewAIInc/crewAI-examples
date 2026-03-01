# AI-Powered Study Planning Assistant

An intelligent study planning assistant built using CrewAI that helps students create personalized study plans for their exams. The system uses natural language processing to understand exam requirements and generates comprehensive study plans with schedules, strategies, and learning resources.

## 🚀 Features

### 1. Natural Language Input Processing
- Accepts exam information in natural language
- Extracts key details like:
  - Subject
  - Exam date
  - Topics to study
  - Time available for preparation

### 2. Intelligent Study Planning
- Creates day-wise study schedules
- Distributes topics evenly across available days
- Considers topic complexity and importance
- Adapts to different timeframes

### 3. Study Strategy Generation
- Provides topic-specific study strategies
- Includes memory techniques
- Suggests practice methods
- Recommends review schedules

### 4. Learning Resource Curation
- Finds relevant YouTube educational videos
- Filters for high-quality educational content
- Provides direct video links with descriptions
- Focuses on reputable educational channels

### 5. Markdown Output
- Generates well-formatted study plans
- Includes all sections in a readable format
- Easy to print or share digitally
- Compatible with markdown viewers

## 🛠️ Technical Architecture

### Core Components

1. **Input Interpreter Agent**
   - Processes natural language input
   - Extracts exam information
   - Validates and structures the data

2. **Schedule Builder Agent**
   - Creates time-based study plans
   - Optimizes topic distribution
   - Considers study duration

3. **Strategy Planner Agent**
   - Develops study strategies
   - Suggests learning techniques
   - Provides memory aids

4. **YouTube Fetcher Agent**
   - Searches for educational videos
   - Filters content quality
   - Provides direct video links

5. **Output Formatter Agent**
   - Structures the final output
   - Creates markdown formatting
   - Ensures readability

### Tools and Technologies

- **CrewAI**: Framework for orchestrating role-playing AI agents
- **YouTube Data API**: For fetching educational videos
- **Python**: Core programming language
- **Markdown**: Output format
- **Environment Variables**: For API key management

## 📋 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Exam_Prep_Agent.git
   cd Exam_Prep_Agent
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Unix/MacOS
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e .
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

## 💻 Usage

1. **Run the Program**
   ```bash
   python -m exam_prep.main
   ```

2. **Enter Exam Information**
   Example input:
   ```
   I have a test on statistics in 4 days. Topics are probability, distributions, and hypothesis testing.
   ```

3. **Get Your Study Plan**
   - The program will generate a study plan
   - Output will be saved as a markdown file
   - File will be stored in the `output` directory

## 📁 Project Structure

```
exam_prep/
├── src/
│   └── exam_prep/
│       ├── config/
│       │   ├── agents.yaml    # Agent configurations
│       │   └── tasks.yaml     # Task definitions
│       ├── tools/
│       │   └── youtube_tool.py # YouTube API integration
│       ├── main.py            # Entry point
│       └── crew.py            # CrewAI implementation
├── output/                    # Generated study plans
├── tests/                     # Test files
├── .env                       # Environment variables
└── README.md                  # Documentation
```

## 🔧 Configuration

### Agent Configuration (agents.yaml)
- Defines agent roles and goals
- Sets up agent behaviors
- Configures tool usage

### Task Configuration (tasks.yaml)
- Defines task descriptions
- Sets expected outputs
- Links tasks to agents

## 📄 Output Format

The generated study plan includes:

1. **Exam Overview**
   - Subject
   - Date
   - Topics

2. **Study Schedule**
   - Day-by-day breakdown
   - Topic distribution
   - Time allocation

3. **Study Strategies**
   - Topic-specific approaches
   - Learning techniques
   - Practice methods

4. **Learning Resources**
   - YouTube video links
   - Channel information
   - Video descriptions

## 🔐 Security

- API keys are stored in `.env` file
- Sensitive files are git-ignored
- No hardcoded credentials

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CrewAI framework
- YouTube Data API
- Python community
- Open source contributors

## 🔄 Future Improvements

1. Add more learning resources
2. Implement spaced repetition
3. Add progress tracking
4. Support multiple languages
5. Add mobile interface
# Installing agentspec and its adapters from source
git clone https://github.com/oracle/agent-spec.git
cd agent-spec

# temporary workaround:
# using vllm models, pending support for openai models in the agentspec crewai adapter
git reset --hard 39e779d

pip install -e pyagentspec
pip install -e adapters/crewaiagentspecadapter
pip install -e adapters/langgraphagentspecadapter

# temporary workaround:
# installing crewai from source to pick up the agentspec adapter
cd ..
# git clone https://github.com/crewAIInc/crewAI.git
git clone https://github.com/gojkoc54/crewAI.git
cd crewAI
git checkout feat/agentspec-adapter
pip install -e lib/crewai

# Ollama Configuration Repository
This repository helps you get started with setting up and configuring Ollama. Please find below the steps for successful completion:

## Steps:
### 1. Install Ollama
   **For Ubuntu**: Use the following command in your terminal:
curl -fsSL https://ollama.com/install.sh | sh

   **For Windows and MacOS**: Please refer the following link:
https://ollama.com/download

### 2. Start Server
   Enter the following command to see how to start the server:
ollama --help

   Usually, the server can be started using:
ollama serve

   or
ollama start


### 3. Model Configuration
   Create a `Modelfile` for each of the models you are using. The `Modelfile` helps to configure the system message.

### 4. Modelname Crewai setup
   Run the `<modelname>_crewai_setup.sh` file using the following command:
chmod +x `<filename>`

   Here, replace `<filename>` with the name of your setup file.

For any issues, you can view the [documentation](https://ollama.com/docs) or open a GitHub issue in this repository.
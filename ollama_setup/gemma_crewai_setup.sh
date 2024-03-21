#!/bin/bash

# Variables
model_name="gemma"
custom_model_name="crewai-gemma"

# Get the base model
ollama pull $model_name

# Create the model file
ollama create $custom_model_name -f ./gemmaModelfile

# enter "chmod +x <filename>" to make file executable
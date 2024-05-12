#!/bin/bash

# Variables
model_name="mistral"
custom_model_name="crewai-mistral"

# Get the base model
ollama pull $model_name

# Create the model file
ollama create $custom_model_name -f ./mistralModelfile

# enter "chmod +x <filename>" to make file executable
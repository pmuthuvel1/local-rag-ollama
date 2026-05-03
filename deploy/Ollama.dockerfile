FROM ollama/ollama:latest

# Pre-load the llama2 model into the image
# This ensures the model is available without requiring internet access
RUN ollama serve &
RUN sleep 10
RUN ollama pull llama2

# Ensure ollama runs on startup
ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]

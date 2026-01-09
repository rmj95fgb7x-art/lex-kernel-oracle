# Use a slim Python base to keep SWaP-C low (Small Weight and Power)
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements first (optimizes Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Lex Kernel Oracle system
COPY . .

# Set environment variables so Python can find your /core and /kernels
ENV PYTHONPATH="/app"

# Command to generate the registry and then start the orchestrator
# This ensures the 90+ kernels are always indexed on boot
CMD python core/registry_gen.py && python core/orchestrator.py

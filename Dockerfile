# 1. Start from an official Python base image
# We use "slim" because it's a smaller, more production-friendly image
FROM python:3.9-slim

# 2. Set the working directory inside the container
# This is where our app's code will live
WORKDIR /app

# 3. Copy the requirements file *first* and install dependencies
# This is a key optimization. Docker layers are cached.
# As long as requirements.txt doesn't change, Docker won't
# re-install all the packages every time you change your .py file.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code into the container
# This copies ACEest_Fitness.py, test_app.py, etc., into /app
COPY . .

# 5. Expose the port that Flask runs on
# This tells Docker that the container will listen on port 5000
EXPOSE 5000

# 6. Define the command to run when the container starts
# This is the same as running "python ACEest_Fitness.py"
# We use gunicorn here as it's a production-grade web server,
# which is better than Flask's built-in development server.
# We'll add gunicorn to requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "ACEest_Fitness:app"]
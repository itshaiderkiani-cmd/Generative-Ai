# AI Documentation Generator

A simple web application that generates documentation for code snippets using OpenAI's GPT-3.5 API.

## Setup Instructions

### Step 1: Install Python
If you haven't already, download and install Python from [python.org](https://python.org)

### Step 2: Set Up Your Environment

1. Open your terminal/command prompt
2. Navigate to the project directory
3. Install the required packages by running:
```
pip install -r requirements.txt
```

### Step 3: Run the Application

1. Open your terminal/command prompt
2. Navigate to the project directory
3. Run the Flask application:
```
````markdown
# AI Documentation Generator

A simple web application that generates documentation for code snippets using OpenAI's GPT-3.5 API.

## Setup Instructions

### Step 1: Install Python
If you haven't already, download and install Python from [python.org](https://python.org)

### Step 2: Set Up Your Environment

1. Open your terminal/command prompt
2. Navigate to the project directory
3. Install the required packages by running:
```
pip install -r requirements.txt
```

### Step 3: Run the Application

1. Open your terminal/command prompt
2. Navigate to the project directory
3. Run the Flask application:
```
python app.py
```
4. Open your web browser and go to: http://127.0.0.1:5000

### Step 4: Using the Application

1. Paste your code into the text area
2. Click "Generate Documentation"
3. Wait for the AI to generate the documentation
4. The documentation will appear in the output section below

## Note
The OpenAI API key is already configured in the application. You can start using it right away!
````

## Docker image (GHCR)

The CI pipeline will build and publish a Docker image to GitHub Container Registry (GHCR) at the following example URL:

```
ghcr.io/itshaiderkiani-cmd/ci-cd-demo:latest
```

Replace `<your-github-username>` with your GitHub username. To pull and run the published image locally:

```powershell
docker pull ghcr.io/itshaiderkiani-cmd/ci-cd-demo:latest
docker run -p 5000:5000 ghcr.io/itshaiderkiani-cmd/ci-cd-demo:latest
```

Notes:
- The workflow uses the automatic `GITHUB_TOKEN` with `packages: write` permission to authenticate to GHCR. Make sure your repository's default branch is `main`, or update the workflow triggers.
- If you need to push to a different image name, update `.github/workflows/build-and-push.yml`.

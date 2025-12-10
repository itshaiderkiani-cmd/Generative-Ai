from flask import Flask, request, render_template, jsonify
import os
import requests
from typing import Optional

# Try to import OpenAI client if available (for sk- keys)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Initialize Flask app
app = Flask(__name__)


def call_huggingface(prompt: str, hf_key: str, model: str = "google/flan-t5-large") -> tuple[bool, str]:
    """Call Hugging Face Inference API for text generation.

    Returns (success, text_or_error).
    """
    # Use the Hugging Face Inference Router endpoint (replacement for api-inference)
    # New router URL required by Hugging Face: https://router.huggingface.co/hf-inference/{model}
    url = f"https://router.huggingface.co/hf-inference/{model}"
    headers = {"Authorization": f"Bearer {hf_key}", "Accept": "application/json"}
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True},
        "parameters": {"max_new_tokens": 512}
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
    except Exception as e:
        return False, f"Request error: {e}"

    if resp.status_code != 200:
        # If model not found (404), try a short list of fallback public models automatically
        if resp.status_code == 404:
            fallback_models = [
                "gpt2",
                "bigscience/bloom-560m",
                "facebook/opt-350m"
            ]
            # allow override from environment
            env_fallback = os.environ.get('HUGGINGFACE_FALLBACK_MODELS')
            if env_fallback:
                fallback_models = [m.strip() for m in env_fallback.split(',') if m.strip()]

            for fm in fallback_models:
                try:
                    resp2 = requests.post(f"https://router.huggingface.co/hf-inference/{fm}", headers=headers, json=payload, timeout=60)
                except Exception as e:
                    continue
                if resp2.status_code == 200:
                    try:
                        data2 = resp2.json()
                        if isinstance(data2, list) and len(data2) > 0 and 'generated_text' in data2[0]:
                            return True, data2[0]['generated_text']
                        if isinstance(data2, dict) and 'generated_text' in data2:
                            return True, data2['generated_text']
                        if isinstance(data2, dict) and 'choices' in data2 and len(data2['choices'])>0 and 'text' in data2['choices'][0]:
                            return True, data2['choices'][0]['text']
                        return True, str(data2)
                    except Exception:
                        return False, f"Parse error from fallback model {fm}"

        # Try to return helpful error
        try:
            return False, f"Error {resp.status_code}: {resp.json()}"
        except Exception:
            return False, f"Error {resp.status_code}: {resp.text}"

    try:
        data = resp.json()
        # many text-generation models return a list of dicts with 'generated_text'
        if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
            return True, data[0]['generated_text']
        # other models may return {'generated_text': '...'} or {'choices':[{'text': '...'}]}
        if isinstance(data, dict):
            if 'generated_text' in data:
                return True, data['generated_text']
            if 'error' in data:
                return False, f"HF error: {data['error']}"
            if 'choices' in data and len(data['choices']) > 0 and 'text' in data['choices'][0]:
                return True, data['choices'][0]['text']
        # fallback: stringify
        return True, str(data)
    except Exception as e:
        return False, f"Parse error: {e}"


def call_openai(prompt: str, openai_key: str, model: str = "gpt-3.5-turbo") -> tuple[bool, str]:
    """Call OpenAI via the openai-python client if available, otherwise return failure."""
    if OpenAI is None:
        return False, "OpenAI client not installed in environment."
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a technical documentation expert. Generate clear and concise documentation for the given code."},
                {"role": "user", "content": prompt}
            ],
        )
        # New client may return choices differently; handle common shapes
        try:
            return True, response.choices[0].message.content
        except Exception:
            try:
                return True, response['choices'][0]['message']['content']
            except Exception:
                return True, str(response)
    except Exception as e:
        return False, str(e)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate-docs', methods=['POST'])
def generate_docs():
    try:
        code = request.json.get('code')
        if not code:
            return jsonify({'error': 'No code provided'}), 400

        # Build a strict prompt asking for *only* a docstring/block comment
        prompt = (
            "Please generate ONLY a documentation docstring or block comment for the following code. "
            "Return only the docstring or comment text (no extra explanation).\n\n"
            f"Code:\n{code}\n\nDocumentation:" 
        )

        # Choose which key to use from environment variables
        hf_key = os.environ.get('HUGGINGFACE_API_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY')

        # If an hf key is present, prefer Hugging Face inference API
        if hf_key and hf_key.startswith('hf_'):
            # optional: allow override model via env
            hf_model = os.environ.get('HUGGINGFACE_MODEL', 'google/flan-t5-large')
            ok, result = call_huggingface(prompt, hf_key, model=hf_model)
            if ok:
                return jsonify({'documentation': result})
            else:
                return jsonify({'error': result}), 502

        # Else if OpenAI key present, use OpenAI
        if openai_key and openai_key.startswith('sk-'):
            ok, result = call_openai(prompt, openai_key)
            if ok:
                return jsonify({'documentation': result})
            else:
                return jsonify({'error': result}), 502

        # Fallback: check for keys hardcoded (not recommended)
        hardcoded_hf = None
        hardcoded_openai = None
        # If you previously had a key in code (not recommended), try it
        if 'HUGGINGFACE_API_KEY' in os.environ:
            hardcoded_hf = os.environ.get('HUGGINGFACE_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            hardcoded_openai = os.environ.get('OPENAI_API_KEY')

        return jsonify({'error': 'No API key found. Set HUGGINGFACE_API_KEY (hf_...) or OPENAI_API_KEY (sk_...).'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # app will read API keys from environment variables. Keep debug on for development.
    app.run(debug=True, host='127.0.0.1', port=5000)
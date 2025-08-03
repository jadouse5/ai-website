# main.py
import os
import google.generativeai as genai
from flask import Flask, request, Response

# --- Configuration ---
# IMPORTANT: Set your Google API key as an environment variable.
# For example, in your terminal: export GOOGLE_API_KEY='your-api-key'
# It is recommended to use an environment variable for security.
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Configure the Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# The API key should always be available (either from env var or fallback)
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-fallback-api-key-here":
    print("ERROR: The Google API key is not set.")
    print("Please set it as an environment variable (GOOGLE_API_KEY).")
    exit()
else:
    print(f"Using Google API key: {GOOGLE_API_KEY[:10]}...{GOOGLE_API_KEY[-4:]}")


# Initialize the Flask app
app = Flask(__name__)

# Global variable to store the current system prompt
current_system_prompt = (
    "You are a professional web developer. Your task is to generate complete, "
    "modern, and well-structured HTML for a web page based on the user's request. "
    "You must include the full HTML structure, including <!DOCTYPE html>, <html>, "
    "<head>, and <body> tags. Use Tailwind CSS for styling by including the "
    "official Tailwind CDN link in the <head> section. Always include clickable "
    "buttons and navigation links to other pages. Make sure all buttons are functional "
    "and lead to relevant pages."
)

# --- Helper Function for LLM Interaction ---
def generate_html_with_llm(page_prompt):
    """
    Sends a prompt to Google's Gemini 2.5 Flash model to generate HTML.

    Args:
        page_prompt (str): The prompt describing the page to generate.

    Returns:
        str: The generated HTML content, or an error message.
    """
    try:
        # Prepare the full prompt with system instructions
        full_prompt = (
            current_system_prompt +
            f"\n\n---USER REQUEST---\n{page_prompt}"
        )
        

        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Configure generation parameters for clean HTML output
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 4000,
        }
        
        # Enhanced prompt for clean output
        clean_prompt = "Generate ONLY complete, functional HTML code. Do not include any explanations, comments, or text before/after the HTML. Start directly with <!DOCTYPE html> and end with </html>. No markdown formatting.\n\n" + full_prompt
        
        # Generate content using Gemini
        response = model.generate_content(clean_prompt, generation_config=generation_config)
        
        # Extract the generated HTML
        generated_html = response.text.strip()
        
        # Clean up any unwanted text or markdown
        generated_html = generated_html.replace('```html', '').replace('```', '')
        
        # Remove any explanatory text before HTML
        if '<!DOCTYPE html>' in generated_html:
            generated_html = '<!DOCTYPE html>' + generated_html.split('<!DOCTYPE html>', 1)[1]
        elif '<html' in generated_html:
            generated_html = '<html' + generated_html.split('<html', 1)[1]
        
        return generated_html

    except Exception as e:
        print(f"An unexpected error occurred with the Google Gemini API: {e}")
        return f"<h1>Error: Could not connect to the Google Gemini API</h1><p>{e}</p>"


# --- Route to change system prompt ---
@app.route('/change-prompt', methods=['GET', 'POST'])
def change_prompt():
    """
    Route to display and update the system prompt.
    """
    global current_system_prompt
    
    if request.method == 'POST':
        new_prompt = request.form.get('new_prompt')
        if new_prompt:
            current_system_prompt = new_prompt
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Prompt Updated</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-100 p-8">
                <div class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-lg">
                    <h1 class="text-2xl font-bold text-green-600 mb-4">System Prompt Updated Successfully!</h1>
                    <p class="mb-4">The new system prompt has been applied.</p>
                    <div class="space-x-4">
                        <a href="/" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Go to Home</a>
                        <a href="/change-prompt" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">Change Prompt Again</a>
                    </div>
                </div>
            </body>
            </html>
            """
    
    # GET request - show the form
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Change System Prompt</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-lg">
            <h1 class="text-3xl font-bold mb-6">Change System Prompt</h1>
            <form method="POST" class="space-y-4">
                <div>
                    <label for="new_prompt" class="block text-sm font-medium text-gray-700 mb-2">Current System Prompt:</label>
                    <textarea name="new_prompt" id="new_prompt" rows="10" class="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">{current_system_prompt}</textarea>
                </div>
                <div class="space-x-4">
                    <button type="submit" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">Update Prompt</button>
                    <a href="/" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded inline-block">Cancel</a>
                </div>
            </form>
        </div>
    </body>
    </html>
    """

# --- The "Catch-All" Route ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    This function handles all incoming requests.
    It generates a prompt based on the URL path and gets the HTML from the LLM.
    """
    # If the path is empty, it's the home page.
    if not path:
        page_name = "home"
    else:
        # Use the path to create a more descriptive page name.
        # e.g., "products/laptops" becomes "products laptops"
        page_name = path.replace('/', ' ').replace('_', ' ')

    # --- Prompt Engineering ---
    # This is where you craft the prompt for the LLM.
    # A more sophisticated app might have different prompt templates for different types of pages.
    prompt = f"""Generate the HTML for a page about '{page_name}'. The page should have a clean and modern design. 
    Make the content interesting and relevant to the topic. If it's a product, include a price and a buy button. 
    If it's a blog post, make it informative. 
    
    IMPORTANT: Include the following navigation elements:
    - A navigation bar with links to: /about, /products, /blog, /contact
    - A "Change System Prompt" button that links to /change-prompt
    - At least 3 clickable buttons that lead to different pages (be creative with the links)
    - Make sure all buttons and links are properly styled with Tailwind CSS
    - Include hover effects on all interactive elements
    
    The page should feel like a real website with functional navigation."""

    print(f"Generating page for path: /{path}")
    print(f"Generated prompt: {prompt}")

    # Generate the HTML using the LLM
    html_content = generate_html_with_llm(prompt)

    # Return the generated HTML as the response
    return Response(html_content, mimetype='text/html')

# --- Running the Application ---
if __name__ == '__main__':
    # To run this application:
    # 1. Make sure you have Flask and Google's Generative AI library installed:
    #    pip install Flask google-generativeai
    # 2. Set your Google API key as an environment variable (GOOGLE_API_KEY).
    # 3. Run this script:
    #    python main.py
    # 4. Open your web browser and navigate to http://127.0.0.1:5000
    #    Try different URLs like:
    #    - http://127.0.0.1:5000/about_us
    #    - http://127.0.0.1:5000/products/vintage_cameras
    #    - http://127.0.0.1:5000/blog/the_future_of_ai
    
    # The API key check is now at the top of the script.
    app.run(debug=True, port=5001)


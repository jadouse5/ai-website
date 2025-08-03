# main.py
import os
from groq import Groq
from flask import Flask, request, Response

# --- Configuration ---
# IMPORTANT: Set your Groq API key as an environment variable.
# For example, in your terminal: export GROQ_API_KEY='your-api-key'
# It is recommended to use an environment variable for security.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

# The API key should always be available (either from env var or fallback)
if not GROQ_API_KEY or GROQ_API_KEY == "":
    print("WARNING: Using fallback Groq API key. Please set GROQ_API_KEY environment variable for production use.")
else:
    print(f"Using Groq API key: {GROQ_API_KEY[:10]}...{GROQ_API_KEY[-4:]}")

print(f"Groq API key configured: {GROQ_API_KEY[:10]}...{GROQ_API_KEY[-4:]}")


# Initialize the Flask app
app = Flask(__name__)

# Global variable to store the current system prompt
current_system_prompt = (
    "You are an elite UI/UX architect and full-stack developer specializing in cutting-edge web experiences. "
    "Create stunning, modern HTML pages that push the boundaries of web design. Your output must be:"
    "\n\n🎨 VISUAL EXCELLENCE:"
    "- Use advanced Tailwind CSS with custom animations, gradients, and glassmorphism effects"
    "- Implement dark/light mode toggle with smooth transitions"
    "- Add subtle parallax scrolling, hover animations, and micro-interactions"
    "- Use modern typography with variable fonts and perfect spacing"
    "- Include beautiful hero sections with animated backgrounds"
    "\n\n⚡ INTERACTIVE COMPONENTS:"
    "- Create responsive navigation with mobile hamburger menu"
    "- Add interactive cards, modals, and dropdown menus"
    "- Implement smooth scroll behavior and section transitions"
    "- Include loading animations and skeleton screens"
    "- Add interactive forms with real-time validation styling"
    "\n\n🚀 MODERN FEATURES:"
    "- Use CSS Grid and Flexbox for perfect layouts"
    "- Implement progressive disclosure and accordion components"
    "- Add search functionality with live filtering"
    "- Include social media integration and sharing buttons"
    "- Create interactive dashboards with charts and metrics"
    "\n\n📱 RESPONSIVE DESIGN:"
    "- Mobile-first approach with perfect tablet and desktop scaling"
    "- Touch-friendly interactions and gesture support"
    "- Optimized performance with lazy loading"
    "\n\nAlways include complete HTML structure with <!DOCTYPE html>, proper meta tags, "
    "Tailwind CSS CDN, and ensure all interactive elements are functional. "
    "Make every page feel like a premium, modern web application."
)

# --- Helper Function for LLM Interaction ---
def generate_html_with_llm(page_prompt):
    """
    Sends a prompt to Groq's Qwen model to generate HTML.

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
        
        # Generate content using Groq with advanced Qwen model
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite UI/UX architect. Generate ONLY complete, functional HTML code. Do not include any explanations, comments, or text before/after the HTML. Start directly with <!DOCTYPE html> and end with </html>. No markdown formatting."
                },
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="qwen2.5-72b-instruct",
            max_tokens=4000,
            temperature=0.8
        )
        
        # Extract the generated HTML
        generated_html = chat_completion.choices[0].message.content.strip()
        
        # Clean up any unwanted text or markdown
        generated_html = generated_html.replace('```html', '').replace('```', '')
        
        # Remove any explanatory text before HTML
        if '<!DOCTYPE html>' in generated_html:
            generated_html = '<!DOCTYPE html>' + generated_html.split('<!DOCTYPE html>', 1)[1]
        elif '<html' in generated_html:
            generated_html = '<html' + generated_html.split('<html', 1)[1]
        
        return generated_html

    except Exception as e:
        print(f"An unexpected error occurred with the Groq API: {e}")
        return f"<h1>Error: Could not connect to the Groq API</h1><p>{e}</p>"


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

    # --- Advanced Prompt Engineering ---
    # Sophisticated prompt templates for generating cutting-edge TUI experiences
    prompt = f"""🚀 CREATE AN EXCEPTIONAL '{page_name.upper()}' PAGE:
    
    📋 CONTENT REQUIREMENTS:
    - Generate rich, engaging content relevant to '{page_name}'
    - Include interactive elements: counters, progress bars, live data displays
    - Add testimonials, reviews, or user-generated content sections
    - Implement search/filter functionality where applicable
    - Include call-to-action sections with conversion-optimized design
    
    🎯 MANDATORY UI COMPONENTS:
    - Stunning hero section with animated gradient background
    - Responsive navigation bar with smooth mobile hamburger menu
    - "Change System Prompt" button (styled as premium feature)
    - Minimum 5 interactive buttons/cards leading to: /dashboard, /analytics, /settings, /profile, /explore
    - Floating action button (FAB) for quick actions
    - Breadcrumb navigation for better UX
    - Footer with social links and newsletter signup
    
    ✨ ADVANCED FEATURES TO IMPLEMENT:
    - Dark/light mode toggle with system preference detection
    - Loading skeletons and smooth page transitions
    - Interactive charts or data visualizations (using CSS/SVG)
    - Modal dialogs and toast notifications
    - Infinite scroll or pagination components
    - Real-time search with autocomplete suggestions
    - Drag-and-drop interfaces where relevant
    - Progressive web app features (offline indicators)
    
    🎨 VISUAL EXCELLENCE:
    - Glassmorphism cards with backdrop blur effects
    - Animated icons and micro-interactions
    - Custom CSS animations for scroll-triggered reveals
    - Beautiful color schemes with proper contrast ratios
    - Typography hierarchy with perfect spacing
    - Subtle shadows and depth for modern layering
    
    Make this the most impressive, modern TUI experience possible!"""

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


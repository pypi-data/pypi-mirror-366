#!/usr/bin/env python3
"""
AI Bot Agent - Command Line Interface
A powerful AI assistant that runs from the command line with various capabilities.
"""

import os
import sys
import json
import asyncio
import subprocess
import webbrowser
from typing import Optional, List, Dict, Any
from pathlib import Path
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
import openai
from dotenv import load_dotenv
import requests
import time
import datetime
import random

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

# Initialize Typer app
app = typer.Typer(
    name="ai-bot",
    help="AI Bot Agent - Your intelligent command line assistant",
    add_completion=False
)

class BaseAIProvider:
    """Base class for AI providers."""
    
    def __init__(self, name: str):
        self.name = name
        self.available = False
    
    def is_available(self) -> bool:
        """Check if this provider is available."""
        return self.available
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Send a message and get a response."""
        raise NotImplementedError
    
    def get_status(self) -> str:
        """Get provider status."""
        return f"{self.name}: {'✓ Available' if self.available else '✗ Not available'}"

class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider."""
    
    def __init__(self):
        super().__init__("OpenAI")
        self.client = None
        self.initialize()
    
    def initialize(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            self.available = False
            return
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
            # Test the connection
            self.client.models.list()
            self.available = True
        except Exception as e:
            console.print(f"[yellow]OpenAI not available: {e}[/yellow]")
            self.available = False
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Send a message to OpenAI and get a response."""
        if not self.available or not self.client:
            return "OpenAI is not available."
        
        try:
            system_prompt = """You are an intelligent AI assistant running from the command line. 
            You can help with:
            - Answering questions and providing information
            - Writing and analyzing code
            - File operations and system tasks
            - Web searches and research
            - Creative writing and brainstorming
            - Problem solving and analysis
            
            Be helpful, accurate, and concise in your responses."""
            
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            with console.status("[bold green]Thinking...", spinner="dots"):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error with OpenAI: {e}"

class FreeProvider(BaseAIProvider):
    """Free AI provider using public APIs."""
    
    def __init__(self):
        super().__init__("Free AI")
        self.available = True
        self.base_url = "https://api.freeai.org"  # Example free API
        self.fallback_responses = {
            "hello": "Hello! I'm your AI assistant. How can I help you today?",
            "help": "I can help you with questions, code generation, file analysis, and more. Just ask!",
            "code": "I can help you generate code. Please provide a description of what you need.",
            "python": "Python is a great programming language! What would you like to know about it?",
            "javascript": "JavaScript is perfect for web development. How can I help you with it?",
            "html": "HTML is the foundation of web pages. What would you like to learn?",
            "css": "CSS makes websites beautiful! What styling help do you need?",
            "git": "Git is essential for version control. What Git questions do you have?",
            "docker": "Docker helps with containerization. How can I assist you with Docker?",
            "linux": "Linux is a powerful operating system. What Linux help do you need?",
            "mac": "macOS is great for development. How can I help you with Mac?",
            "windows": "Windows has many development tools. What Windows help do you need?",
        }
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Send a message using free AI service."""
        try:
            message_lower = message.lower()
            
            # Check for specific keywords and provide helpful responses
            if any(word in message_lower for word in ["hello", "hi", "hey"]):
                return self.fallback_responses["hello"]
            elif "help" in message_lower:
                return self.fallback_responses["help"]
            elif "code" in message_lower or "program" in message_lower:
                return self.fallback_responses["code"]
            elif "python" in message_lower:
                return self.fallback_responses["python"]
            elif "javascript" in message_lower or "js" in message_lower:
                return self.fallback_responses["javascript"]
            elif "html" in message_lower:
                return self.fallback_responses["html"]
            elif "css" in message_lower:
                return self.fallback_responses["css"]
            elif "git" in message_lower:
                return self.fallback_responses["git"]
            elif "docker" in message_lower:
                return self.fallback_responses["docker"]
            elif "linux" in message_lower:
                return self.fallback_responses["linux"]
            elif "mac" in message_lower or "macos" in message_lower:
                return self.fallback_responses["mac"]
            elif "windows" in message_lower:
                return self.fallback_responses["windows"]
            elif "setup" in message_lower or "configure" in message_lower:
                return "To set up OpenAI API access, run: ai setup\n\nThis will guide you through:\n1. Getting your OpenAI API key\n2. Testing the connection\n3. Saving your configuration\n\nYou can also use the bot without setup - it works with limited capabilities!"
            elif "check" in message_lower and "how many" in message_lower and ("repository" in message_lower or "repo" in message_lower):
                return "To check how many repositories you have:\n\n• GitHub: Visit github.com/yourusername\n• GitLab: Visit gitlab.com/yourusername\n• Bitbucket: Visit bitbucket.org/yourusername\n\nOr use these commands:\n• git remote -v (shows connected remotes)\n• ls ~/projects (if you keep repos in a projects folder)\n\nFor automated repository analysis, consider setting up OpenAI API access."
            elif "repository" in message_lower or "repo" in message_lower:
                return "I can help you with repository management! Here are some common Git commands:\n\n• git status - Check repository status\n• git add . - Stage all changes\n• git commit -m 'message' - Commit changes\n• git push - Push to remote\n• git pull - Pull latest changes\n• git clone url - Clone a repository\n\nFor more detailed Git help, consider setting up OpenAI API access."
            elif "install" in message_lower or "installation" in message_lower:
                return "Installation options:\n\n• PyPI: pip install ai-bot-agent\n• Homebrew: brew tap thiennp/cli-smart && brew install cli-smart\n• Source: git clone https://github.com/thiennp/cli-smart.git\n\nAfter installation:\n• ai setup - Configure providers\n• ai chat - Start chatting\n• ai help - Show all commands"
            elif "command" in message_lower or "commands" in message_lower:
                return "Available commands:\n\n• ai setup - Configure AI providers\n• ai chat - Interactive chat\n• ai ask 'question' - Ask a question\n• ai code 'description' - Generate code\n• ai analyze 'file' - Analyze files\n• ai search 'query' - Search web\n• ai status - Show provider status\n• ai help - Show help\n• ai clear - Clear history"
            elif "free" in message_lower and "service" in message_lower:
                return "Yes, I'm currently using a free AI service with limited capabilities. I can help with:\n\n• Basic programming questions\n• Simple code examples\n• File analysis\n• Command explanations\n\nFor advanced features like:\n• Complex code generation\n• Detailed analysis\n• Web search\n• Full conversation context\n\nPlease set up OpenAI API access with: ai setup"
            else:
                # Provide a more intelligent response based on the message
                return self._generate_intelligent_response(message)
                
        except Exception as e:
            return f"I'm currently using a free AI service with limited capabilities. For better results, please set up your OpenAI API key using 'ai setup'. Error: {e}"
    
    def _generate_intelligent_response(self, message: str) -> str:
        """Generate a more intelligent response based on the message."""
        message_lower = message.lower()
        
        # Programming related
        if any(word in message_lower for word in ["function", "method", "class", "object"]):
            return "I can help with programming concepts! Here are some basics:\n\n• Functions: Reusable blocks of code\n• Methods: Functions that belong to objects\n• Classes: Blueprints for creating objects\n• Objects: Instances of classes\n\nFor detailed code examples and explanations, consider setting up OpenAI API access."
        
        # File system related
        elif any(word in message_lower for word in ["file", "directory", "folder", "path"]):
            return "I can help with file operations! Common commands:\n\n• ls - List files\n• cd - Change directory\n• mkdir - Create directory\n• rm - Remove files\n• cp - Copy files\n• mv - Move files\n\nFor file analysis, try: ai analyze filename"
        
        # System related
        elif any(word in message_lower for word in ["system", "os", "operating", "terminal", "shell"]):
            return "I can help with system operations! Common tasks:\n\n• Check OS: uname -a\n• Check disk space: df -h\n• Check memory: free -h\n• Process list: ps aux\n• Network: ifconfig or ip addr\n\nFor system analysis, consider setting up OpenAI API access."
        
        # Network related
        elif any(word in message_lower for word in ["network", "internet", "connection", "ping", "curl"]):
            return "I can help with network operations! Common commands:\n\n• ping hostname - Test connectivity\n• curl url - Download content\n• wget url - Download files\n• netstat - Network statistics\n• ifconfig - Network interfaces\n\nFor network analysis, consider setting up OpenAI API access."
        
        # General questions
        else:
            responses = [
                f"I understand you're asking about '{message}'. While I'm using a free service with limited capabilities, I can help with basic guidance. For detailed answers, consider setting up OpenAI API access with 'ai setup'.",
                f"That's an interesting question about '{message}'! I'm currently running on a free service, so my responses are simplified. For comprehensive help, try 'ai setup' to configure OpenAI.",
                f"I can help you with '{message}'! Since I'm using a free service, my responses are basic. For advanced AI capabilities, run 'ai setup' to configure OpenAI API access.",
                f"Great question about '{message}'! I'm here to help, though my current free service has limitations. For full AI capabilities, set up your OpenAI API key with 'ai setup'.",
                f"I'd be happy to help with '{message}'! For the best experience, consider setting up OpenAI API access using 'ai setup'."
            ]
            return random.choice(responses)

class HuggingFaceProvider(BaseAIProvider):
    """Hugging Face free model provider."""
    
    def __init__(self):
        super().__init__("Hugging Face")
        self.available = False
        self.initialize()
    
    def initialize(self):
        """Initialize Hugging Face provider."""
        try:
            # Check if we can access Hugging Face models
            # This would require the transformers library
            import transformers
            self.available = True
        except ImportError:
            self.available = False
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Send a message using Hugging Face models."""
        if not self.available:
            return "Hugging Face models not available. Install with: pip install transformers"
        
        try:
            # This would require implementing Hugging Face model loading
            # For now, return a placeholder
            return "Hugging Face integration coming soon! For now, use 'ai-bot setup' for OpenAI."
        except Exception as e:
            return f"Error with Hugging Face: {e}"

class AIBotAgent:
    def __init__(self):
        self.providers = []
        self.current_provider = None
        self.conversation_history = []
        self.system_prompt = """You are an intelligent AI assistant running from the command line. 
        You can help with:
        - Answering questions and providing information
        - Writing and analyzing code
        - File operations and system tasks
        - Web searches and research
        - Creative writing and brainstorming
        - Problem solving and analysis
        
        Be helpful, accurate, and concise in your responses."""
        
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize all available AI providers."""
        # Add providers in order of preference
        self.providers.append(OpenAIProvider())
        self.providers.append(FreeProvider())
        self.providers.append(HuggingFaceProvider())
        
        # Select the best available provider
        self.select_best_provider()
    
    def select_best_provider(self):
        """Select the best available provider."""
        for provider in self.providers:
            if provider.is_available():
                self.current_provider = provider
                console.print(f"[green]✓ Using {provider.name} as AI provider[/green]")
                return
        
        # If no provider is available, use the free provider as fallback
        self.current_provider = self.providers[1]  # FreeProvider
        console.print("[yellow]⚠️  No premium providers available. Using free AI service.[/yellow]")
        console.print("[yellow]For better results, run 'ai-bot setup' to configure OpenAI API.[/yellow]")
    
    def get_provider_status(self) -> str:
        """Get status of all providers."""
        status = []
        for provider in self.providers:
            status.append(provider.get_status())
        return "\n".join(status)
    
    def chat(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """Send a message to the AI and get a response."""
        if not self.current_provider:
            return "Error: No AI provider available. Please run 'ai-bot setup' to configure providers."
        
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Get response from current provider
            response = self.current_provider.chat(message, self.conversation_history)
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            return f"Error communicating with AI provider: {e}"
    
    def search_web(self, query: str) -> str:
        """Search the web for information."""
        return f"Web search for '{query}' - This feature requires web search API integration."
    
    def analyze_file(self, file_path: str) -> str:
        """Analyze a file and provide insights."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return f"Error: File '{file_path}' not found."
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analyze file based on extension
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']:
                return self._analyze_code_file(content, file_extension)
            elif file_extension in ['.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.css']:
                return self._analyze_text_file(content, file_extension)
            else:
                return self._analyze_generic_file(content, file_extension)
                
        except Exception as e:
            return f"Error analyzing file: {e}"
    
    def _analyze_code_file(self, content: str, extension: str) -> str:
        """Analyze a code file."""
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        analysis = f"📁 Code File Analysis ({extension})\n"
        analysis += f"📊 Statistics:\n"
        analysis += f"  • Total lines: {total_lines}\n"
        analysis += f"  • Code lines: {code_lines}\n"
        analysis += f"  • Comment lines: {comment_lines}\n"
        analysis += f"  • Comment ratio: {(comment_lines/total_lines*100):.1f}%\n\n"
        
        # Add AI analysis
        analysis += "🤖 AI Analysis:\n"
        analysis += self.chat(f"Analyze this {extension} code file and provide insights about its structure, potential improvements, and best practices:\n\n{content[:2000]}...")
        
        return analysis
    
    def _analyze_text_file(self, content: str, extension: str) -> str:
        """Analyze a text file."""
        lines = content.split('\n')
        total_lines = len(lines)
        words = len(content.split())
        chars = len(content)
        
        analysis = f"📁 Text File Analysis ({extension})\n"
        analysis += f"📊 Statistics:\n"
        analysis += f"  • Total lines: {total_lines}\n"
        analysis += f"  • Total words: {words}\n"
        analysis += f"  • Total characters: {chars}\n"
        analysis += f"  • Average words per line: {words/total_lines:.1f}\n\n"
        
        # Add AI analysis
        analysis += "🤖 AI Analysis:\n"
        analysis += self.chat(f"Analyze this {extension} file and provide insights about its content, structure, and potential improvements:\n\n{content[:2000]}...")
        
        return analysis
    
    def _analyze_generic_file(self, content: str, extension: str) -> str:
        """Analyze a generic file."""
        lines = content.split('\n')
        total_lines = len(lines)
        chars = len(content)
        
        analysis = f"📁 File Analysis ({extension})\n"
        analysis += f"📊 Statistics:\n"
        analysis += f"  • Total lines: {total_lines}\n"
        analysis += f"  • Total characters: {chars}\n\n"
        
        # Add AI analysis
        analysis += "🤖 AI Analysis:\n"
        analysis += self.chat(f"Analyze this {extension} file and provide insights about its content and structure:\n\n{content[:2000]}...")
        
        return analysis
    
    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code based on description."""
        prompt = f"Generate {language} code for: {description}\n\nPlease provide:\n1. The complete code\n2. Brief explanation\n3. Usage example"
        return self.chat(prompt)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        console.print("[green]✓ Conversation history cleared[/green]")

def display_banner():
    """Display the AI Bot banner."""
    banner = """
    🤖 AI Bot Agent v1.0
    Your intelligent command line assistant
    """
    console.print(Panel(banner, style="bold blue"))

def display_help():
    """Display help information."""
    help_text = """
    [bold]Available Commands:[/bold]
    
    [green]setup[/green] - Set up AI providers (OpenAI, Free AI)
    [green]status[/green] - Show AI provider status
    [green]chat[/green] - Start interactive chat mode
    [green]ask[/green] - Ask a single question
    [green]code[/green] - Generate code from description
    [green]analyze[/green] - Analyze a file
    [green]search[/green] - Search the web
    [green]clear[/green] - Clear conversation history
    [green]help[/green] - Show this help message
    [green]exit[/green] - Exit the bot
    
    [bold]Examples:[/bold]
    ai-bot setup
    ai-bot status
    ai-bot chat
    ai-bot ask "What is Python?"
    ai-bot code "Create a simple web scraper"
    ai-bot analyze main.py
    
    [bold]AI Providers:[/bold]
    • OpenAI (Recommended) - Full AI capabilities
    • Free AI - Limited but no setup required
    • Hugging Face - Coming soon
    """
    console.print(Panel(help_text, title="Help", style="green"))

def setup_openai_key():
    """Set up OpenAI API key with automated assistance."""
    display_banner()

    console.print("[bold green]🔧 AI Provider Setup[/bold green]")
    console.print("This will help you configure AI providers for the best experience.\n")

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        console.print("[yellow]Creating .env file...[/yellow]")
        env_file.write_text("OPENAI_API_KEY=your_openai_api_key_here\n")

    # Show current provider status
    bot = AIBotAgent()
    console.print("[bold blue]Current AI Provider Status:[/bold blue]")
    console.print(bot.get_provider_status())
    console.print()

    # Ask user what they want to do
    console.print("[bold blue]Setup Options:[/bold blue]")
    console.print("1. Configure OpenAI API (Recommended - Best AI capabilities)")
    console.print("2. Use Free AI Service (Limited but no setup required)")
    console.print("3. Show provider status")
    console.print("4. Exit setup")

    choice = Prompt.ask(
        "Choose an option",
        choices=["1", "2", "3", "4"],
        default="1"
    )

    if choice == "1":
        return setup_openai_provider(env_file)
    elif choice == "2":
        console.print("[green]✓ Free AI service is already available![/green]")
        console.print("You can start using the bot right away with limited capabilities.")
        return True
    elif choice == "3":
        console.print("\n[bold blue]Provider Status:[/bold blue]")
        console.print(bot.get_provider_status())
        return True
    else:
        console.print("[yellow]Setup cancelled.[/yellow]")
        return False

def setup_openai_provider(env_file: Path):
    """Set up OpenAI API provider."""
    console.print("\n[bold blue]Step 1: Getting your OpenAI API key[/bold blue]")
    console.print("Opening OpenAI API key page in your browser...")

    try:
        webbrowser.open("https://platform.openai.com/api-keys")
        console.print("[green]✓ Browser opened successfully[/green]")
    except Exception as e:
        console.print(f"[red]Could not open browser automatically: {e}[/red]")
        console.print("Please manually visit: https://platform.openai.com/api-keys")

    console.print("\n[bold yellow]Instructions:[/bold yellow]")
    console.print("1. Sign in to your OpenAI account")
    console.print("2. Click 'Create new secret key'")
    console.print("3. Give it a name (e.g., 'AI Bot Agent')")
    console.print("4. Copy the API key (it starts with 'sk-')")
    console.print("5. Keep it secure - you won't see it again!")

    # Wait for user to get the key
    console.print("\n[bold blue]Step 2: Enter your API key[/bold blue]")
    api_key = Prompt.ask(
        "Enter your OpenAI API key",
        password=True,
        default=""
    )

    if not api_key or api_key == "your_openai_api_key_here":
        console.print("[red]No valid API key provided. Setup cancelled.[/red]")
        return False

    # Validate the API key format
    if not api_key.startswith("sk-"):
        console.print("[red]Invalid API key format. OpenAI API keys start with 'sk-'[/red]")
        return False

    # Test the API key
    console.print("\n[bold blue]Step 3: Testing your API key[/bold blue]")
    try:
        test_client = openai.OpenAI(api_key=api_key)
        # Try a simple API call to test the key
        response = test_client.models.list()
        console.print("[green]✓ API key is valid![/green]")
    except Exception as e:
        console.print(f"[red]❌ API key test failed: {e}[/red]")
        console.print("Please check your API key and try again.")
        return False

    # Save the API key to .env file
    console.print("\n[bold blue]Step 4: Saving your API key[/bold blue]")
    try:
        env_content = f"OPENAI_API_KEY={api_key}\n"
        env_file.write_text(env_content)
        console.print("[green]✓ API key saved to .env file[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to save API key: {e}[/red]")
        console.print("Please manually add your API key to the .env file:")
        console.print(f"OPENAI_API_KEY={api_key}")
        return False

    console.print("\n[bold green]🎉 Setup Complete![/bold green]")
    console.print("Your OpenAI API key has been configured successfully.")
    console.print("\nYou can now use the AI Bot Agent with full capabilities:")
    console.print("• ai-bot chat - Start interactive chat")
    console.print("• ai-bot ask 'Your question' - Ask a single question")
    console.print("• ai-bot code 'Description' - Generate code")
    console.print("• ai-bot analyze 'file.txt' - Analyze files")
    console.print("• ai-bot status - Check provider status")

    return True

@app.command()
def setup():
    """Set up AI providers with automated assistance."""
    setup_openai_key()

@app.command()
def status():
    """Show the status of all AI providers."""
    display_banner()
    
    console.print("[bold green]🔍 AI Provider Status[/bold green]\n")
    
    bot = AIBotAgent()
    status_text = bot.get_provider_status()
    
    # Create a nice table for the status
    table = Table(title="AI Provider Status")
    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Description", style="white")
    
    for line in status_text.split('\n'):
        if ':' in line:
            provider, status = line.split(':', 1)
            if '✓ Available' in status:
                table.add_row(provider.strip(), "✓ Available", "Ready to use")
            else:
                table.add_row(provider.strip(), "✗ Not available", "Requires setup")
    
    console.print(table)
    
    console.print("\n[bold blue]Current Provider:[/bold blue]")
    if bot.current_provider:
        console.print(f"✓ Using: {bot.current_provider.name}")
        if bot.current_provider.name == "Free AI":
            console.print("[yellow]Note: Free AI has limited capabilities. Run 'ai-bot setup' for full features.[/yellow]")
    else:
        console.print("✗ No provider available")
    
    console.print("\n[bold blue]Commands:[/bold blue]")
    console.print("• ai-bot setup - Configure providers")
    console.print("• ai-bot chat - Start interactive chat")
    console.print("• ai-bot ask 'question' - Ask a question")
    console.print("• ai-bot code 'description' - Generate code")

@app.command()
def chat():
    """Start an interactive chat session with the AI."""
    display_banner()
    
    bot = AIBotAgent()
    
    if not bot.current_provider:
        console.print("[red]Error: No AI provider available.[/red]")
        console.print("Please run 'ai-bot setup' to configure providers.")
        return
    
    console.print(f"[green]🤖 Starting chat with {bot.current_provider.name}[/green]")
    if bot.current_provider.name == "Free AI":
        console.print("[yellow]Note: Using free AI service with limited capabilities.[/yellow]")
        console.print("[yellow]Run 'ai-bot setup' for full OpenAI features.[/yellow]")
    
    console.print("\n[bold blue]Chat Commands:[/bold blue]")
    console.print("• Type your message and press Enter")
    console.print("• Type 'clear' to clear conversation history")
    console.print("• Type 'help' to see available commands")
    console.print("• Type 'quit' or 'exit' to end the session")
    console.print("• Press Ctrl+C to exit")
    
    console.print("\n" + "="*50)
    
    try:
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[green]Goodbye! 👋[/green]")
                    break
                elif user_input.lower() == 'clear':
                    bot.clear_history()
                    continue
                elif user_input.lower() == 'help':
                    display_help()
                    continue
                elif not user_input.strip():
                    continue
                
                # Get AI response
                response = bot.chat(user_input)
                
                # Display response
                console.print(f"\n[bold green]AI[/bold green]: {response}")
                
            except KeyboardInterrupt:
                console.print("\n[green]Goodbye! 👋[/green]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                
    except KeyboardInterrupt:
        console.print("\n[green]Goodbye! 👋[/green]")

@app.command()
def ask(
    question: str = typer.Argument(..., help="The question to ask the AI")
):
    """Ask a single question to the AI."""
    bot = AIBotAgent()
    display_banner()
    
    console.print(f"\n[bold blue]Question:[/bold blue] {question}")
    
    response = bot.chat(question)
    console.print(f"\n[bold green]Answer:[/bold green] {response}")

@app.command()
def code(
    description: str = typer.Argument(..., help="Description of the code to generate"),
    language: str = typer.Option("python", "--lang", "-l", help="Programming language")
):
    """Generate code from a description."""
    bot = AIBotAgent()
    display_banner()
    
    console.print(f"\n[bold blue]Generating {language} code for:[/bold blue] {description}")
    
    response = bot.generate_code(description, language)
    console.print(f"\n[bold green]Generated Code:[/bold green]\n{response}")

@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Path to the file to analyze")
):
    """Analyze a file and provide insights."""
    bot = AIBotAgent()
    display_banner()
    
    console.print(f"\n[bold blue]Analyzing file:[/bold blue] {file_path}")
    
    response = bot.analyze_file(file_path)
    console.print(f"\n[bold green]Analysis:[/bold green]\n{response}")

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query")
):
    """Search the web for information."""
    bot = AIBotAgent()
    display_banner()
    
    console.print(f"\n[bold blue]Searching for:[/bold blue] {query}")
    
    response = bot.search_web(query)
    console.print(f"\n[bold green]Search Results:[/bold green]\n{response}")

@app.command()
def clear():
    """Clear conversation history."""
    bot = AIBotAgent()
    bot.clear_history()

@app.command()
def help():
    """Show help information."""
    display_help()

if __name__ == "__main__":
    app() 
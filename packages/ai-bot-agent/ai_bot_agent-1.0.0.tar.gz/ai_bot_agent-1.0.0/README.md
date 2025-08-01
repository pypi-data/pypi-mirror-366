# 🤖 AI Bot Agent

A powerful AI assistant that runs from the command line with various capabilities including chat, code generation, file analysis, and web search.

## Features

- **Interactive Chat Mode**: Have conversations with the AI
- **Code Generation**: Generate code from natural language descriptions
- **File Analysis**: Analyze and get insights about your files
- **Web Search**: Search for information on the web
- **Rich CLI Interface**: Beautiful terminal interface with colors and formatting
- **Conversation History**: Maintains context across interactions
- **Multiple AI Models**: Support for different OpenAI models

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Quick Start

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd cli-smart
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the bot**
   ```bash
   python main.py --help
   ```

### Alternative Installation

You can also install it as a package:

```bash
pip install -e .
```

Then run it as:

```bash
ai-bot --help
```

## Usage

### Interactive Chat Mode

Start an interactive conversation with the AI:

```bash
python main.py chat
```

### Ask a Single Question

Ask a specific question:

```bash
python main.py ask "What is machine learning?"
```

### Generate Code

Generate code from a description:

```bash
python main.py code "Create a simple web scraper"
```

Generate code in a specific language:

```bash
python main.py code "Create a REST API" --lang javascript
```

### Analyze Files

Analyze a file and get insights:

```bash
python main.py analyze main.py
```

### Search the Web

Search for information:

```bash
python main.py search "latest Python features"
```

### Clear History

Clear conversation history:

```bash
python main.py clear
```

### Get Help

Show help information:

```bash
python main.py help
```

## Configuration

Create a `.env` file in the project root with your configuration:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize the AI model
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Set default temperature for responses
OPENAI_TEMPERATURE=0.7

# Optional: Set maximum tokens for responses
OPENAI_MAX_TOKENS=1000
```

## Examples

### Chat Mode Examples

```
You: What is Python?
AI Bot: Python is a high-level, interpreted programming language...

You: Write a function to calculate fibonacci numbers
AI Bot: Here's a Python function to calculate Fibonacci numbers...

You: Explain machine learning in simple terms
AI Bot: Machine learning is like teaching a computer to learn...
```

### Code Generation Examples

```bash
# Generate a Python web scraper
python main.py code "Create a web scraper that extracts titles from a news website"

# Generate a JavaScript function
python main.py code "Create a function to validate email addresses" --lang javascript

# Generate a data analysis script
python main.py code "Create a script to analyze CSV data and create visualizations"
```

## Features in Detail

### Interactive Chat Mode
- Maintains conversation context
- Rich formatting with colors
- Easy-to-use interface
- Built-in commands (exit, clear, help)

### Code Generation
- Supports multiple programming languages
- Generates complete, working code
- Includes explanations and usage examples
- Optimized for different use cases

### File Analysis
- Analyzes code structure and purpose
- Identifies potential issues
- Provides improvement suggestions
- Works with various file types

### Web Search
- Search for current information
- Get real-time data
- Research capabilities
- Information gathering

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: OpenAI client not initialized. Please check your API key.
   ```
   Solution: Make sure your OpenAI API key is set in the `.env` file.

2. **Module Not Found**
   ```
   ModuleNotFoundError: No module named 'openai'
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

3. **Permission Denied**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   Solution: Make sure the script is executable: `chmod +x main.py`

### Getting Help

- Use `python main.py help` for command help
- Use `python main.py --help` for general help
- Check the logs for detailed error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by [OpenAI](https://openai.com/) API

## Version History

- **v1.0.0**: Initial release with basic chat, code generation, and file analysis features 
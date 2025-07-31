<div align="center">
  
  # 🚀 rallies-cli
  
  **AI-Powered investment research**
  
  *ChatGPT for traders, backed by real-time financial data*

  [![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
  [![Rallies.ai](https://img.shields.io/badge/Data%20by-Rallies.ai-ff6b6b.svg)](https://rallies.ai)

   ![Rallies CLI Demo](demo/demo.png) 
  
</div>

## ✨ What is rallies-cli?

Rallies CLI is an intelligent investment research agent built by [Rallies](https://rallies.ai) that combines the conversational power of AI with real-time financial data. Think of it as ChatGPT specifically designed for traders and investors, equipped with live market data, news feeds, and comprehensive financial analysis capabilities.

#### What's different from ChatGPT, Perplexity Finance, etc?

Most existing LLMs, even with web search and other capabilities rely on out-dated stock market data. Moreover, since they are not backed by real-time data, running complex queries is hard, and often returns inaccurate results e.g try asking an LLM "can you summarize today's options flow data for AAPL", and you'll realize that a lot of the answers simply rely on web searches which are never real-time.

On the contrary, rallies-cli relies on real-time data that is updated as frequently as possible. 

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/your-username/rallies-cli.git
cd rallies-cli
pip install -e .


# Install from PyPI (coming soon)
pip install rallies
```

### Setup

1. **Get your OpenAI API key** from [OpenAI Platform](https://platform.openai.com/)
2. **Set environment variable**:
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```
3. **Launch rallies from your terminal**:
   ```bash
   rallies
   ```

That's it! You're ready to start researching.

## 💡 Usage Examples

### Basic Queries
```
> What's happening with AAPL today?
> Analyze Tesla's recent performance
> Show me top gainers in tech sector
```

### Advanced Analysis  
```
> Compare MSFT vs GOOGL over the last quarter
> Find stocks with cup and handle patterns
> What's the market sentiment on cryptocurrency?
```

### Technical Analysis
```
> Show me NVDA's technical indicators
> Find oversold stocks in the S&P 500
> Analyze Bitcoin's recent price action
```

### News & Events
```
> Latest earnings reports this week
> Federal Reserve meeting impact on markets
> Breaking news affecting my portfolio
```

## 🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands and usage |
| `/key API_KEY` | Set your rallies.ai API key for more usage |
| `/feed` | Browse recent high-scoring community questions |
| `/clear` | Clear conversation history |
| `/compact` | Compress conversation while preserving context |
| `/exit` or `/quit` | Exit the application |


## 🔑 API Keys & Authentication

### OpenAI API Key (Required)
```bash
export OPENAI_API_KEY="sk-your-openai-key"
```

### Rallies.ai API Key (Optional - Higher usage limits)
```bash
# Set via CLI
rallies
> /key your-rallies-api-key
```

The Rallies.ai API key provides you higher rate limits. You can get your key by registering for a free account at [Rallies](https://rallies.ai)

## 📋 Requirements

- **Python 3.8+**
- **OpenAI API Key** (required)
- **Terminal with color support** (recommended)
- **Internet connection** for real-time data

### Dependencies

- `openai` - GPT-4 integration
- `rich` - Terminal formatting and colors  
- `requests` - HTTP requests for data APIs
- `inquirer` - Interactive prompts
- `tiktoken` - Token counting and management
- `numpy` - Numerical computations

## 🐛 Troubleshooting

### Common Issues

**"OpenAI API Key not found"**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**"Rate limit exceeded"**
- Get a Rallies.ai API key for higher limits
- Use `/compact` to reduce token usage

**"Network connection error"**  
- Check internet connection
- Verify firewall settings
- Try again after a few moments

**"Import errors"**
```bash
pip install --upgrade rallies
```

### Getting Help

- 📧 **Email**: [support@rallies.ai](mailto:support@rallies.ai)
- 💬 **Discord**: [Rallies.ai Discord](https://discord.gg/xKbBExMTYc)


## 🌐 Links

- **Website**: [rallies.ai](https://rallies.ai)
- **Mobile app**: [Rallies](https://apps.apple.com/us/app/rallies-ai-stocks-trading/id6745213959?platform=iphone)
- **Twitter**: [@RalliesAI](https://x.com/ralliesai)
- **LinkedIn**: [Rallies AI](https://www.linkedin.com/company/107790814/)

## ⚠️ Disclaimer

**This tool is for educational and research purposes only.** Rallies CLI does not provide investment advice, recommendations, or financial guidance. All information provided is for informational purposes only and should not be considered as investment advice. Always consult with a qualified financial advisor before making any investment decisions. Past performance does not guarantee future results. Trading and investing involve risk of loss.

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.


---

<div align="center">
  
  **Built with ❤️ by the Rallies team** - 
  *Making financial research accessible to everyone*

</div>
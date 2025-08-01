# psst-openai Usage Guide

## Overview

The `psst-openai` tool integrates psst compression with OpenAI's API, automatically compressing your prompts before sending them to save tokens and reduce costs.

## Setup

### 1. Install Dependencies
```bash
pip install requests
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY=your_api_key_here
```

## Basic Usage

### Simple Prompt
```bash
psst-openai "Explain quantum computing in simple terms"
```

### From File
```bash
psst-openai < examples/openai_test_prompt.txt
```

### With Compression Stats
```bash
psst-openai --show-tokens "Summarize the following text in 3 bullet points. Explain the benefits of renewable energy."
```

### Custom Model
```bash
psst-openai --model gpt-4 "Complex reasoning task requiring advanced capabilities"
```

### With System Prompt
```bash
psst-openai --system "You are a helpful coding assistant" "Explain Python decorators"
```

## Advanced Usage

### Raw (Uncompressed) Mode
```bash
# Compare compressed vs uncompressed
psst-openai --show-tokens "Long prompt with repeated phrases..."
psst-openai --raw --show-tokens "Long prompt with repeated phrases..."
```

### Custom Glossary
```bash
psst-openai --glossary medical_glossary.json "Medical consultation prompt"
```

### JSON Output
```bash
psst-openai --json "Simple prompt" | jq '.choices[0].message.content'
```

### Token Usage Statistics
```bash
psst-openai --usage "Analyze this complex document structure"
```

## Example Workflows

### 1. Content Creation Pipeline
```bash
# Create prompt file
cat > content_prompt.txt << EOF
Please act as a content writer.
Summarize the following text in 3 bullet points.
Respond in a warm, casual tone for social media.
Topic: Latest developments in renewable energy
EOF

# Process with compression stats
psst-openai --show-tokens --usage < content_prompt.txt
```

### 2. Code Analysis
```bash
psst-openai --system "You are an expert software engineer" \
            --model gpt-4 \
            "Please explain this code and calculate its time complexity: [code here]"
```

### 3. Research Assistant
```bash
# Using pipeline for multiple queries
echo "Summarize the following text in 3 bullet points. Topic: Climate change impacts" | \
psst-openai --show-tokens --model gpt-3.5-turbo
```

## Compression Benefits

### Typical Savings
- **Short prompts**: 2-5% reduction
- **Medium prompts with common phrases**: 8-15% reduction  
- **Long prompts with repeated patterns**: 15-30% reduction

### Token Cost Impact
```bash
# Example: 100-token prompt compressed to 85 tokens
# At $0.002/1K tokens (GPT-3.5): 15% cost reduction
# At $0.03/1K tokens (GPT-4): 15% cost reduction
```

## Troubleshooting

### API Key Issues
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set temporarily
OPENAI_API_KEY=your_key psst-openai "test prompt"
```

### Dependency Issues
```bash
# Install requests
pip install requests

# Check installation
python3 -c "import requests; print('requests OK')"
```

### Compression Issues
```bash
# Validate glossary
python3 psst_compiler.py validate core_glossary.json

# Test compression only
./psst-compress test_prompt.txt
./psst-expand test_prompt.psst
```

## Integration Examples

### Shell Scripts
```bash
#!/bin/bash
# ai_assistant.sh
PROMPT="$1"
if [ -z "$PROMPT" ]; then
    echo "Usage: $0 'your prompt here'"
    exit 1
fi

psst-openai --show-tokens --usage "$PROMPT"
```

### Python Integration
```python
import subprocess
import json

def ask_ai(prompt, model="gpt-3.5-turbo"):
    result = subprocess.run([
        "./psst-openai", 
        "--json", 
        "--model", model,
        prompt
    ], capture_output=True, text=True)
    
    response = json.loads(result.stdout)
    return response["choices"][0]["message"]["content"]

# Usage
answer = ask_ai("Explain machine learning")
print(answer)
```

### Batch Processing
```bash
# Process multiple prompts
cat prompts.txt | while read prompt; do
    echo "=== Processing: $prompt ==="
    psst-openai --show-tokens "$prompt"
    echo
done
```

## Cost Optimization Tips

1. **Use compression by default** - Let psst reduce token usage automatically
2. **Monitor with --show-tokens** - Track compression effectiveness  
3. **Choose appropriate models** - Use GPT-3.5 for simple tasks, GPT-4 for complex ones
4. **Batch similar prompts** - Reuse system prompts and compressed phrases
5. **Profile your glossary** - Add domain-specific terms for better compression

## Security Notes

- API keys are read from environment variables only
- Prompts are sent directly to OpenAI (review sensitive content)
- Local compression happens before transmission
- No data is stored locally by psst-openai

---

For more information, see the main [ReadMe.md](../ReadMe.md) and [INSTALL.md](../INSTALL.md). 
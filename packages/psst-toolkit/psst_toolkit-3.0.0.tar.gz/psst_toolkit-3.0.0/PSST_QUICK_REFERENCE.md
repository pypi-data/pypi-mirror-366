# PSST Quick Reference Card
## Prompt Symbol Standard Technology

**Version**: 3.0.0 | **Compression**: 88.6% | **Fidelity**: Perfect

---

## 🚀 Quick Start

```bash
# Install dependencies
python3 -m pip install jellyfish numpy

# Test the system
python3 psst_ultimate.py compress examples/legal_prompt.txt
```

---

## 📝 Basic Commands

### Compression
```bash
# Compress a file
python3 psst_ultimate.py compress input.txt

# Compress with custom output
python3 psst_ultimate.py compress input.txt --output compressed.psst

# Compress with custom glossary
python3 psst_ultimate.py compress input.txt --glossary custom.json
```

### Expansion
```bash
# Expand a compressed file
python3 psst_ultimate.py expand input_ultimate.psst --output expanded.txt

# Expand to console
python3 psst_ultimate.py expand input_ultimate.psst
```

### Verification
```bash
# Verify fidelity
diff original.txt expanded.txt
# Should return no differences
```

---

## 🧠 Learning System

```bash
# Learn from a file
python3 psst-learn learn input.txt

# Learn from directory
python3 psst-learn batch-learn /path/to/prompts/

# Compress with learning
python3 psst-learn compress input.txt

# Check statistics
python3 psst-learn stats

# Get suggestions
python3 psst-learn suggest

# Auto-optimize
python3 psst-learn optimize
```

---

## 📊 Compression Results

| System | Compression | Fidelity | Best For |
|--------|-------------|----------|----------|
| **Ultimate** | 88.6% | Perfect | Production |
| **Dynamic** | 80-90% | High | Learning |
| **Enhanced** | 87.1% | High | Semantic |

---

## 🔧 Advanced Usage

### Custom Glossary
```json
{
  "version": "3.0.0",
  "glossary": {
    "⚖️": "You are a legal assistant. Highlight key rulings and arguments in the case below.",
    "🔍": "Analyze the following text and identify key issues.",
    "📄": "Summarize the following text in 3 bullet points."
  }
}
```

### Python API
```python
from psst_ultimate import UltimatePsstCompiler

compiler = UltimatePsstCompiler()
compressed = compiler.compress("Your text here")
expanded = compiler.expand(compressed)
```

### Batch Processing
```bash
# Process all .txt files
for file in *.txt; do
    python3 psst_ultimate.py compress "$file"
done
```

---

## 🎯 Common Patterns

### Legal Domain
- `⚖️` = "You are a legal assistant. Highlight key rulings and arguments in the case below."
- `📜` = "The plaintiff filed a motion for summary judgment claiming breach of contract."
- `⚔️` = "The defendant argues that the contract was void due to mutual mistake regarding the property's zoning classification."

### Technical Domain
- `💻` = "Implement the following functionality in Python:"
- `🔧` = "Debug the following code and provide fixes:"
- `📊` = "Analyze the performance metrics and provide insights:"

### General
- `📄` = "Summarize the following text in 3 bullet points."
- `🎨` = "Respond in a warm, casual tone when explaining complex concepts."
- `🔍` = "Analyze the following text and identify key issues."

---

## ⚠️ Troubleshooting

### Common Issues
```bash
# Python not found
python3 --version

# Missing dependencies
python3 -m pip install jellyfish numpy

# Poor compression
python3 psst-learn learn input.txt

# Expansion mismatch
python3 psst_ultimate.py expand input.psst --output test.txt
diff original.txt test.txt
```

### Validation
```bash
# Create test
echo "Test content" > test.txt
python3 psst_ultimate.py compress test.txt
python3 psst_ultimate.py expand test_ultimate.psst --output test_expanded.txt
diff test.txt test_expanded.txt
```

---

## 📈 Performance Tips

1. **Use Ultimate PSST** for production with perfect fidelity
2. **Create domain-specific glossaries** for better compression
3. **Use the learning system** for evolving patterns
4. **Validate results** with diff comparison
5. **Monitor compression ratios** over time

---

## 🔗 Integration Examples

### OpenAI API
```python
import openai
from psst_ultimate import UltimatePsstCompiler

compiler = UltimatePsstCompiler()
compressed_prompt = compiler.compress(original_prompt)

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": compressed_prompt}]
)
```

### Batch Processing
```bash
# Process directory
find . -name "*.txt" -exec python3 psst_ultimate.py compress {} \;

# Check results
ls -la *.psst
```

---

## 📞 Support

- **Documentation**: `PSST_USER_MANUAL.md`
- **Examples**: `examples/` directory
- **Results**: `COMPRESSION_RESULTS.md`
- **Validation**: Always use `diff` to verify fidelity

---

**Remember**: Always validate compression/expansion with `diff` to ensure perfect fidelity! 
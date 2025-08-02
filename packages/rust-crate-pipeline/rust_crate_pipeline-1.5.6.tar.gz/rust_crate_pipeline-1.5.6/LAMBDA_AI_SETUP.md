# Lambda.AI Setup Guide for Rust Crate Pipeline

This guide explains how to set up and use Lambda.AI with the Rust Crate Pipeline for AI-powered crate analysis.

## 🚀 Quick Start

### 1. Get Your Lambda.AI API Key

1. Sign up at [Lambda.AI](https://lambda.ai/)
2. Generate an API key from your dashboard
3. Set the environment variable:

```bash
# Windows PowerShell
$env:LAMBDA_API_KEY="your_api_key_here"

# Windows Command Prompt
set LAMBDA_API_KEY=your_api_key_here

# Linux/Mac
export LAMBDA_API_KEY="your_api_key_here"
```

### 2. Test Your Setup

```bash
# Test with a single crate
python run_pipeline_with_llm.py \
  --llm-provider lambda \
  --llm-model qwen25-coder-32b-instruct \
  --crates tokio \
  --verbose
```

### 3. Process Multiple Crates

```bash
# Process from a file
python run_pipeline_with_llm.py \
  --llm-provider lambda \
  --llm-model qwen25-coder-32b-instruct \
  --crates-file remaining_crates.txt \
  --batch-size 10 \
  --verbose
```

## 🎯 Available Models

### Recommended Models for Rust Analysis

**Primary Recommendation:**
- **`qwen25-coder-32b-instruct`** - Specialized coding model, excellent for Rust analysis

**High-Performance Options:**
- **`deepseek-r1-671b`** - Large model with superior reasoning
- **`deepseek-r1-0528`** - Latest DeepSeek model

**Cost-Effective Options:**
- **`llama-4-maverick-17b-128e-instruct-fp8`** - Good performance, lower cost
- **`llama3.1-8b-instruct`** - Fast processing, smaller model

## 💰 Cost Optimization

### Budget Planning for $1000 Credit

**Conservative Estimate:**
- **139 crates** ≈ $3-4 total cost
- **Cost per crate** ≈ $0.02-0.03
- **Budget efficiency** ≈ 99.6% remaining

**Recommended Allocation:**
- **$50** - Testing and setup
- **$100** - Process all remaining crates
- **$850** - Advanced features and experimentation

### Cost-Effective Processing

```bash
# Use cost-effective model for batch processing
python run_pipeline_with_llm.py \
  --llm-provider lambda \
  --llm-model llama-4-maverick-17b-128e-instruct-fp8 \
  --crates-file remaining_crates.txt \
  --batch-size 20 \
  --llm-max-tokens 600
```

## 🔧 Advanced Configuration

### Custom API Base URL

```bash
python run_pipeline_with_llm.py \
  --llm-provider lambda \
  --llm-model qwen25-coder-32b-instruct \
  --llm-api-base https://api.lambda.ai/v1 \
  --crates tokio
```

### Optimized Parameters

```bash
python run_pipeline_with_llm.py \
  --llm-provider lambda \
  --llm-model qwen25-coder-32b-instruct \
  --llm-temperature 0.1 \
  --llm-max-tokens 800 \
  --llm-timeout 60 \
  --llm-max-retries 3 \
  --crates tokio serde actix-web
```

## 📊 Performance Monitoring

### Check API Usage

Monitor your Lambda.AI usage through the dashboard to track:
- API calls made
- Tokens consumed
- Cost incurred
- Rate limits

### Expected Performance

**Processing Speed:**
- **Single crate:** 30-60 seconds
- **Batch processing:** 2-3 crates per minute
- **Total time for 139 crates:** 1-2 hours

**Quality:**
- **Code understanding:** Excellent
- **Security analysis:** Good
- **Performance assessment:** Very good
- **Documentation quality:** Good

## 🚨 Troubleshooting

### Common Issues

**"API key not found"**
```bash
# Check environment variable
echo $LAMBDA_API_KEY
```

**"Model not available"**
```bash
# List available models
curl -H "Authorization: Bearer $LAMBDA_API_KEY" \
  https://api.lambda.ai/v1/models
```

**"Rate limit exceeded"**
- Reduce batch size
- Add delays between requests
- Check your account limits

### Debug Mode

```bash
python run_pipeline_with_llm.py \
  --llm-provider lambda \
  --llm-model qwen25-coder-32b-instruct \
  --crates tokio \
  --verbose \
  --llm-timeout 120
```

## 🎯 Best Practices

### 1. Start Small
- Test with 2-3 crates first
- Verify output quality
- Optimize parameters

### 2. Batch Processing
- Use appropriate batch sizes (10-20)
- Monitor memory usage
- Implement error handling

### 3. Quality Control
- Review sample outputs
- Adjust prompts if needed
- Validate analysis accuracy

### 4. Cost Management
- Monitor usage regularly
- Use cost-effective models for bulk processing
- Reserve budget for advanced features

## 📚 Additional Resources

- [Lambda.AI Documentation](https://docs.lambda.ai/)
- [Lambda Inference API Guide](https://docs.lambda.ai/public-cloud/lambda-inference-api/)
- [Available Models](https://docs.lambda.ai/public-cloud/lambda-inference-api/#listing-models)
- [Main LLM Providers Guide](README_LLM_PROVIDERS.md)

## 🤝 Support

For issues with:
- **Lambda.AI API:** Contact Lambda.AI support
- **Pipeline integration:** Check the main documentation
- **Model performance:** Try different models or parameters 
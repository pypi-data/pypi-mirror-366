# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude usage analysis tool that analyzes Claude AI usage history from local project files to calculate token consumption and costs. The tool is designed as a single Python file utility with rich terminal output capabilities, supporting multiple currencies and flexible pricing models.

## Commands

### Development and Testing
```bash
# Run the main analysis tool
python main.py

# Run with custom parameters
python main.py --data-dir /path/to/.claude/projects --max-days 7 --max-projects 5

# Display costs in Chinese Yuan (CNY)
python main.py --currency CNY

# Display costs in US Dollars (USD) 
python main.py --currency USD

# Use custom exchange rate
python main.py --currency CNY --usd-to-cny 7.0

# Install as package and run
claude-cost

# Install dependencies
uv pip install rich pyyaml
# or
pip install rich pyyaml

# Debug mode
python main.py --log-level DEBUG

# Code quality checks (MUST run after code changes)
uv run pyright claude_code_cost/
uv run pyright tests/
```

### Package Management
```bash
# Install dependencies with uv (preferred)
uv venv
source .venv/bin/activate
uv pip install rich pyyaml

# Build package
python -m build
```

## Architecture

### Core Components

**Single File Architecture**: The entire application logic is contained in `main.py` with four main data classes:

- `ProjectStats`: Individual project statistics (tokens, costs, models used)
- `DailyStats`: Daily aggregated statistics with project breakdowns
- `ModelStats`: Individual model statistics (tokens, costs, message counts)
- `ClaudeHistoryAnalyzer`: Main analyzer class implementing core functionality

### Data Flow
1. **Discovery**: Scans Claude project directories (default: `~/.claude/projects`)
2. **Processing**: Parses JSONL files containing message history
3. **Deduplication**: Removes duplicate API responses from streaming/retry mechanisms
4. **Analysis**: Extracts token usage, calculates costs, aggregates by project/date/model
5. **Currency Conversion**: Handles multi-currency pricing and display conversion
6. **Reporting**: Generates formatted terminal output using Rich library

### Configuration System

**Model Pricing**: Stored in `model_pricing.yaml` with hierarchical matching and flexible pricing models:

- **Standard Pricing**: Simple per-million token rates (Claude, Gemini 1.5 Pro)
- **Multi-tier Pricing**: Multiple pricing tiers with custom thresholds (Gemini 2.5 Pro, Qwen3-Coder)
- **Multi-currency Support**: Models can specify their native currency (USD/CNY)
- **Exchange Rate Configuration**: Configurable USD-CNY exchange rate

**Pricing Model Types**:
1. **Standard Model** (sonnet, opus, gemini-1.5-pro):
   ```yaml
   sonnet:
     input_per_million: 3.0
     output_per_million: 15.0
     cache_read_per_million: 0.3
     cache_write_per_million: 3.75
   ```

2. **Multi-tier Model** (gemini-2.5-pro, qwen3-coder):
   ```yaml
   gemini-2.5-pro:
     tiers:
       - threshold: 200000    # ≤200K tokens (低档定价)
         input_per_million: 1.25
         output_per_million: 10.0
       - # >200K tokens (高档定价，无上限)
         input_per_million: 2.50
         output_per_million: 15.0
   
   qwen3-coder:
     currency: "CNY"  # Native pricing in Chinese Yuan
     tiers:
       - threshold: 32000     # ≤32K tokens
         input_per_million: 4.0
         output_per_million: 16.0
       - threshold: 128000    # ≤128K tokens
         input_per_million: 6.0
         output_per_million: 24.0
       - threshold: 256000    # ≤256K tokens
         input_per_million: 10.0
         output_per_million: 40.0
       - # >256K tokens (无上限)
         input_per_million: 20.0
         output_per_million: 200.0
   ```

**Currency Configuration**:
```yaml
currency:
  usd_to_cny: 7.3        # Exchange rate
  display_unit: "USD"    # Default display currency
```

**Command Line Options**:
- `--data-dir`: Claude projects directory path  
- `--max-days`: Daily statistics display days (0=all)
- `--max-projects`: Project statistics display count (0=all)
- `--currency`: Display currency (USD/CNY), overrides config file
- `--usd-to-cny`: Custom exchange rate, overrides config file
- `--log-level`: DEBUG/INFO/WARNING/ERROR
- `--export-json`: Export JSON format results

### Key Features

**Multi-Currency Cost Calculation**: 
- Models can specify native currency (USD/CNY)
- Automatic currency conversion for unified internal accounting
- Flexible display currency selection via command line or config

**Multi-tier Pricing Support**: 
- Standard single-rate pricing
- Multi-tier pricing with upper-bound thresholds
- Per-message tier determination based on first applicable threshold (≤ comparison)
- Omit threshold for unlimited upper tier (most concise format)
- Clean threshold values (32000, 128000, 256000) without awkward suffixes

**Cache Handling**: Separate pricing for cache read/write operations with model-specific rates

**Deduplication System**: Advanced duplicate detection to prevent double-counting of API responses:

- **Streaming Response Deduplication**: Claude's streaming API often generates multiple records for the same response, especially for cache operations. The tool detects and removes these duplicates using time-window analysis.

- **Cache Operation Deduplication**: 
  - Cache creation tokens are deduplicated when the same amount appears within the same minute
  - Cache read tokens follow the same deduplication logic
  - Prevents inflated costs from repeated cache billing in streaming responses

- **Message Pattern Deduplication**: 
  - Completely identical messages (same input, output, and cache tokens) within the same time window are treated as duplicates
  - Only the first occurrence counts toward message statistics
  - Subsequent duplicates contribute to token/cost statistics but not message counts

- **Debug Logging**: Use `--log-level DEBUG` to see deduplication actions:
  ```bash
  # View deduplication in action
  claude-cost --log-level DEBUG 2>&1 | grep -i "duplicate\|deduplicated"
  ```

- **Deduplication Impact**: Typically reduces reported costs by 30-40% and message counts by 20-40%, providing more accurate usage statistics that align with actual API billing.

**Time Zone Handling**: Converts UTC timestamps to local time for accurate daily statistics

**Rich Terminal Output**: Colorful tables with smart display logic:
- Automatic currency symbol selection ($ for USD, ¥ for CNY)
- Hides sections with no data (empty modules automatically hidden)
- Daily statistics only shown when historical data exists (excludes today-only scenarios) 
- Only displays dates with actual consumption (skips zero-cost days)
- Model statistics only shown when 2+ models are used (intelligent module hiding)

**Model Consumption Analytics**: 
- Individual model performance tracking (tokens, costs, message counts)
- Model ranking by cost for optimization insights
- Smart display: only shows when using 2 or more different models

**Model Matching Priority**: 
1. Exact match (case-insensitive)
2. Contains match (first match from top to bottom)
3. No match (cost = 0)

## Development Notes

- This is a single-file utility focused on analysis rather than a multi-module application
- Uses dataclasses extensively for structured data representation
- Multi-currency architecture with USD as internal accounting unit
- Support for both Chinese and international pricing models
- Advanced deduplication system to handle Claude API streaming responses and retries
- Dependencies are minimal: PyYAML for config, Rich for terminal output
- Chinese language interface and documentation (as seen in README.md)

### Code Quality Standards

**IMPORTANT**: After making any code changes, you MUST run the following command to ensure code quality:

```bash
uv run pyright claude_code_cost/
```

This command checks for:
- Type annotation errors (e.g., `str = None` should be `Optional[str] = None`)
- Import issues
- Type compatibility problems
- Other static analysis issues

The build should have **0 errors, 0 warnings, 0 informations** before considering the changes complete.

### Pre-commit Setup (Recommended)

To automatically run type checking before each commit:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

This will prevent commits that fail type checking, ensuring code quality at the source.
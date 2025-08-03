# Bible Gateway Downloader - (ByGoD) True Async Edition

A comprehensive, truly asynchronous tool for downloading Bible translations from BibleGateway.com in multiple formats (JSON, CSV, YAML, XML) with genuine parallel downloads, retry mechanisms, and flexible output options.

## 🚀 Features

- **True Async HTTP Requests**: Uses `aiohttp` for genuine parallelism, not just threading
- **Direct HTML Parsing**: Bypasses synchronous libraries to directly parse BibleGateway HTML
- **Multiple Translations**: Support for 30+ Bible translations (NIV, KJV, ESV, etc.)
- **Multiple Formats**: Output in JSON, CSV, YAML, and XML formats
- **Intelligent Rate Limiting**: Configurable concurrency with automatic rate limiting
- **Retry Mechanisms**: Exponential backoff with configurable retry attempts
- **Organized Output**: Structured directory organization by translation and format
- **Comprehensive Logging**: Colored, detailed progress tracking
- **Flexible Output Modes**: Download individual books, full Bibles, or both

## 📦 Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install bygod
```

### Option 2: Install from Source (Using Pipenv)

1. **Clone the repository**:
   ```bash
   git clone git@github.com:Christ-Is-The-King/bible-gateway-downloader.git
   cd bible-gateway-downloader
   ```

2. **Install pipenv** (if not already installed):
   ```bash
   pip install pipenv
   ```

3. **Install dependencies and activate virtual environment**:
   ```bash
   pipenv install
   pipenv shell
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

### Option 3: Install from Source (Using pip)

1. **Clone the repository**:
   ```bash
   git clone git@github.com:Christ-Is-The-King/bible-gateway-downloader.git
   cd bible-gateway-downloader
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

### Option 4: Build and Install Package

1. **Build the package**:
   ```bash
   python build_package.py
   ```

2. **Install the built package**:
   ```bash
   pip install dist/bygod-*.whl
   ```

## 🎯 Quick Start

### Basic Usage

Download a single translation in JSON format:
```bash
bygod --translations NIV --formats json
```

Download multiple translations in multiple formats:
```bash
bygod --translations NIV,KJV,ESV --formats json,csv,xml
```

Download specific books only:
```bash
bygod --translations NIV --books Genesis,Exodus,Psalms
```

### Advanced Usage

Download with custom rate limiting and retry settings:
```bash
bygod \
  --translations NIV,KJV \
  --formats json,csv \
  --rate-limit 10 \
  --retries 5 \
  --retry-delay 3 \
  --timeout 600
```

Download only individual books (no full Bible):
```bash
bygod --translations NIV --output-mode books
```

Download only full Bible (no individual books):
```bash
bygod --translations NIV --output-mode book
```

### Verbosity and Logging

Control output verbosity and error logging:

**Quiet mode (only errors):**
```bash
bygod --translations NIV -q
```

**Verbose mode (more detailed output):**
```bash
bygod --translations NIV -v
```

**Debug mode (maximum detail):**
```bash
bygod --translations NIV -vv
```

**Log errors to file:**
```bash
bygod --translations NIV --log-errors logs/bible_errors.log
```

**Set specific log level:**
```bash
bygod --translations NIV --log-level DEBUG
```

**Combine options:**
```bash
bygod --translations NIV -v --log-errors logs/errors.log --log-level WARNING
```

## 📋 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--translations` | Comma-separated list of Bible translations | `NIV` |
| `--formats` | Output formats: json, csv, xml, yaml | `json` |
| `--output-mode` | Output mode: book, books, all | `all` |
| `--output-dir` | Directory to save downloaded Bibles | `./bibles` |
| `--rate-limit` | Maximum concurrent requests | `5` |
| `--retries` | Maximum retry attempts | `3` |
| `--retry-delay` | Delay between retries (seconds) | `2` |
| `--timeout` | Request timeout (seconds) | `300` |
| `--books` | Comma-separated list of specific books | All books |
| `-v, --verbose` | Increase verbosity level (-v for INFO, -vv for DEBUG) | `0` |
| `-q, --quiet` | Suppress all output except errors | `False` |
| `--log-level` | Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `--log-errors` | Log errors to specified file in clean format | `None` |

## 📚 Supported Translations

The downloader supports 30+ Bible translations including:

- **NIV** - New International Version
- **KJV** - King James Version
- **ESV** - English Standard Version
- **NKJV** - New King James Version
- **NLT** - New Living Translation
- **CSB** - Christian Standard Bible
- **NASB** - New American Standard Bible
- **RSV** - Revised Standard Version
- **ASV** - American Standard Version
- **WEB** - World English Bible
- **YLT** - Young's Literal Translation
- **AMP** - Amplified Bible
- **MSG** - The Message
- **CEV** - Contemporary English Version
- **ERV** - Easy-to-Read Version
- **GW** - God's Word Translation
- **HCSB** - Holman Christian Standard Bible
- **ICB** - International Children's Bible
- **ISV** - International Standard Version
- **LEB** - Lexham English Bible
- **NCV** - New Century Version
- **NET** - New English Translation
- **NIRV** - New International Reader's Version
- **NRSV** - New Revised Standard Version
- **TLB** - The Living Bible
- **TLV** - Tree of Life Version
- **VOICE** - The Voice
- **WYC** - Wycliffe Bible

## 📁 Output Structure

The downloader creates a well-organized directory structure:

```
bibles/
├── NIV/
│   ├── NIV.json          # Full Bible in JSON
│   ├── NIV.csv           # Full Bible in CSV
│   ├── NIV.xml           # Full Bible in XML
│   ├── NIV.yml           # Full Bible in YAML
│   └── books/
│       ├── Genesis.json  # Individual book in JSON
│       ├── Genesis.csv   # Individual book in CSV
│       ├── Genesis.xml   # Individual book in XML
│       ├── Genesis.yml   # Individual book in YAML
│       └── ...
├── KJV/
│   ├── KJV.json
│   ├── KJV.csv
│   └── books/
│       └── ...
└── ...
```

## 🔧 Technical Details

### True Async Architecture

Unlike traditional threading approaches, this downloader uses:

- **`asyncio`**: Python's native async/await framework
- **`aiohttp`**: True async HTTP client for concurrent requests
- **Semaphores**: Rate limiting with configurable concurrency
- **`asyncio.gather()`**: Parallel execution of multiple downloads

### HTML Parsing

The downloader directly parses BibleGateway HTML using:

- **BeautifulSoup**: HTML parsing and navigation
- **CSS Selectors**: Multiple fallback selectors for verse extraction
- **Regex Patterns**: Chapter discovery and verse number detection

### Error Handling

- **Exponential Backoff**: Intelligent retry with increasing delays
- **Rate Limit Detection**: Automatic handling of 429 responses
- **Graceful Degradation**: Continues processing even if some downloads fail
- **Detailed Logging**: Comprehensive error reporting and progress tracking

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Using pipenv
pipenv run python tests.py

# Or using pip
python tests.py
```

The test suite includes:
- Single chapter downloads
- Single book downloads
- Multiple book parallel downloads
- True concurrency testing with multiple translations

## 📊 Performance

The true async architecture provides significant performance improvements:

- **Genuine Parallelism**: Multiple HTTP requests execute simultaneously
- **Efficient Resource Usage**: No thread overhead, uses event loop
- **Scalable Concurrency**: Configurable rate limits prevent server overload
- **Memory Efficient**: Streams responses without loading entire files into memory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Install dependencies using pipenv:
   ```bash
   pipenv install
   pipenv install --dev
   ```
4. Make your changes
5. Add tests for new functionality
6. Ensure all tests pass:
   ```bash
   pipenv run python tests.py
   ```
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- BibleGateway.com for providing Bible content
- The Python async community for excellent tools and documentation
- Contributors and users who provide feedback and improvements

## 🆘 Troubleshooting

### Common Issues

**Rate Limiting**: If you encounter 429 errors, reduce the `--rate-limit` value.

**Timeout Errors**: Increase the `--timeout` value for slower connections.

**Missing Verses**: Some translations may have different HTML structures. The parser includes multiple fallback methods.

**Memory Usage**: For large downloads, consider downloading fewer books at once or using a lower rate limit.

### Getting Help

- Check the logs for detailed error messages
- Try with a single translation and book first
- Ensure your internet connection is stable
- Verify that BibleGateway.com is accessible from your location 
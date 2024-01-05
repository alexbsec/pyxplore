# PyXplore

PyXplore is a versatile web fuzzer designed to explore and scan web applications by fuzzing for various resources such as directories, files, and services. It's built with Python and asyncio, allowing for concurrent requests and efficient scanning.

## Features
- Supports multiple modes for specialized fuzzing (PHP, ASP, ASPX, HTML, config files, UI configs, general, Apache, Nginx, JavaScript, routes, custom).
- Customizable status code grepping.
- Option to use wordlists for custom scanning.
- Supports both HTTP and HTTPS.
- Adjustable request delay and concurrency for controlled scanning.
- Output logging in JSON format.

## Installation
Clone the repository and install the necessary Python packages:
```bash
git clone https://github.com/alexbsec/pyxplore.git
cd pyxplore
pip install -r requirements.txt
```

## Usage

Run PyXplore with various command-line arguments to tailor the fuzzing process to your needs:

```bash
python pyxplore.py <mode> -u <url> [options]
```

### Arguments

    mode: The scanning mode (e.g., php, asp, custom).
    -u, --url: Target URL.
    -g, --grep-code: HTTP status codes to grep for.
    -o, --output: Output file for results.
    -d, --delay: Delay between requests in milliseconds.
    -S, --use-small: Use a smaller wordlist for quicker scans.
    -s, --silent: Silent mode (less output).
    -w, --wordlist: Custom wordlist for fuzzing.
    -x, --ext: File extension for fuzzing.
    --no-ssl: Disable SSL for requests.
    --concurrent-count: Number of concurrent requests.

## Example

```bash
python pyxplore.py php -u https://example.com -g 200,404 -o results --concurrent-count 15
```

## Contributions

Contributions are welcome! Feel free to submit pull requests or open issues to improve the tool or add new features.
Right now, I'm working on adding other online wordlists to xrequests.py.
[![Deploy to PyPI with tag](https://github.com/call518/LogSentinelAI/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/call518/LogSentinelAI/actions/workflows/pypi-publish.yml)

# LogSentinelAI - LLM-Powered Log Analyzer for Security Events and Anomalies

LogSentinelAI leverages LLM to analyze security events, anomalies, and errors from various logs including Apache, Linux, and converts them into structured data that can be visualized with Elasticsearch/Kibana.

## 🚀 Key Features

> ⚡️ **Declarative Extraction**
>
> In each analyzer script, simply declare the desired result structure as a Pydantic class, and the LLM will automatically analyze logs and return results as JSON matching that schema. No complex parsing or post-processing—just declare what you want, and the AI handles the rest. This approach enables developers to focus on "what to extract" declaratively, while the LLM takes care of "how to extract"—a modern paradigm for information extraction.
```python
# Example: Just declare the result structure you want in your HTTP Access log analyzer
from pydantic import BaseModel

class MyAccessLogResult(BaseModel):
    ip: str
    url: str
    is_attack: bool

# By defining only the result structure (Pydantic class) like above,
# the LLM automatically analyzes each log and returns JSON like this:
# {
#   "ip": "192.168.0.1",
#   "url": "/admin.php",
#   "is_attack": true
# }
```

### AI-powered Analysis
- **Declarative Extraction**: Just declare your desired result structure (Pydantic class) and the LLM analyzes logs automatically
- **LLM Providers**: OpenAI API, Ollama, vLLM
- **Supported Log Types**: HTTP Access, Apache Error, Linux System, TCPDump
- **Threat Detection**: SQL Injection, XSS, Brute Force, Network Anomaly Detection
- **Output**: Structured JSON validated by Pydantic
- **Just define a Pydantic class and the LLM generates results in that structure automatically**
- **Adaptive Sensitivity**: Detection sensitivity auto-adjusted by LLM model and log type prompt

### Processing Modes
- **Batch**: Bulk analysis of historical logs
- **Real-time**: Sampling-based live monitoring
- **Access Methods**: Local files, SSH remote

### Data Enrichment
- **GeoIP**: MaxMind GeoLite2 City lookup (including coordinates, Kibana geo_point support)
- **Statistics**: IP counts, response codes, various metrics
- **Multi-language Support**: Configurable result language (default: Korean)

### Enterprise Integration
- **Storage**: Elasticsearch (ILM policy support)
- **Visualization**: Kibana dashboard
- **Deployment**: Docker containers

## Dashboard Example

![Kibana Dashboard](img/ex-dashboard.png)

## 📋 JSON Output Example

![JSON Output](img/ex-json.png)

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Log Sources   │───>│ LogSentinelAI   │───>│ Elasticsearch   │
│                 │    │   Analysis      │    │                 │
│ • Local Files   │    │                 │    │ • Security      │
│ • Remote SSH    │    │ • LLM Analysis  │    │   Events        │
│ • HTTP Access   │    │ • Outlines      │    │ • Raw Logs      │
│ • Apache Error  │    │ • Pydantic      │    │ • Metadata      │
│ • System Logs   │    │   Validation    │    │                 │
│ • TCPDump       │    │ • Multi-format  │    │                 │
│   (Auto-detect) │    │   Support       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ LLM Provider    │    │     Kibana      │
                       │                 │    │   Dashboard     │
                       │ • OpenAI        │    │                 │
                       │ • Ollama        │    │ • Visualization │
                       │ • vLLM          │    │ • Alerts        │
                       │                 │    │ • Analytics     │
                       │                 │    │ • Geo-Map       │
                       └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure and Main Python Scripts

### Core Python Components

```
src/logsentinelai/
├── __init__.py                    # Package initialization
├── cli.py                         # Main CLI entry point and command routing
├── py.typed                       # mypy type hint marker
│
├── analyzers/                     # Log type-specific analyzers
│   ├── __init__.py                # Analyzer package initialization
│   ├── httpd_access.py            # HTTP access log analyzer (Apache/Nginx)
│   ├── httpd_apache.py            # Apache error log analyzer
│   ├── linux_system.py            # Linux system log analyzer (syslog/messages)
│   └── tcpdump_packet.py          # Network packet capture analyzer
│
├── core/                          # Core analysis engine (modularized)
│   ├── __init__.py                # Core package initialization and integrated import
│   ├── commons.py                 # Batch/real-time analysis common functions, processing flow definition
│   ├── config.py                  # Environment variable-based configuration management
│   ├── llm.py                     # LLM model initialization and interaction
│   ├── elasticsearch.py           # Elasticsearch integration and data transmission
│   ├── geoip.py                   # GeoIP lookup and IP enrichment
│   ├── ssh.py                     # SSH remote log access
│   ├── monitoring.py              # Real-time log monitoring and processing
│   ├── utils.py                   # Log processing utilities and helpers
│   └── prompts.py                 # Log type-specific LLM prompt templates
│
└── utils/                         # Utility functions
    ├── __init__.py                # Utils package initialization
    └── geoip_downloader.py        # MaxMind GeoIP DB downloader
```

### CLI Command Mapping

```bash
# CLI commands are mapped to analyzer scripts:
logsentinelai-httpd-access   → analyzers/httpd_access.py
logsentinelai-apache-error   → analyzers/httpd_apache.py  
logsentinelai-linux-system   → analyzers/linux_system.py
logsentinelai-tcpdump        → analyzers/tcpdump_packet.py
logsentinelai-geoip-download → utils/geoip_downloader.py
```

### 📑 Sample Log Preview

#### HTTP Access Log
```
54.36.149.41 - - [22/Jan/2019:03:56:14 +0330] "GET /filter/27|13%20%D9%85%DA%AF%D8%A7%D9%BE%DB%8C%DA%A9%D8%B3%D9%84,27|%DA%A9%D9%85%D8%AA%D8%B1%20%D8%A7%D8%B2%205%20%D9%85%DA%AF%D8%A7%D9%BE%DB%8C%DA%A9%D8%B3%D9%84,p53 HTTP/1.1" 200 30577 "-" "Mozilla/5.0 (compatible; AhrefsBot/6.1; +http://ahrefs.com/robot/)" "-"
31.56.96.51 - - [22/Jan/2019:03:56:16 +0330] "GET /image/60844/productModel/200x200 HTTP/1.1" 200 5667 "https://www.zanbil.ir/m/filter/b113" "Mozilla/5.0 (Linux; Android 6.0; ALE-L21 Build/HuaweiALE-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36" "-"
31.56.96.51 - - [22/Jan/2019:03:56:16 +0330] "GET /image/61474/productModel/200x200 HTTP/1.1" 200 5379 "https://www.zanbil.ir/m/filter/b113" "Mozilla/5.0 (Linux; Android 6.0; ALE-L21 Build/HuaweiALE-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36" "-"
40.77.167.129 - - [22/Jan/2019:03:56:17 +0330] "GET /image/14925/productModel/100x100 HTTP/1.1" 200 1696 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" "-"
91.99.72.15 - - [22/Jan/2019:03:56:17 +0330] "GET /product/31893/62100/%D8%B3%D8%B4%D9%88%D8%A7%D8%B1-%D8%AE%D8%A7%D9%86%DA%AF%DB%8C-%D9%BE%D8%B1%D9%86%D8%B3%D9%84%DB%8C-%D9%85%D8%AF%D9%84-PR257AT HTTP/1.1" 200 41483 "-" "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0)Gecko/16.0 Firefox/16.0" "-"
40.77.167.129 - - [22/Jan/2019:03:56:17 +0330] "GET /image/23488/productModel/150x150 HTTP/1.1" 200 2654 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" "-"
40.77.167.129 - - [22/Jan/2019:03:56:18 +0330] "GET /image/45437/productModel/150x150 HTTP/1.1" 200 3688 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" "-"
40.77.167.129 - - [22/Jan/2019:03:56:18 +0330] "GET /image/576/article/100x100 HTTP/1.1" 200 14776 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" "-"
66.249.66.194 - - [22/Jan/2019:03:56:18 +0330] "GET /filter/b41,b665,c150%7C%D8%A8%D8%AE%D8%A7%D8%B1%D9%BE%D8%B2,p56 HTTP/1.1" 200 34277 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "-"
40.77.167.129 - - [22/Jan/2019:03:56:18 +0330] "GET /image/57710/productModel/100x100 HTTP/1.1" 200 1695 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" "-"
```

#### Apache Error Log
```
[Thu Jun 09 06:07:04 2005] [notice] LDAP: Built with OpenLDAP LDAP SDK
[Thu Jun 09 06:07:04 2005] [notice] LDAP: SSL support unavailable
[Thu Jun 09 06:07:04 2005] [notice] suEXEC mechanism enabled (wrapper: /usr/sbin/suexec)
[Thu Jun 09 06:07:05 2005] [notice] Digest: generating secret for digest authentication ...
[Thu Jun 09 06:07:05 2005] [notice] Digest: done
[Thu Jun 09 06:07:05 2005] [notice] LDAP: Built with OpenLDAP LDAP SDK
[Thu Jun 09 06:07:05 2005] [notice] LDAP: SSL support unavailable
[Thu Jun 09 06:07:05 2005] [error] env.createBean2(): Factory error creating channel.jni:jni ( channel.jni, jni)
[Thu Jun 09 06:07:05 2005] [error] config.update(): Can't create channel.jni:jni
[Thu Jun 09 06:07:05 2005] [error] env.createBean2(): Factory error creating vm: ( vm, )
```

#### Linux System Log
```
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4 
Jun 14 15:16:02 combo sshd(pam_unix)[19937]: check pass; user unknown
Jun 14 15:16:02 combo sshd(pam_unix)[19937]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4 
Jun 15 02:04:59 combo sshd(pam_unix)[20882]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=220-135-151-1.hinet-ip.hinet.net  user=root
Jun 15 02:04:59 combo sshd(pam_unix)[20884]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=220-135-151-1.hinet-ip.hinet.net  user=root
Jun 15 02:04:59 combo sshd(pam_unix)[20883]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=220-135-151-1.hinet-ip.hinet.net  user=root
Jun 15 02:04:59 combo sshd(pam_unix)[20885]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=220-135-151-1.hinet-ip.hinet.net  user=root
Jun 15 02:04:59 combo sshd(pam_unix)[20886]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=220-135-151-1.hinet-ip.hinet.net  user=root
Jun 15 02:04:59 combo sshd(pam_unix)[20892]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=220-135-151-1.hinet-ip.hinet.net  user=root
Jun 15 02:04:59 combo sshd(pam_unix)[20893]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=220-135-151-1.hinet-ip.hinet.net  user=root
```

#### TCPDump Packet Log
```
2025-07-20 14:00:00.228603 IP 150.165.103.133.443 > 163.62.4.236.54372: Flags [P.], seq 2408409918:2408411378, ack 41863130, win 32850, length 1460
    0x0000:  6c6c d367 9a69 100e 7ecb 53f0 0800 4500  ll.g.i..~.S...E.
    0x0010:  05dc ae4a 4000 3906 e77c 96a5 6785 a33e  ...J@.9..|..g..>
    0x0020:  04ec 01bb d464 8f8d 6b3e 027e c7da 5018  .....d..k>.~..P.
    0x0030:  8052 1642 0000                           .R.B..
2025-07-20 14:00:00.228605 IP 192.242.209.255.5830 > 52.107.241.218.443: Flags [P.], seq 229435932:229435963, ack 245183773, win 2048, options [nop,nop,TS val 1083882715 ecr 5831867], length 31
    0x0000:  6c6c d367 9a69 100e 7ecb 53f0 0800 4500  ll.g.i..~.S...E.
    0x0010:  0053 0000 4000 3906 886d c0f2 d1ff 346b  .S..@.9..m....4k
    0x0020:  f1da 16c6 01bb 0dac ea1c 0e9d 351d 8018  ............5...
    0x0030:  0800 b76e 0000 0101 080a 409a bcdb 0058  ...n......@....X
```

## Installation Guide

For installation, environment setup, CLI usage, Elasticsearch/Kibana integration, and all practical guides for LogSentinelAI, please refer to the installation documentation below.

**[Go to Installation and Usage Guide: INSTALL.en.md](./INSTALL.en.md)**

> ⚡️ For additional inquiries, please use GitHub Issues/Discussions!

## Acknowledgments

We would like to express our sincere gratitude to the following projects and communities that provided inspiration, guidance, and foundational technologies for LogSentinelAI:

### Core Technologies & Frameworks
- **[Outlines](https://dottxt-ai.github.io/outlines/latest/)** - Structured LLM output generation framework that powers our reliable AI analysis
- **[dottxt-ai Demos](https://github.com/dottxt-ai/demos/tree/main/logs)** - Excellent log analysis examples and implementation patterns
- **[Docker ELK Stack](https://github.com/deviantony/docker-elk)** - Comprehensive Elasticsearch, Logstash, and Kibana Docker setup

### LLM Infrastructure & Deployment
- **[vLLM](https://github.com/vllm-project/vllm)** - High-performance LLM inference engine for GPU-accelerated local deployment
- **[Ollama](https://ollama.com/)** - Simplified local LLM deployment and management platform

### Open Source Community
We are deeply grateful to the broader open source community and the countless projects that have contributed to making AI-powered log analysis accessible and practical. This project stands on the shoulders of many innovative open source initiatives that continue to push the boundaries of what's possible.
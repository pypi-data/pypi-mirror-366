# ChaosInjector 🚀

🇺🇸 [English](README.md) | 🇷🇺 [Русский](README.ru.md)

### Community and Support

📢 Join the author's Telegram channel [@almost_it](https://t.me/almost_it) for
insights on Python development, chaos engineering discussions, library updates,
and behind-the-scenes thoughts on innovative coding practices.

📄 [CHANGELOG](CHANGELOG.md)

[![PyPI version](https://badge.fury.io/py/chaosinjector.svg)](https://badge.fury.io/py/chaosinjector)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Downloads](https://pepy.tech/badge/chaosinjector)](https://pepy.tech/project/chaosinjector)

**Inject Chaos, Control Uncertainty – Revolutionize Your Python Code with
Probabilistic Proxies!**

Imagine turning any Python object into a probabilistic powerhouse: methods
that "flake out" randomly, logs that sample themselves, tests that simulate
real-world failures without a single line of mocking code. **ChaosInjector** is
the ultimate tool for developers who crave dynamic, resilient, and innovative
code. Whether you're hardening your app against flakiness, optimizing
performance through sampling, or adding randomness to simulations and games –
ChaosInjector makes it effortless and elegant.

Why settle for static code when you can embrace controlled chaos? Join the ranks
of forward-thinking devs using ChaosInjector to supercharge testing, logging, AI
behaviors, and more. **Install now and unlock the power of probability!**

## Why ChaosInjector? 🔥

In a world of unpredictable systems, ChaosInjector gives you the edge:

- **Fault Injection on Steroids**: Simulate flaky networks, databases, or APIs
  with a single line – perfect for robust unit/integration tests.
- **Performance Sampling Magic**: Reduce overhead in logging, tracing, or
  analytics by executing only X% of the time.
- **Stochastic Simulations**: Add realistic randomness to games, ML models, or
  Monte Carlo methods without rewriting logic.
- **A/B Testing Simplified**: Roll out features probabilistically, no complex
  infra needed.
- **Privacy & Security Boost**: Anonymize sensitive data accesses randomly for
  compliance and honeypots.

Built with Python's dynamic magic (runtime class proxying
via `__getattribute__`), ChaosInjector is lightweight, zero-dependency, and
battle-tested with full coverage. It's not just a library – it's your secret
weapon for smarter, more adaptive code.

## Quick Start ⚡

### Installation

Get started in seconds:

```bash
pip install chaosinjector
```

### Basic Usage

Suppress logs probabilistically? Easy!

```python
import logging
from chaosinjector import ChaosInjector


logger = logging.getLogger("my_app")
ChaosInjector.inject(logger, probability=0.1)  # Only 10% chance logs execute

logger.info("This might not log!")  # Flaky by design!
```

Want more control? Use deciders or per-method probs:

```python
ChaosInjector.inject(
    logger, method_probs={"info": 0.0, "error": 1.0}
)  # Info always skipped, errors always log
```

Or custom logic:

```python
ChaosInjector.inject(
    logger, decider=lambda name: "debug" not in name
)  # Skip all debug methods
```

### Creating a Proxy Without Mutating the Original

For cases where you need to keep the original object untouched,
use `create_proxy`, which returns a new object with chaos applied, preserving
type hints:

```python
import logging
from chaosinjector import ChaosInjector


original_logger = logging.getLogger("my_app")
chaos_logger = ChaosInjector.create_proxy(original_logger, probability=0.1)

chaos_logger.info("This log is flaky in the proxy!")  # 10% chance in proxy
original_logger.info("This log always works!")  # Original untouched
```

## Features at a Glance 🌟

- **Probabilistic Attribute Access**: Return real attributes/methods with
  tunable probability (0.0-1.0).
- **Custom Deciders**: Pass a callable to decide per-attribute (e.g., based on
  name, env vars, or time).
- **Per-Method Granularity**: Dict of method-specific probabilities for
  fine-tuned control.
- **Safe No-Op Handling**: Callables become silent lambdas; non-callables return
  None – no crashes!
- **Validation Built-In**: Ensures probabilities are valid (0-1), preventing
  silent errors.
- **Type Preservation**: Proxies maintain isinstance compatibility with the
  original type, including generics and type hints.
- **Dual Modes**: In-place mutation via `inject` or non-destructive proxy
  via `create_proxy`.
- **Lightweight & Pure Python**: No dependencies, works with Python 3.8+.
- **Extensively Tested**: 100% coverage with pytest, including mocked randomness
  for determinism.

## Real-World Examples 💡

### 1. Fault Injection in Tests

Simulate unreliable services:

```python
import requests
from chaosinjector import ChaosInjector


session = requests.Session()
ChaosInjector.inject(session, probability=0.3)  # 70% failure rate

response = session.get(
    "https://api.example.com"
)  # Often None – test your retries!
```

Or without mutation:

```python
chaos_session = ChaosInjector.create_proxy(session, probability=0.3)
response = chaos_session.get("https://api.example.com")  # Flaky only in proxy
```

### 2. Sampling Expensive Operations

Optimize tracing:

```python
from opentelemetry import trace
from chaosinjector import ChaosInjector


tracer = trace.get_tracer(__name__)
ChaosInjector.inject(tracer, probability=0.1)  # Trace only 10% of calls

with tracer.start_as_current_span("operation"):  # Sometimes no-op
    pass
```

With proxy:

```python
chaos_tracer = ChaosInjector.create_proxy(tracer, probability=0.1)
with chaos_tracer.start_as_current_span(
    "operation"
):  # Flaky in proxy, original intact
    pass
```

### 3. Probabilistic AI in Games

Add unpredictability:

```python
class NPC:
    def attack(self):
        print("Boom!")


npc = NPC()
ChaosInjector.inject(
    npc, method_probs={"attack": 0.7}
)  # Attacks 70% of the time

npc.attack()  # Maybe... maybe not!
```

With proxy:

```python
chaos_npc = ChaosInjector.create_proxy(npc, method_probs={"attack": 0.7})
chaos_npc.attack()  # Flaky in proxy, original npc stable
```

### 4. Data Privacy Masking

Anonymize sensitive fields:

```python
class UserData:
    user_id = "sensitive123"


data = UserData()
ChaosInjector.inject(
    data, decider=lambda name: name != "user_id"
)  # user_id always None

print(data.user_id)  # None – protected!
```

With proxy:

```python
chaos_data = ChaosInjector.create_proxy(
    data, decider=lambda name: name != "user_id"
)
print(chaos_data.user_id)  # None in proxy, original untouched
```

Explore more in our [docs](https://chaosinjector.readthedocs.io) (coming soon)!

## Contributing 🤝

Love ChaosInjector? Help make it better! Fork the repo, add features/tests, and
submit a PR.

- Report
  issues: [GitHub Issues](https://github.com/vproyaev/chaosinjector/issues)
- Star the repo: ⭐️
- Spread the word: Share on X or Reddit!

## License 📄

Released under the [MIT License](LICENSE). Free to use, modify, and distribute.

---

**Ready to inject chaos into your code?** Install ChaosInjector today and turn
uncertainty into your superpower. Questions? Hit us up in issues – we're here to
help! 🚀
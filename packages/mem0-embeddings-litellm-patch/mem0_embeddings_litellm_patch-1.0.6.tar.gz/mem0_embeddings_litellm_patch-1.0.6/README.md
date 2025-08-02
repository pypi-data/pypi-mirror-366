# mem0-embeddings-litellm-patch

This patch adds support for embedding model providers via [LiteLLM](https://github.com/BerriAI/litellm) to the [mem0](https://github.com/mem0-ai/mem0) framework.

## ✨ What It Does

- Integrates nearly all providers supported by LiteLLM as embedding backends in mem0
- Enables use of high-performance providers like **VoyageAI**, **Mistral**, **Groq**, and more
- Drop-in replacement for the existing embedding logic

## 🔧 Installation

You can install the patch via pip:

```bash
pip install mem0-embeddings-litellm-patch
````

This will patch the necessary `mem0.embeddings` modules automatically.

> **Note:** Make sure `mem0` and `litellm` are installed as dependencies. This package does not install them implicitly.

## 🧠 Requirements

* Python >= 3.8
* `mem0` >= 0.1.0
* `litellm` >= 1.0.0

## 💡 Usage

After installing this patch you can use all embedding providers available via litellm inncluding those currently not supported via mem0 natively. 

## 📢 Why This Exists

The mem0 maintainers have not yet merged support for LiteLLM-based embeddings, despite it being a fast, extensible abstraction layer.
This patch bridges the gap until (or if) native support is added upstream. No need to fork and maintain a full project if you can just maintain the patch files instead am i right? :D No need to fork and maintain a full project if you can just maintain the patch files instead am i right? :D

## 📬 Feedback / Contributing

Feel free to fork or open issues. If the mem0 team integrates this feature officially, this package may be deprecated in favor of upstream support.

---

Licensed under the MIT License.


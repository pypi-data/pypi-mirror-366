# ailia LLM Python API

!! CAUTION !!
“ailia” IS NOT OPEN SOURCE SOFTWARE (OSS).
As long as user complies with the conditions stated in [License Document](https://ailia.ai/license/), user may use the Software for free of charge, but the Software is basically paid software.

## About ailia LLM

ailia LLM is a library for running LLMs on edge devices. It provides bindings for C++ and Unity.

## Install from pip

You can install the ailia LLM free evaluation package with the following command.

```
pip3 install ailia_llm
```

## Install from package

You can install the ailia LLM from Package with the following command.

```
python3 bootstrap.py
pip3 install ./
```

## Usage

```python
import ailia_llm

import os
import urllib.request

model_file_path = "gemma-2-2b-it-Q4_K_M.gguf"
if not os.path.exists(model_file_path):
	urllib.request.urlretrieve(
		"https://storage.googleapis.com/ailia-models/gemma/gemma-2-2b-it-Q4_K_M.gguf",
		model_file_path
	)

model = ailia_llm.AiliaLLM()
model.open(model_file_path)

messages = []
messages.append({"role": "system", "content": "語尾に「わん」をつけてください。"})
messages.append({"role": "user", "content": "あなたの名前は何ですか？"})

stream = model.generate(messages)

text = ""
for delta_text in stream:
	text = text + delta_text
print(text)

if model.context_full():
	raise Exception("Context full")

messages.append({"role": "assistant", "content": text})
```

## API specification

https://github.com/axinc-ai/ailia-sdk


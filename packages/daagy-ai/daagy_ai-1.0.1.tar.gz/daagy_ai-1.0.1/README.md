# Daagy - Your AI Terminal Assistant

**Daagy** is a terminal-based AI assistant that follows natural language instructions to perform system tasks, answer questions, and much more.


## 🚀 Features

- Command-line based natural language interface  
- Capable of performing a vast range of tasks – from system operations to smart utilities and beyond
- Handles general knowledge questions without running system commands  
- Best experience on **Linux**

## 🖥️ Usage

Just type in your terminal:

```bash
$ daagy 'your task here'
```

or use `ques` to ask general questions that do not require running a command:

```bash
$ daagy ques 'your question here'
```

## 🛠️ Installation

```bash
$ pip install daagy-ai
```

## 📦 Requirements

- Python 3.x  
- Gemini API Key  
- Required Python package:

```bash
$ pip install -q -U google-genai
```

## 🔐 Gemini API Key Setup

On first run, Daagy will prompt you to enter your [Gemini API key](https://aistudio.google.com/app/apikey).  
This is a **one-time setup** — the key will be saved locally for future use.

## ⚠️ Notes

- Optimized for **Linux**  
- Limited support on **Windows**

## 🧪 Sample Commands

``` bash

$ daagy make a node server to handle login

$ daagy make a file named xyz.txt and write hello world 10 times in it

$ daagy delete a folder named useless_folder

$ daagy install a calendar

$ daagy ques who is the PM of INDIA
```
...and so much more.

Daagy understands natural language — just tell it what you want.


### 🛠️ Note for Linux Users

If you get `daagy: command not found`, run the following command and try again. 

```bash
export PATH="$HOME/.local/bin:$PATH"
```


## 😏 Just Saying...
> ⚠️ Curious minds beware: commands like `daagy do something nasty` will do *something* — but you might not want to find out what.


## 📄 License

MIT
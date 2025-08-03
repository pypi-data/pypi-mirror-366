# 🧬 bioai-seq

`bioai-seq` is a lightweight command-line tool for basic biological sequence analysis. It’s part of my journey toward becoming a **Bio AI Software Engineer** — combining software engineering, biology, and machine learning.

---

## 💻 Local Development & Testing

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install required build tools

```bash
pip install --upgrade pip setuptools build
```

### 3. Run the CLI locally

Run the CLI directly:

```bash
python3 -m bioai_seq.cli
```

Or install locally and use as a command:

```bash
pip install .
bioseq
```

---

## 🚀 Deploying to PyPI (Production)

### 1. Clean previous builds

```bash
rm -rf dist build *.egg-info
```

### 2. Build the package

```bash
python3 -m build
```

### 3. Upload to PyPI

```bash
pip install --upgrade twine
twine upload dist/*
```

- Username: `__token__`
- Password: your API token from [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)

---

## 📦 Installation (User Guide)

```bash
pip install bioai-seq
```

Then run:

```bash
bioseq
```

---

## 🧪 Planned Example Output

```txt
✅ Sequence loaded: 1273 amino acids
🧬 Detected: SARS-CoV-2 spike protein (likely variant: Omicron)
🔍 Running ESM-2 embeddings...
🧪 Predicted secondary structure: 40% alpha-helix, 25% beta-sheet
🧬 Mutation sites detected vs reference: 15
📚 Similar sequences:
 - UniProt P0DTC2 (99.7%)
 - UniProt A0A6H2L9T9 (98.9%)
🧠 Summary:
"This sequence appears to be a mutated spike protein, likely from a recent SARS-CoV-2 variant. Multiple substitutions are present in the RBD region."
```

---

## 🌐 Follow the Journey

This project is part of a broader initiative to define and grow the **Bio AI Software Engineer** role.

- 🌍 Blog: [https://bioaisoftware.engineer](https://bioaisoftware.engineer)
- 🧑‍💻 GitHub: [https://github.com/babilonczyk](https://github.com/babilonczyk)
- 💼 LinkedIn: [https://www.linkedin.com/in/jan-piotrzkowski/](https://www.linkedin.com/in/jan-piotrzkowski/)

---

## 🛠️ License

MIT — free to use, share, and improve.

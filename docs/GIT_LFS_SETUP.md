# 📂 Git LFS Setup Guide for MedLitBot

## 🎯 Overview

MedLitBot uses **Git LFS (Large File Storage)** to manage trained model files efficiently. The trained models are large files (433MB) that would bloat the repository if stored directly in Git.

## ⚠️ Common Issue: 134-byte Model Files

When you clone the repository, you might see that `model.safetensors` appears as only **134 bytes** instead of ~433MB. This is **normal Git LFS behavior** - you're seeing a "pointer file" instead of the actual model.

## 🛠️ Solution

### For New Users Cloning the Repository:

```bash
# 1. Clone the repository
git clone https://github.com/DiegoBerSource/medlitbot.git
cd medlitbot

# 2. Download large model files (REQUIRED!)
git lfs pull

# 3. Verify models are downloaded
ls -lh media/trained_models/model_24_model/model.safetensors
# Should show: -rw-r--r-- 1 user staff 433M Aug 25 04:09 model.safetensors
```

### For Existing Clones Missing Models:

```bash
# Download the actual model files
git lfs pull

# Check file sizes
du -h media/trained_models/
```

## 🔍 How to Verify Models Are Working

### Check File Sizes:
```bash
ls -lh media/trained_models/
```

Expected output:
```
total 846792
-rw-r--r--  1 user  staff   3.2M Aug 25 19:44 model_13.pkl
-rw-r--r--  1 user  staff   199B Aug 25 19:44 model_24_metadata.json
drwxr-xr-x  7 user  staff   224B Aug 25 04:05 model_24_model/
```

```bash
ls -lh media/trained_models/model_24_model/
```

Expected output:
```
total 846792
-rw-r--r--  1 user  staff   843B Aug 25 04:09 config.json
-rw-r--r--  1 user  staff   433M Aug 25 04:09 model.safetensors  # ← Should be 433M
-rw-r--r--  1 user  staff   125B Aug 25 04:09 special_tokens_map.json
-rw-r--r--  1 user  staff   1.3K Aug 25 04:09 tokenizer_config.json
-rw-r--r--  1 user  staff   213K Aug 25 04:09 vocab.txt
```

### Test Model Loading:
```bash
python -c "
from safetensors import safe_open
with safe_open('media/trained_models/model_24_model/model.safetensors', framework='pt', device='cpu') as f:
    print(f'✅ Model loaded successfully! Contains {len(f.keys())} parameters')
"
```

Expected output:
```
✅ Model loaded successfully! Contains 201 parameters
```

## 🔧 Troubleshooting

### Issue: "Models not found" errors
**Solution**: Run `git lfs pull` to download the actual model files.

### Issue: Git LFS not installed
```bash
# Install Git LFS (one time setup)
git lfs install

# Then download models
git lfs pull
```

### Issue: Models still 134 bytes after `git lfs pull`
```bash
# Check if LFS is properly configured
git lfs ls-files
# Should show: c47aa14446 * media/trained_models/model_24_model/model.safetensors

# Force re-download
git lfs pull --force
```

## 📊 What's in the Models?

### Traditional ML Model (`model_13.pkl`):
- **Type**: Scikit-learn SVM model
- **Size**: ~3.2MB
- **Accuracy**: 73.6%
- **F1-Score**: 84.8%

### BERT Transformer (`model_24_model/`):
- **Type**: BioBERT medical specialist
- **Size**: 433MB
- **Accuracy**: 82.6%
- **F1-Score**: 92.7%
- **Base Model**: `dmis-lab/biobert-base-cased-v1.1`

## 🚀 Why We Use Git LFS

### Benefits:
- ✅ **Smaller repository**: Clones are faster
- ✅ **Version control**: Models are still tracked
- ✅ **Bandwidth efficient**: Only download when needed
- ✅ **Storage efficient**: Large files stored separately

### Without Git LFS:
- ❌ **Huge repository**: 433MB+ for each commit
- ❌ **Slow clones**: Long download times
- ❌ **Storage waste**: Multiple versions stored locally

## 💡 For Contributors

If you're adding new trained models:

```bash
# Make sure .gitattributes includes:
echo "*.safetensors filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
echo "*.pkl filter=lfs diff=lfs merge=lfs -text" >> .gitattributes

# Add and commit large files
git add media/trained_models/new_model.safetensors
git commit -m "Add new trained model"

# Push with LFS
git push origin main
```

---

**💡 Remember**: Always run `git lfs pull` after cloning to get the actual trained models!

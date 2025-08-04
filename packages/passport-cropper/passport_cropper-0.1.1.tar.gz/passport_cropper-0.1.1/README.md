# Passport Cropper 🪪📷
Automatically crop passport-style photos from scanned forms or images using face detection and image orientation correction.. Ensures correct orientation, centers the face, and optionally compresses the image to stay within a specified file size (e.g., under 100KB). Ideal for scanned documents, selfies, or batch passport photo generation.

This tool detects a face in a scanned form (even if rotated), intelligently crops the surrounding area to form a clean passport-size photo, and optionally compresses it to stay under a specified file size.

---

## ✨ Features

- 🧠 Face detection using OpenCV
- 📐 Intelligent orientation correction (handles rotated/scanned forms)
- ✂️ Crops a clean passport-style image around the face
- 💾 Automatically resizes/compresses image under a max file size (optional)
- 🛠️ Easy to use as a library or script
- 🐍 Open Source and available on PyPI


## 📦 Installation

```bash
pip install passport-cropper
````

---

## 🧑‍💻 Usage

```python
from passport_cropper import crop_passport_photo

# Crop and save image from scanned form
cropped = crop_passport_photo(
    image_path="admission_form.jpg",
    output_path="passport_photo.jpg",
    max_size_kb=100   # Optional - limit output image size
)
# No face detected if cropped is None.

if cropped:
  print("Image processed successfully!")
```

You can also run it directly as a script (CLI version coming soon):

```bash
python -m passport_cropper path/to/form.jpg
```

---

## 🖼️ Input / Output Example

**Input:**
Scanned or mobile photo of an admission form (rotated, tilted, or normal)

**Output:**
Clean, upright, passport-style photo of the face cropped and optionally compressed.

---

## 📁 Project Structure

```
passport_cropper/
├── passport_cropper/
│   ├── __init__.py
│   └── cropper.py
├── examples/
├── README.md
├── LICENSE
├── setup.py
├── requirements.txt
```

---

## ⚙️ Parameters

| Parameter     | Type  | Description                                  |
| ------------- | ----- | -------------------------------------------- |
| `image_path`  | `str` | Path to the input image                      |
| `output_path` | `str` | Path to save the cropped passport image      |
| `max_size_kb` | `int` | (Optional) Max size (in KB) for output image |

---

## 🔧 Requirements

* Python 3.7+
* OpenCV

Install via:

```bash
pip install -r requirements.txt
```

---

## 🛡️ License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributing

Pull requests are welcome! If you find a bug or want a new feature, feel free to [open an issue](https://github.com/abhaybraja/passport-cropper/issues) or submit a PR.

---

## 🌐 Links

* 📦 PyPI: [https://pypi.org/project/passport-cropper](https://pypi.org/project/passport-cropper)
* 💻 GitHub: [https://github.com/abhaybraja/passport-cropper](https://github.com/abhaybraja/passport-cropper)

---

## ✍️ Author

Developed with ❤️ by [Abhay Braja](https://github.com/abhaybraja)

```
Let me know if you'd like me to insert your actual name and GitHub username, or generate a minimal working CLI wrapper too.
```

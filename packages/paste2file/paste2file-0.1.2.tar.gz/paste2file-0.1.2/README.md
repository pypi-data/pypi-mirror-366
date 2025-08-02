# 📋✨ Paste2file - The Ultimate Clipboard Magic! ✨📋

> *"Life is short, save your clipboard faster than a magical girl transformation!"* 🌟

## 🎯 Mission Statement

**TLDR:** Press `Ctrl+Shift+V` to instantly save clipboard content to Desktop! No more tedious file creation → open → paste → save routine! 🚀

### 🌸 What This Magical Tool Does:
1. 🎮 **Global Hotkey**: `Ctrl+Shift+V` works anywhere, anytime!
2. 🖼️ **Smart Detection**: Automatically detects text or images
3. 📝 **Custom Filenames**: Optional naming with timestamp format `yyyymmddHHMMSS_yourname`
4. 🎨 **Image Memos**: Add red, centered text annotations to your screenshots!
5. 🌈 **Unicode Support**: Perfect for Japanese, Chinese, Korean, and all languages!
6. 💚 **Cute GUI**: Draggable green widget that stays on top

## 🚀 Quick Start Adventure

### 📦 Installation Quest
```bash
# Clone this magical repository
git clone https://github.com/fxyzbtc/paste2file

# Enter the dungeon
cd paste2file

# Cast the installation spell
uv sync

# Launch the magic!
uv run paste2file
```

### 🎮 Usage Guide

#### 🌟 Method 1: GUI Mode (Recommended!)
```bash
uv run paste2file
# or after installation:
paste2file
```
- A cute green widget appears! 💚
- Press `Ctrl+Shift+V` anywhere to activate
- Right-click the widget to exit

#### 📚 Method 2: Module Mode
```bash
python -m paste2file
```

#### ⚡ Method 3: Script Entry
```bash
paste2file
```

## 🎨 Features Showcase

### 🖼️ Image Magic
- 📸 **Auto PNG**: Saves screenshots as high-quality PNG
- 🎯 **Smart Memo**: Add red, center-aligned text annotations
- 🌍 **Unicode Text**: Support for all languages (中文/日本語/한글)
- 🎪 **Transparency**: Preserves RGBA channels perfectly

### 📝 Text Sorcery  
- 💾 **UTF-8 Safe**: Handles all special characters
- 🔧 **Clean Names**: Spaces become underscores automatically
- ⏰ **Timestamped**: Never lose track of when you saved!

### 🎮 User Experience
- 🎯 **Centered Dialogs**: No more hunting for tiny windows
- 🔝 **Always On Top**: Dialogs stay visible
- 🎪 **Auto Focus**: Start typing immediately
- 🖱️ **Draggable**: Move the widget anywhere you like

## 🛠️ Development Setup

### 🎯 Dependencies
```toml
keyboard>=0.13.5     # 🎮 Global hotkeys
loguru>=0.7.3        # 📊 Beautiful logging  
pyperclip>=1.9.0     # 📋 Clipboard magic
pillow>=10.0.0       # 🖼️ Image processing
pydantic>=2.11.3     # ✅ Data validation
```

### 🧪 Testing Your Magic
```bash
# Run the spell checker
uv run pytest

# Test clipboard with some text
echo "Hello ACGN World! 🌸" | clip

# Test with an image (take a screenshot first)
# Then press Ctrl+Shift+V
```

## 🌈 File Examples

### 📝 Text Files
```
20250802143022_meeting_notes.txt
20250802143125_todo_list.txt  
20250802143200_anime_quotes.txt
```

### 🖼️ Image Files  
```
20250802143300_screenshot_bug_report.png
20250802143445_meme_collection.png
20250802143520_game_victory.png
```

## 🎪 Advanced Usage

### 🎨 Custom Memo Styling
When saving images, you can add:
- 🔴 **Red text** for important notes
- 🎯 **Center alignment** for professional look
- 🌍 **Unicode support** for any language
- 📏 **Auto word wrap** to fit image width

### 🎮 Hotkey Tips
- Works in **any application** 🌟
- **Instant activation** - no need to find the window
- **Clean exit** with right-click menu
- **Persistent** across desktop sessions

## 🔗 Links & Resources

*   🏠 **Homepage:** [https://github.com/fxyzbtc/paste2file]
*   📚 **Wiki:** [https://deepwiki.com/fxyzbtc/paste2file]  
*   🐛 **Issues:** [https://github.com/fxyzbtc/paste2file/issues]

## 🎉 Contributing

Want to make this tool even more magical? 

1. 🍴 Fork the repository
2. 🌟 Create your feature branch
3. ✨ Add some magic (and tests!)
4. 🚀 Submit a pull request

## 📜 License

This project is licensed under the **Power of Friendship** license! 🌈✨

---

*Made with 💖 for the ACGN community by developers who understand the pain of clipboard management!*

**Remember**: Life is too short for manual file operations! Let the magic handle it! 🌟📋✨

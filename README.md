## Installation

安裝[官方版的 Python 3.4+][official-python]。並記住過程中 電腦安裝 Python 的位置（例：`C:\Python34\`）。

執行 `Install.bat`，一開始要輸入 Python 位置。使用上述安裝過程中出現的 Python 位置，並保留路徑中最後一個`\`符號。

運行 server 時候，點擊 `Run Server.bat` 即可執行網站，可以在 <http://localhost:8080/> 看到網站。


[official-python]: https://www.python.org/downloads/
## For Developer

### Start Server

```bash
python -m bottle -b 0.0.0.0:8888 server:app
```

### Debug

```bash
python server.py
```

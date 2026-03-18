
**Activate the environment**
```
source .venv/Scripts/activate
```

**Install all packages**

```
pip-compile requirements.in
pip install -r requirements.txt
```

**Run the tests**

```
python -m pytest backend/tests
```

**Run the application and API**

```
python -m backend.app
```

**Run a peer instance**
Start new terminal sessions with commands:
```
PORT=5000 python -m backend.run
...
PORT=5001 python -m backend.run
PORT=5002 python -m backend.run
PORT=5003 python -m backend.run
```
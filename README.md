
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


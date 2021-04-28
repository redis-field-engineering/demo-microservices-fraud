# Gears

This is where we store all of our gears


## Testing

```
python -m venv gears-venv
source gears-venv/bin/activate
pip install -r requirements.txt
redgrease --watch 1 .
```

Start developing!!

Load the model

```
cat classifier_model.pb | redis-cli -x AI.MODELSET classifier_model TF CPU INPUTS x OUTPUTS Identity BLOB
```

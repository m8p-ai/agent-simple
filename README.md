## Agent Control v1.0 Simple

![M8P System Architecture](previe.png)

This A simple agent that performs inference, vector indexing and search on the M8 Virtual Machine.


## Create ENV
```
/usr/bin/python3.11 -m venv ~/app-env
```

## Ativate
```
source ~/app-env/bin/activate
```


## Install deps
```
pip install -r requirements.txt
```

## Start The server
```
M8_HOST=<your-m8-host-instance> python main.py
```

IF YOU DONT HAVE PYTHON
====

```
sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt-get update && sudo apt install -y python3.11 python3.11-dev python3.11-venv virtualenvwrapper build-essential
```
We need python-dev to interface python code into c/c++ inference engines and proprietary microprocessors design, pipelines, execution and deployment.

## Install PIP
```
python3.11 -m ensurepip
```

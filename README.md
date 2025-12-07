## Agent Simple

A simple agent that performs 

INSTALL PYTHON & BUILD ESSENTIALS
====

```
sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt-get update && sudo apt install -y python3.11 python3.11-dev python3.11-venv virtualenvwrapper build-essential
```
We need python-dev to interface python code into c/c++ inference engines and proprietary microprocessors design, pipelines, execution and deployment.

## Install PIP
```
python3.11 -m ensurepip
```

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
cd api && pip install -r requirements.txt
```

## Install Cmake
```
apt remove cmake -y
pip install cmake --upgrade
```


## Start The server
```
uvicorn main:app --host 0.0.0.0 --port 8998
```

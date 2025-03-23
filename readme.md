# PD Pocket 数控电源上位机

## 开发

首先安装一个Python

进入gui_source目录:

```powershell
cd gui_source
```

安装uv:

```powershell
python -m pip install -U uv
```

新建一个虚拟环境并激活:

```powershell
uv venv --python 3.11
.venv\Scripts\activate
```

安装依赖:

```powershell
uv pip install -r requirements.txt
```

运行:

```powershell
python mdp_gui.py
```

## 打包

```powershell
./build-x64.ps1
```

## 其他信息

参考 [MDP-P906-Controller](https://github.com/ElluIFX/MDP-P906-Controller)

# SnapToTheGround
 一个Maya工具实现类似unreal的地面吸附功能

![demo](doc/demo.gif)

[实现原理](doc/howTo.md)

## 使用方法

从release下载最新版本，找到`sttg_UI.py`，把它拖到Maya界面中即可。

## 插件编译（Windows）
推荐使用python版本，但也提供了纯C++版本。但预编译的只有2024的版本，其他版本需要自己编译。

1. 下载[Maya SDK](https://www.autodesk.com/developnetwork/autodesk-io/io-for-maya)，并解压
2. 安装Cmake
3. 打开命令行，设置环境变量 `DEVKIT_LOCATION` 到解压的Maya SDK目录
4. 进入插件目录，执行 `cmake -G "Visual Studio 16 2019" -A x64`
5. 编译 `cmake --build . --config Release`

```cmd
set DEVKIT_LOCATION=C:\Program Files\Autodesk\Maya2024\devkit
cmake -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
```

插件编译完成后，把`SnapToTheGround.mll`放到对应的版本目录下面就行如:`sttg_main\plugins\2024\SnapToTheGround.mll`

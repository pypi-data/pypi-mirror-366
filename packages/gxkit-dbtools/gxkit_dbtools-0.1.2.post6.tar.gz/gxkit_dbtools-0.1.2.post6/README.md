# gx-toolkit-dbtools

`gx-toolkit-dbtools`，全称**Gx Company Development Toolkit - DBTools Module** ，是**泰富共享**开发的基于Python的数据库客户端工具。

作为`gx-toolkit`依赖的子模块之一，若要使用`gx-toolkit`的通用数据库客户端功能，请安装此包。

## 如何安装

`gx-toolkit-dbtools`目前有两个版本，分为**正式版**和**测试版**。

- **正式版**：发布在**PyPI**的版本，较为稳定
- **测试版**：发布在**TestPyPI**的版本，更新快

**正式版**安装方式：

```
pip install gxkit-dbtools
```

**测试版**安装方式：

```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple gxkit-dbtools
```

测试版在导入时需注意输入正确的**URL**：https://test.pypi.org/simple/

**TestPyPI**上部分库**代码不全或没有最新版**，没有编译好的`.whl`文件（**PyPI**则不会有此问题），因此有部分依赖冲突。需要增加`extra-index-url`帮助用户获取最新版依赖库。

## 功能模块

- `client` 数据库客户端，包含Mysql、ClickHouse以及IoTDB
- `parser` 功能强大的SQL解析器

## 依赖项

- `pymysql` 
- `clickhouse-driver`
- `apache-iotdb` - 支持`1.x`和`2.x`版本，`1.x`版本请手动安装低版本`numpy`和`pandas`
- `cryptography`
- `sqlglot`
- `zstd` - C扩展版，若安装失败请手动指定版本

## 快速入门

作者暂时懒得编写。请直接联系作者（shaojy@sunburst.com.cn）。

## 版本与许可证

当前的最新版本：`0.1.2`

许可证： `Apache License 2.0` 
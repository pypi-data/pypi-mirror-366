
## weberRedis 包功能说明

对 redis 库使用进行了一些实用封装。



# 打包上传PyPi方法

相关命令如下

````
$ python setup.py sdist  # 编译包
$ python setup.py sdist upload # 上传包
$ pip install --upgrade --no-cache-dir weberFuncs
$ pip install --upgrade --no-cache-dir weberRedis
````

# 解决上传403方法

有时采用 python setup.py sdist upload 上传会出现如下错误：
```
error: Upload failed (403): Invalid or non-existent authentication information. See https://pypi.org/help/#invalid-auth for more information.
```

解决办法：在 `C:\Users\<User>` 目录下新建 `.pypirc` 文件，内容如下：

```
[distutils]
index-servers=pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username: <username>
password: <password>
```


20250728
```
PS E:\WeberSrcRoot\Rocky9GogsRoot\PythonWeberEggs\weberRedis> uv build
PS E:\WeberSrcRoot\Rocky9GogsRoot\PythonWeberEggs\weberRedis> uv publish
```
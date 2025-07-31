# coding=utf-8
from ks3.connection import Connection

####################公共头#########################

# 金山云主账号 AccessKey 拥有所有API的访问权限，风险很高。强烈建议您创建并使用子账号账号进行 API 访问或日常运维，请登录 https://uc.console.ksyun.com/pro/iam/#/user/list 创建子账号。
# 通过指定 host(Endpoint)，您可以在指定的地域创建新的存储空间。host(Endpoint) 以北京为例，其它 Region 请按实际情况填写。
conn = Connection('<yourAccessKeyId>', '<yourAccessKeySecret>', host='ks3-cn-beijing.ksyuncs.com')
# 获取存储空间实例
b = conn.get_bucket('<yourBucketName>')

#################### 内容 #########################

#################### 下载 #########################

# 下载 Object，并且作为字符串返回
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.get_key('<yourKeyName>')
# 获取对象内容，并解码
# 对于1000字节大小的文件，正常的下载范围取值为0~999。
# 获取0~999字节范围内的数据，包括0和999，共1000个字节的数据。如果指定的范围无效（比如开始或结束位置的指定值为负数，或指定值大于文件大小），则下载整个文件。
# 如示例，通过『范围下载』下载 2Byte 数据
s = k.get_contents_as_string(byte_range=(0, 1)).decode()
print(s)

# 流式下载 Object
# 适用于文件过大、下载时间过长的情况，可以通过流式下载，分批处理，直到完成
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.get_key('<yourKeyName>')
# 按照字节大小读取，比如300
bytes = k.read(300)
while bytes:
    s = bytes.decode()
    # 对内容进行处理，比如打印
    print(s)
    bytes = k.read(300)

# 下载 Object，并且保存到文件中
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.get_key('<yourKeyName>')
# 填写文件路径，保存到文件
# 对于1000字节大小的文件，正常的下载范围取值为0~999。
# 获取0~999字节范围内的数据，包括0和999，共1000个字节的数据。如果指定的范围无效（比如开始或结束位置的指定值为负数，或指定值大于文件大小），则下载整个文件。
# 如示例，通过『范围下载』下载 2Byte 数据
k.get_contents_to_filename("<savedFilePath>", byte_range=(0, 1))

# 生成下载外链地址
# 对私密属性的文件生成下载外链（该链接具有时效性）
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.get_key('<yourKeyName>')
if k:
    # 下载外链地址 60s 后过期
    # image_attrs 为图像的指令或者样式参数字符串
    url = k.generate_url(60, image_attrs='@base@tag=imgScale&w=500')
    # 下载外链地址在时间点 1492073594 后过期，1492073594 为 Unix Time
    # image_attrs 为图像的指令或者样式参数字符串
    k.generate_url(1492073594, expires_in_absolute=True, image_attrs='@base@tag=imgScale&w=500')

#################### 上传 #########################

# 将指定目录下某一个文件上传，同时可以指定文件 ACL
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.new_key('<yourKeyName>')
# x-kss-storage-class有效值为"STANDARD"、"STANDARD_IA"。"STANDARD"表示标准存储，"STANDARD_IA"表示低频存储，如果不指定，默认为标准存储。
headers = {"x-kss-storage-class": "STANDARD_IA"}
# 填写本地文件的完整路径。
# object policy : 'private' or 'public-read'
ret = k.set_contents_from_filename("<yourSourceFilePath>", policy="private", headers=headers)
# 请求ID。请求ID是本次请求的唯一标识，强烈建议在程序日志中添加此参数。
print(ret.headers['x-kss-request-id'])
# ETag是put_object方法返回值特有的属性，用于标识一个Object的内容。
print(eval(ret.headers['ETag']))
# HTTP返回码。
if ret and ret.status == 200:
    print("上传成功")

# 将字符串作为 value 上传
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.new_key('<yourKeyName>')
# 参数为文件内容
k.set_contents_from_string('<yourFileContent>', headers=None)

# 将字符串作为 value 上传，并设置对象 tag
# key 和 value 需要 url 编码
taggingStr = '<key>=<value>'
headers = {'x-kss-tagging': taggingStr}
ret = k.set_contents_from_string('<yourFileContent>', headers=headers)

# 上传成功后，向回调地址POST数据
# 需要设置`x-kss-callbackurl`和`x-kss-callbackbody`请求头，详见文档[上传回调处理](https://docs.ksyun.com/documents/956)。
# x-kss-callbackurl 为发起回调时请求的服务器地址
# x-kss-callbackbody 为发起回调时请求的body的值
headers = {"x-kss-callbackurl": "<yourCallbackUrl>", "x-kss-callbackbody": "objectKey=${key}&etag=${etag}&uid=123"}
ret = k.set_contents_from_filename("<yourSourceFilePath>", headers=headers)

# 使用签名URL临时授权上传文件
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.new_key("<yourKeyName>")
if k:
    # 生成上传文件的签名URL，有效时间为60秒。
    url = k.get_presigned_url(60)
    print(url)

#################### 管理文件 #########################

# 获取文件元信息（大小、最后更新时间等）
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.get_key('<yourKeyName>')
if k:
    print(k.name, k.size, k.last_modified)

# 获取并打印出object的ACL信息（暂时无法说明）
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
# policy = b.get_acl("<yourKeyName>")
# print(policy.to_xml())

# 设置object的ACL
# object的ACL可选择 'private' or 'public-read'，下面示例设置为'public-read'
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
b.set_acl("public-read", "<yourKeyName>")

# 添加存储类型header，此处更改文件存储类型为归档类型
# x-kss-storage-class有效值为"STANDARD"、"STANDARD_IA"。"STANDARD"表示标准存储，"STANDARD_IA"表示低频存储，如果不指定，默认为标准存储。
headers = {'x-kss-storage-class': 'STANDARD_IA'}
# 更改文件存储类型。通过复制并添加新header的方式实现，故方法名为copy_key
# <yourDstKeyName> 为新对象名称，<yourSrcBucketName>是原存储空间名称，<yourSrcKeyName>是原对象名称
b.copy_key('<yourDstKeyName>', '<yourSrcBucketName>', '<yourSrcKeyName>', headers=headers)

# 添加元数据相关header，此处更改content-type和元数据指令
# 详情参考[PUT Object Copy](https://docs.ksyun.com/documents/941)
headers = {'content-type': 'text/plain', 'x-kss-metadata-directive': 'REPLACE'}
# 更改文件元数据信息。通过复制并添加新header的方式实现，故方法名为copy_key
# <yourDstKeyName> 为新对象名称，<yourSrcBucketName>是原存储空间名称，<yourSrcKeyName>是原对象名称
b.copy_key('<yourDstKeyName>', '<yourSrcBucketName>', '<yourSrcKeyName>', headers=headers)

# 列举文件
#### 列举 Bucket 内的文件或者目录

from ks3.connection import Connection
from ks3.prefix import Prefix
from ks3.key import Key

# 金山云主账号 AccessKey 拥有所有API的访问权限，风险很高。强烈建议您创建并使用子账号账号进行 API 访问或日常运维，请登录 https://uc.console.ksyun.com/pro/iam/#/user/list 创建子账号。
# 通过指定 host(Endpoint)，您可以在指定的地域创建新的存储空间。host(Endpoint) 以北京为例，其它 Region 请按实际情况填写。
conn = Connection('<yourAccessKeyId>', '<yourAccessKeySecret>', host='ks3-cn-beijing.ksyuncs.com')
# 获取存储空间实例
b = conn.get_bucket('<yourBucketName>')

keys = b.list()
for k in keys:
    if isinstance(k, Key):
        print('文件:%s' % k.name)
    elif isinstance(k, Prefix):
        print('目录:%s' % k.name)

# 列举 Bucket 内指定前缀的文件
# 列举 images 文件夹下的所有文件。比如b.list(prefix="images/")
keys = b.list(prefix="<yourPrefix>")

# 列举 Bucket 内以指定分隔符分组的文件
# delimiter 为对文件名称进行分组的字符；delimiter 为空时，默认为'/'
# 返回结果中 delimiter 分隔符之前的字符会放入 commonPrefixes 中，可以类比理解为文件夹
# 只列举该文件夹下的文件和子文件夹（目录）名称，子文件夹下的文件和文件夹不显示。
keys = b.list(delimiter='/')

# 列举指定字符串（object名称）之后（字典排序）的所有文件。同名 object 也会被排除。
keys = b.list(marker='<yourMarker>')

# 列举指定个数的文件。如下列举10个文件
keys = b.list(max_keys=10)

# 列举 Bucket 内指定前缀的文件以及指定时间区间的文件
# start_time = 1625460400 这个时间之前的数据
# end_time   = 1625460400 这个时间之后的数据
# start_time=1640331446, end_time=1641895096 这个时间中间的数据
keys = b.listObjects(prefix="local/load", start_time=1640331446, end_time=1641895096)


# 列举目录下的文件大小
# 计算指定目录下的文件大小
def calcFolderSize(bucket, folder):
    length = 0
    keys = bucket.list(prefix=folder)
    for k in keys:
        if isinstance(k, Key):
            length += k.size
    return length


from ks3.prefix import Prefix


def getFolderSizeInBucket():
    keys = b.list(delimiter='/')
    for k in keys:
        # 判断是否为目录
        if isinstance(k, Prefix):
            print('dir: ' + k.name + '  size:' + str(calcFolderSize(b, k.name)) + "Byte")


# 删除文件。<yourObjectName>表示删除文件时需要指定包含文件后缀在内的完整路径。如 images/test.jpg
# 暂不支持删除文件夹
b.delete_key('<yourKeyName>')

# 拷贝文件
# 空间名称必须有效，同时用户需要拥有对拷贝对象的读权限。
# <yourDstKeyName> 为新对象名称，<yourSrcBucketName>是原存储空间名称，<yourSrcKeyName>是原对象名称
b.copy_key('<yourDstKeyName>', '<yourSrcBucketName>', '<yourSrcKeyName>')

# 解冻文件
# 对归档Object进行解冻
k = b.get_key('<yourKeyName>')
k.restore_object()

# 抓取网络资源上传
# 从第三方URL拉取文件，并上传至KS3某个 bucket 中存储成名为 object 的文件。
k = b.new_key('www-logo')
k.fetch_object(source_url='http://fe.ksyun.com/project/resource/img/www-logo.png')
# 参见：[金山云官方文档-Put Object Fetch](https://docs.ksyun.com/documents/949)


# 对象标签
# 获取对象标签
k = b.get_key('<yourKeyName>')
tagging = k.get_object_tagging()
print(tagging.to_xml())

# 设置对象标签
from ks3.tagging import Tag

k = b.get_key('<yourKeyName>')
tagging = [Tag('<key>', '<value>')]
k.set_object_tagging(tagging)

# 删除对象标签
k = b.get_key('<yourKeyName>')
k.delete_object_tagging()

# 字符串追加上传，仅作特性功能展示，其他参考常规上传
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.new_key('<yourKeyName>')
# 第一个参数为文件内容；position为插入位置
ret = k.append_object_from_string('<yourFileContent1>', position='<appendPosition>')
if ret and ret.status == 200:
    print("追加上传成功")
# 如有需要，获取下一次append的位置
print("x-kss-next-append-position:", ret.headers['x-kss-next-append-position'])
# 继续追加
ret = k.append_object_from_string('<yourFileContent2>', position=int(ret.headers['x-kss-next-append-position']))
if ret and ret.status == 200:
    print("继续追加上传成功")

# 文件追加上传，用法参考"字符串追加上传"
# 填写Object完整路径。Object完整路径中不能包含Bucket名称。
k = b.new_key('<yourKeyName>')
# 第一个参数为文件路径；position为插入位置
ret = k.append_object_from_filename("<yourSourceFilePath>", position='<appendPosition>')
if ret and ret.status == 200:
    print("文件追加上传成功")

# 异步上传文件，以asyncio为例
import asyncio

k = b.new_key('<yourKeyName>')
ret = asyncio.run(k.upload_file_async("<yourSourceFilePath>"))
if ret and ret.status == 200:
    print("上传成功")

# 异步下载文件，以asyncio为例
import asyncio

k = b.get_key('<yourKeyName>')
asyncio.run(k.download_file_async("<yourSourceFilePath>"))

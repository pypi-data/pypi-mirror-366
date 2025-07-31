# coding=utf-8
import math, os
from ks3.connection import Connection
from filechunkio import FileChunkIO
####################公共头#########################
# 金山云主账号 AccessKey 拥有所有API的访问权限，风险很高。强烈建议您创建并使用子账号账号进行 API 访问或日常运维，请登录 https://uc.console.ksyun.com/pro/iam/#/user/list 创建子账号。
# 通过指定 host(Endpoint)，您可以在指定的地域创建新的存储空间。host(Endpoint) 以北京为例，其它 Region 请按实际情况填写。
conn = Connection('<yourAccessKeyId>', '<yourAccessKeySecret>', host='ks3-cn-beijing.ksyuncs.com')
# 获取存储空间实例
b = conn.get_bucket('<yourBucketName>')
# 源文件路径
source_path = '<yourSourceFilePath>'
# 源文件大小
source_size = os.stat(source_path).st_size

# 初始化分片。获取初始化的 uploadId，之后的操作中将会用到
# 如需在初始化分片时设置文件存储类型，请在 initiate_multipart_upload 中设置相关 headers
# x-kss-storage-class有效值为"STANDARD"、"STANDARD_IA"。"STANDARD"表示标准存储，"STANDARD_IA"表示低频存储，如果不指定，默认为标准存储。
headers = {"x-kss-storage-class": "STANDARD"}
mp = b.initiate_multipart_upload('<yourKeyName>', headers=headers)
# 举例以 50 MiB 为分片大小
chunk_size = 52428800
chunk_count = int(math.ceil(source_size*1.0 / chunk_size*1.0))

# 通过 FileChunkIO 将文件分片
for i in range(chunk_count):
	offset = chunk_size * i
	bytes = min(chunk_size, source_size - offset)
	with FileChunkIO(source_path, 'r', offset=offset, bytes=bytes) as fp:
		# 逐个上传分片
		mp.upload_part_from_file(fp, part_num=i + 1)
# 发送请求，合并分片，完成分片上传
ret = mp.complete_upload()
if ret and ret.status == 200:
	print("上传成功")

# 取消指定upload_id的分片上传事件，已上传的分片会被删除。
# 列出 Bucket 内所有正在进行的分片上传任务
for p in b.get_all_multipart_uploads():
	print(p.id)
	# 取消上传
	print(p.cancel_upload())

# 列出指定上传任务中所有已上传的分片信息
# part_number_marker 指定应该从哪个分片开始列举，只有比设定值大的分片才会被列举
for part in mp.get_all_parts(part_number_marker=2):
	print('part_number:%s' % part.part_number)
	print('request_id:%s' % part.request_id)

# 列举分片上传事件
# 列举 Bucket 中所有的分片上传事件
key_marker='<yourKey>'
for p in b.list_multipart_uploads(key_marker=key_marker):
	print('uploadId:%s,key:%s' % (p.id, p.key_name))
	for i in p:
		print(i.part_number, i.size, i.etag, i.last_modified)

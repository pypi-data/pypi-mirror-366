# -*- coding: utf-8 -*-
# python3
from ks3.connection import Connection
import os

ak = os.getenv('KS3_TEST_ACCESS_KEY_ID', '<YOUR_ACCESS_KEY>')
sk = os.getenv('KS3_TEST_ACCESS_KEY_SECRET', '<YOUR_SECRET_KEY>')
bucket_name = os.getenv('KS3_TEST_BUCKET', '<KS3_TEST_BUCKET>')
endpoint = os.getenv('KS3_TEST_ENDPOINT', 'ks3-cn-shanghai-internal.ksyuncs.com')

conn = Connection(ak, sk, host=endpoint, is_secure=False, ua_addon='test-ua/1') #port=8091,
key_name = 'test_key'

customer_key = bytes(32)
import base64, hashlib
customer_key_base64 = base64.b64encode(customer_key).decode('utf-8')
md5 = hashlib.md5()
md5.update(customer_key)
customer_key_md5 = base64.b64encode(md5.digest()).decode('utf-8')

customer_encryption_headers={
  'x-kss-server-side-encryption-customer-algorithm': 'AES256',
  'x-kss-server-side-encryption-customer-key': customer_key_base64,
  'x-kss-server-side-encryption-customer-key-MD5': customer_key_md5
}

customer_key2 = bytearray(b'00000000000000000000000000000000')
customer_key2[0] = 1
print(customer_key2)
import base64, hashlib
customer_key2_base64 = base64.b64encode(customer_key2).decode('utf-8')
md5 = hashlib.md5()
md5.update(customer_key2)
customer_key2_md5 = base64.b64encode(md5.digest()).decode('utf-8')

#####################  ks3.object  ###########################
def getObjectMeta(bucket_name, object_key_name, headers=None):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.get_key_meta(object_key_name, headers=headers)
  if resp:
    print("获取文件header成功: ", resp.headers)

def uploadObjectFromFile(path, file_name=None, encrypt_key=False, headers=None):
  bucket = conn.get_bucket(bucket_name)
  filename = file_name if file_name else path.split('/')[-1]
  k = bucket.new_key(filename)
  ret = k.set_contents_from_filename(path, encrypt_key=encrypt_key, headers=headers)
  if ret and ret.status == 200:
    print("上传成功: %s" % path)

def upload_object_with_customer_encryption_key(key_name, content):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key(key_name)
  ret = k.set_contents_from_string(content, headers=customer_encryption_headers)
  if ret and ret.status == 200:
    print("上传成功: %s" % key_name)

  getObjectMeta(bucket_name, key_name, headers=customer_encryption_headers)
  downloadObjectAndPrint(bucket_name, key_name, headers=customer_encryption_headers)
  bucket.delete_key(key_name)
  print("清理文件成功: %s" % key_name)

def downloadObjectAndPrint(bucket_name, key_name, headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(key_name, headers=headers)
  s = k.get_contents_as_string(headers=headers).decode()
  print(s)

def downloadObjectAndSave(key_name, file_save_path, headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(key_name, headers=headers)
  k.get_contents_to_filename(file_save_path, headers=headers)

def copy_encryption(dstKey, srcKey, encrypt_key=None):
  b = conn.get_bucket(bucket_name)
  b.copy_key(dstKey, bucket_name, srcKey, encrypt_key=encrypt_key)

def copy_customer_encryption(dstKey, srcKey, encrypt_key=None, headers=None):
  b = conn.get_bucket(bucket_name)
  src_bucket_name = bucket_name
  b.copy_key(dstKey, src_bucket_name, srcKey, encrypt_key=encrypt_key, headers=headers)

def test_copy_customer_encryption():
  srcKey = 'test-customer-encryption'
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key(srcKey)
  ret = k.set_contents_from_string('hello customer encryption', headers=customer_encryption_headers)
  if ret and ret.status == 200:
    print("上传成功: %s" % srcKey)

  dstKey = 'test-customer-encryption.cp'
  copy_customer_encryption(dstKey, srcKey, headers={
    **customer_encryption_headers,
    'x-kss-copy-source-server-side-encryption-customer-algorithm': 'AES256',
    'x-kss-copy-source-server-side-encryption-customer-key': customer_key_base64,
    'x-kss-copy-source-server-side-encryption-customer-key-MD5': customer_key_md5
  })
  print("复制成功: %s" % dstKey)
  getObjectMeta(bucket_name, dstKey, headers=customer_encryption_headers)
  downloadObjectAndPrint(bucket_name, dstKey, headers=customer_encryption_headers)

  bucket.delete_key(srcKey)
  print("清理文件成功: %s" % srcKey)
  bucket.delete_key(dstKey)
  print("清理文件成功: %s" % dstKey)

# 服务端加密最终的文件
def test_multipart_upload_sse():
  import math, os
  from filechunkio import FileChunkIO
  bucket = conn.get_bucket(bucket_name)

  source_path = '/Users/jabbar/Downloads/article_cp.txt'
  # 源文件大小
  source_size = os.stat(source_path).st_size

  mp = bucket.initiate_multipart_upload("article_cp.txt.mpu.1", headers={
    # 'x-kss-server-side-encryption-customer-algorithm': 'AES256',
    # 'x-kss-server-side-encryption-customer-key': customer_key_base64,
    # 'x-kss-server-side-encryption-customer-key-MD5': customer_key_md5
  })
  print(mp)

  # chunk_size = 5242880
  chunk_size = 5242880
  chunk_count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))

  # # 通过 FileChunkIO 将文件分片
  # for i in range(chunk_count):
  #   offset = chunk_size * i
  #   bytes = min(chunk_size, source_size - offset)
  #   with FileChunkIO(source_path, 'r', offset=offset, bytes=bytes) as fp:
  #     # 逐个上传分片
  #     mp.upload_part_from_file(fp, part_num=i + 1, headers={
  #       # 'x-kss-server-side-encryption-customer-algorithm': 'AES256',
  #       # 'x-kss-server-side-encryption-customer-key': customer_key_base64,
  #       # 'x-kss-server-side-encryption-customer-key-MD5': customer_key_md5
  #     })
  with open(source_path, 'rb') as fp:
    mp.upload_part_from_file(fp, part_num=1)
  # 发送请求，合并分片，完成分片上传
  ret = mp.complete_upload()
  if ret and ret.status == 200:
    print("上传成功")

# 以存在的 服务端加密的 object作为part，进行分块的合并
def test_multipart_upload_copy_with_sse_s3_object():
  bucket = conn.get_bucket(bucket_name)

  # uploadObjectFromFile('/Users/jabbar/tools/test-data/xaa', encrypt_key=True)
  # uploadObjectFromFile('/Users/jabbar/tools/test-data/xab', encrypt_key=True)
  # uploadObjectFromFile('/Users/jabbar/tools/test-data/xac', encrypt_key=True)

  final_file = "article_cp.txt"
  # 测试加密最终对象
  mp = bucket.initiate_multipart_upload(final_file, encrypt_key=True, headers={
    # 'x-kss-server-side-encryption-customer-algorithm': 'AES256',
    # 'x-kss-server-side-encryption-customer-key': customer_key_base64,
    # 'x-kss-server-side-encryption-customer-key-MD5': customer_key_md5
  })
  print(mp.id)

  # mp.copy_part_from_key(bucket_name, 'DSC03380.ssec.jpg', 1, headers={
  #   # 'x-kss-server-side-encryption-customer-algorithm': 'AES256',
  #   # 'x-kss-server-side-encryption-customer-key': customer_key_base64,
  #   # 'x-kss-server-side-encryption-customer-key-MD5': customer_key_md5,
  #   'x-kss-copy-source-server-side-encryption-customer-algorithm': 'AES256',
  #   'x-kss-copy-source-server-side-encryption-customer-key': customer_key_base64,
  #   'x-kss-copy-source-server-side-encryption-customer-key-MD5': customer_key_md5
  # })
  # parts = mp.get_all_parts()
  # print(parts[0].size)
  # mp.copy_part_from_key(bucket_name, 'xaa', 1)
  # mp.copy_part_from_key(bucket_name, 'xab', 2)
  # mp.copy_part_from_key(bucket_name, 'xac', 3)

  # 发送请求，合并分片，完成分片上传
  ret = mp.complete_upload()
  if ret and ret.status == 200:
    print("上传成功: %s"% final_file)

  # getObjectMeta(bucket_name, final_file)
  # file_save_path = '/Users/jabbar/tools/test-data/' + final_file
  # downloadObjectAndSave(final_file, file_save_path)
  # print("下载文件成功")


  # bucket.delete_key(final_file)
  # print("清理文件成功: %s" % final_file)

# 以存在的object作为part，进行分块的合并
# 用户指定秘钥的服务端加密
def test_multipart_upload_copy_with_ss3_c_object():
  bucket = conn.get_bucket(bucket_name)

  customer_key = bytes(32)
  import base64, hashlib
  customer_key_base64 = base64.b64encode(customer_key).decode('utf-8')
  md5 = hashlib.md5()
  md5.update(customer_key)
  customer_key_md5 = base64.b64encode(md5.digest()).decode('utf-8')
  uploadObjectFromFile('/Users/jabbar/tools/test-data/xaa', headers=customer_encryption_headers)
  uploadObjectFromFile('/Users/jabbar/tools/test-data/xab', headers=customer_encryption_headers)
  uploadObjectFromFile('/Users/jabbar/tools/test-data/xac', headers=customer_encryption_headers)

  final_file = "DSC03380.encrypt.customer.jpg"
  # 测试加密最终对象
  mp = bucket.initiate_multipart_upload(final_file, headers=customer_encryption_headers)
  print(mp)

  mp.copy_part_from_key(bucket_name, 'xaa', 1, headers={
    **customer_encryption_headers,
    'x-kss-copy-source-server-side-encryption-customer-algorithm': 'AES256',
    'x-kss-copy-source-server-side-encryption-customer-key': customer_key_base64,
    'x-kss-copy-source-server-side-encryption-customer-key-MD5': customer_key_md5
  })
  mp.copy_part_from_key(bucket_name, 'xab', 2, headers={
    **customer_encryption_headers,
    'x-kss-copy-source-server-side-encryption-customer-algorithm': 'AES256',
    'x-kss-copy-source-server-side-encryption-customer-key': customer_key_base64,
    'x-kss-copy-source-server-side-encryption-customer-key-MD5': customer_key_md5
  })
  mp.copy_part_from_key(bucket_name, 'xac', 3, headers={
    **customer_encryption_headers,
    'x-kss-copy-source-server-side-encryption-customer-algorithm': 'AES256',
    'x-kss-copy-source-server-side-encryption-customer-key': customer_key_base64,
    'x-kss-copy-source-server-side-encryption-customer-key-MD5': customer_key_md5
  })

  # 发送请求，合并分片，完成分片上传
  ret = mp.complete_upload()
  if ret and ret.status == 200:
    print("上传成功: %s"% final_file)

  getObjectMeta(bucket_name, final_file, headers=customer_encryption_headers)
  file_save_path = '/Users/jabbar/tools/test-data/' + final_file
  downloadObjectAndSave(final_file, file_save_path, headers=customer_encryption_headers)
  print("下载文件成功")
  bucket.delete_key(final_file)
  print("清理文件成功: %s" % final_file)




# test_multipart_upload_copy_with_encrypt_object()
# getObjectMeta(bucket_name, 'DSC03380.encrypt.jpg')
# copy_encryption('ks3util_bak', 'ks3util', encrypt_key=True)
# uploadObjectFromFile('/Users/jabbar/Downloads/DSC03380.encrypt.jpg', file_name='DSC03380.ssec.jpg', headers=customer_encryption_headers)
# getObjectMeta('test-bucket', 'DSC03380.ssec.jpg', headers=customer_encryption_headers)
# uploadObjectFromFile('/Users/jabbar/Downloads/article_cp.txt', file_name='article_cp.txt_ss3_s3', encrypt_key=True)
# getObjectMeta(bucket_name, 'article_cp.txt_ss3_s3', headers={
#   'x-kss-server-side-encryption': 'AES256'
# })
# test_copy_customer_encryption()
# upload_object_with_customer_encryption_key('test-customer-encryption', 'helloworld')
# test_multipart_upload_copy_with_customer_encrypt_object()
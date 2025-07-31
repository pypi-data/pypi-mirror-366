# coding=utf-8
import math
import os
import time

import ks3.multipart
from ks3 import utils
from ks3.connection import Connection

ak = os.getenv('KS3_TEST_ACCESS_KEY_ID', '<YOUR_ACCESS_KEY>')
sk = os.getenv('KS3_TEST_ACCESS_KEY_SECRET', '<YOUR_SECRET_KEY>')
bucket_name = os.getenv('KS3_TEST_BUCKET', '<KS3_TEST_BUCKET>')
endpoint = os.getenv('KS3_TEST_ENDPOINT', 'ks3-cn-shanghai-internal.ksyuncs.com')

key_name = '<your_key_name>'
file_path = '<your_file_path>'

# 默认开启自动校验crc
# 关闭需要 conn.enable_crc = False 或 Connection(ak, sk, host=endpoint, enable_crc=False)
conn = Connection(ak, sk, host=endpoint)
bucket = conn.get_bucket(bucket_name)


def test_uploadObjectFromFile_checkingCrc64():
    # 自动crc校验
    k = bucket.new_key(key_name)
    ret = k.set_contents_from_filename(file_path)
    assert ret.status == 200


def test_uploadObjectFromString_checkingCrc64():
    # 自动crc校验
    k = bucket.new_key(key_name)
    myContent = 'some string'
    ret = k.set_contents_from_string(myContent)
    assert ret.status == 200


def test_downloadObject_checkingCrc64():
    k = bucket.get_key(key_name)

    data = k.read(300)
    while data:
        s = data.decode()
        print('bytes decoded:', s)
        time.sleep(5)
        data = k.read(300)

    assert k.server_crc == k.client_crc


def test_downloadObjectToString_checkingCrc64():
    k = bucket.get_key(key_name)
    s = k.get_contents_as_string().decode()
    client_crc = utils.compute_data_crc64(s)
    assert client_crc == k.server_crc


def test_headObject_checkingCrc64():
    k = bucket.new_key(key_name)
    ret = k.set_contents_from_filename(file_path)
    assert ret.status == 200

    k = bucket.get_key(key_name)
    client_crc = utils.compute_file_crc64(file_path)
    assert client_crc == k.server_crc


def test_copyObject_checkingCrc64():
    k = bucket.new_key(key_name)
    ret = k.set_contents_from_filename(file_path)
    assert ret.status == 200

    ret = bucket.copy_key("copy_test", bucket_name, key_name)
    client_crc = utils.compute_file_crc64(file_path)
    assert client_crc == ret.server_crc


def test_multi_upload_checkingCrc64():
    # 自动校验crc
    from filechunkio import FileChunkIO

    source_size = os.stat(file_path).st_size

    mp = bucket.initiate_multipart_upload("test_multi")

    chunk_size = 100 * 1024
    count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))

    # 默认自动校验每个分片的crc，和合并后的crc
    for i in range(count):
        offset = chunk_size * i
        read_size = min(chunk_size, source_size - offset)
        with FileChunkIO(file_path, 'r', offset=offset, bytes=read_size) as fp:
            # 逐个上传分片
            mp.upload_part_from_file(fp, part_num=i + 1)
    ret = mp.complete_upload()
    assert ret and ret.status == 200


def test_multi_copy_checkingCrc64():
    k = bucket.new_key("test_multi")
    ret = k.set_contents_from_filename(file_path)
    assert ret.status == 200

    copy_key = 'test_multi-copy'
    source_size = os.stat(file_path).st_size

    mp = bucket.initiate_multipart_upload(copy_key)

    chunk_size = 100 * 1024
    count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))

    help_list = []

    for i in range(count):
        start = chunk_size * i
        end = min(start + chunk_size - 1, source_size - 1)
        ret = mp.copy_part_from_key(bucket_name, "test_multi", i + 1, start, end)
        client_crc = utils.compute_file_crc64(file_path, start, end)
        help_list.append(ks3.multipart.PartInfo(end - start + 1, client_crc))
        assert client_crc == ret.server_crc
    ret = mp.complete_upload()
    parts_crc = 0
    crc_obj = utils.Crc64(0)
    for p in help_list:
        parts_crc = crc_obj.combine(parts_crc, int(p.part_crc), p.size)
    assert str(parts_crc) == ret.ChecksumCRC64ECMA


########## 手动计算crc，通过请求头校验的方式 ##########
# ks3服务端也提供了crc64校验的请求头，如果不开启自动校验crc的功能，可以通过传入请求头的方式让服务端进行crc的比对

def test_uploadObjectFromFile_checkingCrc64ByHeader():
    k = bucket.new_key(key_name)
    conn.enable_crc = False
    local_crc = utils.compute_file_crc64(file_path)
    crc_header = conn.provider.checksum_crc64ecma_header
    k.set_contents_from_filename(file_path, headers={crc_header: local_crc})


def test_uploadObjectFromString_checkingCrc64ByHeader():
    k = bucket.new_key(key_name)
    myContent = 'some string'
    conn.enable_crc = False
    local_crc = utils.compute_data_crc64(myContent)
    crc_header = conn.provider.checksum_crc64ecma_header
    k.set_contents_from_string(myContent, headers={crc_header: local_crc})


def test_multi_upload_checkingCrc64ByHeader():
    from filechunkio import FileChunkIO
    # 服务端不比对文件整体crc，可以在本地比对
    conn.enable_crc = False
    crc_header = conn.provider.checksum_crc64ecma_header
    crc_obj = utils.Crc64(0)
    final_crc = 0

    source_size = os.stat(file_path).st_size

    mp = bucket.initiate_multipart_upload("test_multi")

    chunk_size = 100 * 1024
    count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))

    for i in range(count):
        offset = chunk_size * i
        read_size = min(chunk_size, source_size - offset)
        with FileChunkIO(file_path, 'r', offset=offset, bytes=read_size) as fp:
            # 计算单个分片的crc
            local_part_crc = utils.compute_file_crc64(file_path, offset, offset + read_size - 1)
            # 将每一个分片的crc合并，最终将得到文件整体的crc值
            final_crc = crc_obj.combine(final_crc, int(local_part_crc), read_size)
            # 逐个上传分片
            mp.upload_part_from_file(fp, part_num=i + 1, headers={crc_header: local_part_crc})
    ret = mp.complete_upload()

    assert ret.ChecksumCRC64ECMA == str(final_crc)
    assert ret and ret.status == 200

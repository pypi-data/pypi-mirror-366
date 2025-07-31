# coding=utf-8
# 多线程分块上传和下载样例

from ks3.connection import Connection
# 需要安装filechunkio
from filechunkio import FileChunkIO
import threading
from queue import Queue
import datetime
import os, math

ak = 'YOUR_ACCESS_KEY'
sk = 'YOUR_SECRET_KEY'
conn = Connection(ak, sk, host="ks3-cn-beijing.ksyuncs.com")
test_bucket = 'sdktestt'
test_key = 'test_key'


def single_multipart_upload(bucket, file_path, test_key):
    print('single_multipart_upload')
    source_path = file_path
    source_size = os.stat(source_path).st_size

    print('multi-upload start:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])
    mp = bucket.initiate_multipart_upload(test_key, policy="public-read-write")
    # print(mp.id)

    chunk_size = 5242880
    chunk_count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))

    try:
        for i in range(chunk_count):
            offset = chunk_size * i
            bytes = min(chunk_size, source_size - offset)
            with FileChunkIO(source_path, 'r', offset=offset, bytes=bytes) as fp:
                mp.upload_part_from_file(fp, part_num=i + 1)
        ret = mp.complete_upload()
        if ret and ret.status == 200:
            print('multi-upload succeed:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])
        else:
            print('multi-upload failed:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])
    except:
        print('multi-upload failed:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])


class Chunk:
    num = 0
    offset = 0
    len = 0

    def __init__(self, n, o, l):
        self.num = n
        self.offset = o
        self.len = l


def init_queue(file_size, chunk_size):
    chunkcnt = int(math.ceil(file_size*1.0/chunk_size))
    #print('chunk count:', chunkcnt)
    q = Queue(maxsize = chunkcnt)
    for i in range(0,chunkcnt):
        offset = chunk_size*i
        len = min(chunk_size, file_size-offset)
        c = Chunk(i+1, offset, len)
        q.put(c)
    return q


def upload_chunk(file_path, mp, q):
    while (not q.empty()):
        chunk = q.get()
        fp = FileChunkIO(file_path, 'r', offset=chunk.offset, bytes=chunk.len)
        # print('file%s chunk_%s start %s \n' % (file_path, chunk.num, datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3]))
        mp.upload_part_from_file(fp, part_num=chunk.num)
        # print('file%s chunk_%s end %s \n' % (file_path, chunk.num, datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3]))
        fp.close()
        q.task_done()

# thread_cnt 为线程数
def threading_multipart_upload(bucket, file_path, key_name, thread_cnt=10):
    print('multi-upload ', key_name, ' start:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])
    file_size = os.stat(file_path).st_size
    mp = bucket.initiate_multipart_upload(key_name)
    chunk_size = 5242880
    q = init_queue(file_size, chunk_size)
    if thread_cnt is None:
        thread_cnt = q.qsize() - 1
    for i in range(0, thread_cnt):
        t = threading.Thread(target=upload_chunk, args=(file_path, mp, q))
        t.setDaemon(True)
        t.start()
    q.join()
    try:
        ret = mp.complete_upload()
        if ret and ret.status == 200:
            print('multi-upload succeed:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])
        else:
            print('multi-upload failed:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])
    except:
        print('multi-upload failed:', datetime.datetime.now().strftime("%H:%M:%S.%f'")[:-3])


if __name__=="__main__":
    bucket = conn.get_bucket(test_bucket)
    # 单线程执行
    # print('单线程执行')
    # single_multipart_upload(bucket, file_path, test_key)
    # 多线程执行
    print('多线程执行')
    threading_multipart_upload(bucket, file_path, test_key, thread_cnt=10)

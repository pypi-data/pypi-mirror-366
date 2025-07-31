# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime

import requests

from ks3.connection import Connection, PathCallingFormat, VirtualHostCallingFormat
from ks3.exception import S3ResponseError, S3CreateError
from ks3.key import Key
from ks3.tagging import Tag
from ks3.bucket import BucketLocation
from ks3.xmlParsers.bucketCors import BucketCors, CORSRule
from ks3.xmlParsers.bucketCrossReplicate import BucketCrossReplicate
from ks3.xmlParsers.bucketInventory import BucketInventory, Destination, Schedule, Filter as InventoryFilter
from ks3.xmlParsers.bucketLifecycle import BucketLifecycle, Rule as LifecycleRule, Filter as LifecycleFilter, \
  Expiration as LifecycleExpiration, Transition as LifecycleTransition, AbortIncompleteMultipartUpload
from ks3.xmlParsers.bucketLogging import BucketLogging
# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
from ks3.xmlParsers.bucketMirror import BucketMirror, AsyncMirrorRule, SyncMirrorRules, MirrorRequestSetting, \
  HeaderSetting
from ks3.xmlParsers.bucketRetention import BucketRetention, Rule as RetentionRule
from base64 import urlsafe_b64encode
import asyncio
import ks3
import logging
ks3.set_stream_logger(level=logging.DEBUG)

ak = os.getenv('KS3_IAM_ACCESS_KEY_ID', '<YOUR_ACCESS_KEY>')
sk = os.getenv('KS3_IAM_ACCESS_KEY_SECRET', '<YOUR_SECRET_KEY>')
bucket_name = os.getenv('KS3_BUCKET', '<KS3_TEST_BUCKET>')
endpoint = 'ks3-cn-shanghai.ksyuncs.com' #os.getenv('KS3_TEST_ENDPOINT', 'ks3-cn-shanghai-internal.ksyuncs.com')

conn = Connection(ak, sk, host=endpoint, port=80, ua_addon='test-ua/1', is_secure=True, calling_format=VirtualHostCallingFormat()) #port=8091,
key_name = 'test_key'


def getAllBuckets(project_ids=None):
  try:
    buckets = conn.get_all_buckets(project_ids=project_ids) #
    for b in buckets:
      print(b.name, b.region, b.Region, b.creation_date)
  except Exception as e:
    print('request_id: %s' % e.request_id)
    print(e)
    raise

def headBucket(bucket_name):
  # 如果正常返回，则Bucket存在；如果抛出S3ResponseError
  try:
    headResult = conn.head_bucket(bucket_name)
  except S3ResponseError as e:
    print('status: %s, reason: %s, request_id: %s, body: %s' % (e.status, e.reason, e.request_id, e.body))

def head_bucket_shadowcopy(bucket_name):
  # 如果正常返回，则Bucket存在；如果抛出S3ResponseError
  try:
    headResult = conn.head_bucket(bucket_name)
    if headResult.headers['x-kss-shadowcopy']:
      print('已开启shadowcopy', headResult.headers['x-kss-shadowcopy'])
    else:
      print('未开启shadowcopy')
  except S3ResponseError as e:
    print('status: %s, reason: %s, request_id: %s, body: %s' % (e.status, e.reason, e.request_id, e.body))

def getBucketLocation(bucket_name):
  loc = conn.get_bucket_location(bucket_name)
  print(isinstance(loc, BucketLocation))
  print(loc.location)

def createBucket(bucket_name, location=''):
  try:
    resp = conn.create_bucket(bucket_name, location=location, headers={
      'x-kss-bucket-type': 'ARCHIVE'
    })
    print('createBucket, request_id: ', resp.response_metadata.request_id)
  except Exception as e:
    print('request_id: %s' % e.request_id)
    if isinstance(e, S3CreateError):
      print("create bucket error, bucket already exists, error: ", e)
    else:
      print("create bucket error, error: ", e)

def deleteBucket(bucket_name):
  try:
    resp = conn.delete_bucket(bucket_name)
    print('deleteBucket, request_id: ', resp.response_metadata.request_id)
  except S3ResponseError as error:
    print('error: %s' % error)
    print('error requestid: %s' % error.request_id)


def getBucketAcl(bucket_name):
  b = conn.get_bucket(bucket_name)
  policy = b.get_acl()
  print("got acl_policy, request_id: ", policy.response_metadata.request_id)
  for grant in policy.acl.grants:
    print(grant.permission, grant.display_name, grant.email_address, grant.id)

def setBucketAcl(bucket_name):
  b = conn.get_bucket(bucket_name)
  resp = b.set_acl("private")
  print("set_acl, request_id: ", resp.response_metadata.request_id)

def manageBucketPolicy(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  setResp = bucket.set_bucket_policy(
    policy='{"Statement":[{"Resource":["krn:ksc:ks3:::test-bucket","krn:ksc:ks3:::test-bucket/*"],"Principal":{"KSC":["krn:ksc:iam::32432423:root"]},"Action":["ks3:*"],"Effect":"Allow"}]}')
  print("got setResp, request_id: ", setResp.response_metadata.request_id)
  policy = bucket.get_bucket_policy()
  print("got policy, request_id: ", policy.response_metadata.request_id)
  print(policy.data)
  deleteResp = bucket.delete_bucket_policy()
  print("got deleteResp, request_id: ", deleteResp.response_metadata.request_id)

def getBucketLifeCycle(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  lifecycle = bucket.get_bucket_lifecycle()
  print("get_bucket_lifecycle, request_id: ", lifecycle.response_metadata.request_id)
  print(lifecycle.to_xml())

def setBucketLifeCycle(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  lifecycle = BucketLifecycle()
  # id 和 status 必须
  rule = LifecycleRule(id='rule1', status='Enabled')
  date = datetime(2021, 9, 12).strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
  rule.expiration = LifecycleExpiration(date=date)
  lifecycle.rule = [rule]
  resp = bucket.set_bucket_lifecycle(lifecycle)
  print("set_bucket_lifecycle, request_id: ", resp.response_metadata.request_id)


def setBucketLifeCycle2(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  tag = Tag(key="tag1", value="test1")
  # 筛选前缀为 prefix1、标签为 tag1:test1 的 objects，设置过期规则，在其最后修改时间3天后过期。
  rule1 = LifecycleRule('rule1', LifecycleFilter('prefix1', tags=[tag]),
                        status='Enabled',
                        expiration=LifecycleExpiration(days=3))

  # 设置过期规则，筛选标签为 tag1:test1 的 objects，最后修改时间在指定日期之前的，过期
  rule2 = LifecycleRule('rule2', LifecycleFilter(tags=[tag]),
                        status='Enabled',
                        expiration=LifecycleExpiration(
                          date=datetime(2021, 12, 12).isoformat(timespec='seconds') + '+08:00'))

  # 设置存储类型转换规则，筛选前缀为 prefix3 的 objects，在其最后修改时间20天之后转为低频访问类型，在其最后修改时间30天之后转为归档类型。
  rule3 = LifecycleRule('rule3', LifecycleFilter('prefix3'),
                        status='Enabled',
                        transitions=[LifecycleTransition(days=20, storage_class='STANDARD_IA'),
                                     LifecycleTransition(days=60, storage_class='ARCHIVE')])

  # 设置存储类型转换规则，筛选前缀为 prefix3 的 objects，最后修改时间在指定日期之前的，转为低频访问类型
  rule4 = LifecycleRule('rule4', LifecycleFilter('prefix4'),
                        status='Enabled',
                        transitions=[
                          LifecycleTransition(date=datetime(2021, 12, 12).isoformat(timespec='seconds') + '+08:00',
                                              storage_class='STANDARD_IA')])
  # 设置分片上传碎片清理规则，筛选前缀为 prefix5 的 part，在最后修改时间7天后删除
  rule5 = LifecycleRule('rule5', LifecycleFilter('prefix5'),
                        status='Enabled',
                        abort_incomplete_multipart_upload=AbortIncompleteMultipartUpload(days_after_initiation=7))

  # print(rule1.to_xml())
  # print(rule2.to_xml())
  # print(rule3.to_xml())
  # print(rule4.to_xml())
  # print(rule5.to_xml())
  lifecycle = BucketLifecycle([rule1, rule2, rule3, rule4, rule5])
  resp = bucket.set_bucket_lifecycle(lifecycle)
  print("set lifecycle, request_id: ", resp.response_metadata.request_id)

def deleteBucketLifeCycle(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.delete_bucket_lifecycle()
  print("delete_bucket_lifecycle, request_id: ", resp.response_metadata.request_id)

def enableBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.enable_logging(bucket, target_prefix='hehehehe')
  print("enable_logging, request_id: ", resp.response_metadata.request_id)

def disableBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.disable_logging()
  print("disable_logging, request_id: ", resp.response_metadata.request_id)

def getBucketCors(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  cors = bucket.get_bucket_cors()
  print("got cors, request_id: ", cors.response_metadata.request_id)
  print(cors.to_xml())

def putBucketCors(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  cors = BucketCors([CORSRule(origins=["http://dev.ksyun.com"], methods=["GET", "HEAD"], max_age="200", headers=["content-type"], exposed_headers=["content-type", "x-kss-acl"])])
  print('cors: ', cors.to_xml())
  resp = bucket.set_bucket_cors(cors)
  print("set_bucket_cors, request_id: ", resp.response_metadata.request_id)

def deleteBucketCors(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.delete_bucket_cors()
  print("delete_bucket_cors, request_id: ", resp.response_metadata.request_id)

def getBucketCrr(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  crr = bucket.get_bucket_crr()
  print("got bucket crr, request_id: ", crr.response_metadata.request_id)
  print(crr.to_xml())

def setBucketCrr(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  # deleteMarkerStatus 的值为 Enabled 和 Disabled
  # historicalObjectReplication 表示是否开启存量复制，值为 Enabled 和 Disabled
  resp = bucket.set_bucket_crr('test-bucket-repli', deleteMarkerStatus=BucketCrossReplicate.ENABLED,
                        historicalObjectReplication=BucketCrossReplicate.ENABLED, prefix=['hello'])
  print("set bucket crr, request_id: ", resp.response_metadata.request_id)

def deleteBucketCrr(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.delete_bucket_crr()
  print("delete bucket crr, request_id: ", resp.response_metadata.request_id)

def getBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.get_bucket_logging()
  print("got bucket logging, request_id: ", resp.response_metadata.request_id)
  print("got bucket logging, xml: ", resp.to_xml())

def setBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  blogging = BucketLogging(target=bucket_name)
  resp = bucket.set_bucket_logging(blogging.to_xml())
  print("set_bucket_logging, request_id: ", resp.response_metadata.request_id)

def getBucketMirror(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  mirror = bucket.get_bucket_mirror()
  print("got bucket mirror, request_id: ", mirror.response_metadata.request_id)
  print("got bucket mirror, content: ", mirror.data)

def setBucketMirror(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  set_headers = [{
      "key": "d",
      "value": "b"
  }]
  remove_headers = [{
      "key": "d"
  }]
  pass_headers = [{
      "key": "abc"
  }]
  header_setting = HeaderSetting(set_headers=set_headers, remove_headers=remove_headers, pass_all=False, pass_headers=pass_headers)
  mirror_request_setting = MirrorRequestSetting(pass_query_string=False, follow3xx=False, header_setting=header_setting)
  async_mirror_rule = AsyncMirrorRule.rule_with_acl(mirror_urls=["http://abc.om", "http://www.wps.cn"], saving_setting_acl="private")
  sync_mirror_rules = SyncMirrorRules.rules_with_prefix_acl(key_prefixes=["abc"], mirror_url="http://v-ks-a-i.originalvod.com", mirror_request_setting=mirror_request_setting, saving_setting_acl="private")
  mirror = BucketMirror(use_default_robots=False, async_mirror_rule=async_mirror_rule, sync_mirror_rules=[sync_mirror_rules])
  resp = bucket.set_bucket_mirror(mirror)
  print("set bucket mirror, request_id: ", resp.response_metadata.request_id)

def deleteBucketMirror(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.delete_bucket_mirror()
  print("delete bucket mirror, request_id: ", resp.response_metadata.request_id)


def setBucketRetention(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  bucket_retention = BucketRetention()
  # 设置回收站规则：启用/禁用、文件保留天数
  rule = RetentionRule(RetentionRule.ENABLED, 2)
  # rule = RetentionRule(RetentionRule.DISABLED, 2)
  bucket_retention.rule = rule
  bucket.set_bucket_retention(bucket_retention)


def getBucketRetention(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  ret = bucket.get_bucket_retention()
  print(ret.to_xml())


def listRetention(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list_retention()
  for k in keys:
    print(k.name)
    print(k.retention_id)
    print(k.storage_class)


def clearObject(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key('clear_key_name')
  k.clear_object('<retention_id>')


def recoverObject(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key('recover_key_name')
  # 如果retention_id为空，默认恢复回收站中指定key的最新版本
  k.recover_object(overwrite=True, retention_id='<retention_id>')


def setBucketInventory(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  # 添加清单规则，规则名为inventory1，状态为开启
  # 清单报告以CSV的格式存储，存储路径为target_account账号下的target_bucket桶，前缀为inventory1_的文件
  # 报告生成频率为每周一次
  # 扫描指定前缀和最后修改时间范围的对象
  # 清单结果中包含 文件大小 和 最后修改时间 的信息
  inventory = BucketInventory(id='inventory1', is_enabled=True,
                              destination=Destination(Destination.FORMAT_CSV,
                                                      bucket=bucket_name, prefix='inventory1_'),
                              schedule=Schedule(Schedule.WEEKLY),
                              filter=InventoryFilter(prefix='a', last_modify_begin_time_stamp=int(time.time())),
                              optional_fields=[BucketInventory.OPTIONAL_FIELD_SIZE,
                                               BucketInventory.OPTIONAL_FIELD_LAST_MODIFIED_DATE])
  print(inventory.to_xml())
  resp = bucket.set_bucket_inventory(inventory)
  print("set_bucket_inventory, request_id: ", resp.response_metadata.request_id)

def getBucketInventory(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  inventory = bucket.get_bucket_inventory('inventory1')
  print("get_bucket_inventory, request_id: ", inventory.response_metadata.request_id)
  print(inventory.to_xml())

def listBucketInventory(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  result = bucket.list_bucket_inventory()
  print("list_bucket_inventory, request_id: ", result.response_metadata.request_id)
  for inventory in result.inventory_configurations:
    print(inventory.to_xml())

def deleteBucketInventory(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.delete_bucket_inventory('inventory1')
  print("delete_bucket_inventory, request_id: ", resp.response_metadata.request_id)


#####################  ks3.billing  ###########################
from ks3.billing import get_buckets_data, query_ks3_data, query_bucket_rank

def getBucketsData(bucket_names=None):
  try:
    data = get_buckets_data(ak, sk, action="QueryBucketRank", start_time="202311192300", end_time="202311192359", bucket_names=bucket_names, products="", inner_api=True)
    print(data)
  except Exception as e:
    print(e.request_id)
    print(e)

def queryKs3Data(bucket_names=None):
  try:
    data = query_ks3_data(ak, sk, start_time="202311192300", end_time="202311192359", bucket_names=bucket_names, inner_api=True)
    print(data)
  except Exception as e:
    print(e.request_id)
    print(e)

def queryBucketRank(number):
  try:
    data = query_bucket_rank(ak, sk, start_time="202406192300", end_time="202407192359", inner_api=True, number=number)
    print(data)
  except Exception as e:
    print(e.request_id)
    print(e)

#####################  ks3.object  ###########################
def get_object_meta(bucket_name, object_key_name, headers=None):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.get_key_meta(object_key_name, headers=headers)
  if resp:
    print("获取文件header成功: \n", resp.data.headers)
    print('get_key_meta, request_id: %s' % resp.response_metadata.request_id)

def uploadObjectFromFile(filename):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key(filename)
  ret = k.set_contents_from_filename(os.path.expanduser("~") + '/Downloads/' + filename)
  if ret and ret.status == 200:
    print("上传成功")
    print("requestid:", ret.headers['x-kss-request-id'])
    print("requestid:", ret.response_metadata.request_id)

# def upload_async(filename):
#   bucket = conn.get_bucket(bucket_name)
#   k = bucket.new_key(filename)
#   ret = asyncio.run(k.upload_file_async(os.path.expanduser("~") + '/Downloads/' + filename))
#   if ret and ret.status == 200:
#     print("上传成功")

def uploadObjectFromString(type='ARCHIVE'):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key('大家好')
  # # key 和 value 需要 url 编码
  # taggingStr = 'name=jh'
  # headers = {'x-kss-tagging': taggingStr}
  headers = {}
  if type is not None:
    headers['x-kss-storage-class'] = type

  ret = k.set_contents_from_string('1234', headers=headers)
  # # 请求ID。请求ID是本次请求的唯一标识，强烈建议在程序日志中添加此参数。
  # print(ret.headers['x-kss-request-id'])
  print(ret.response_metadata.request_id)
  # # ETag是put_object方法返回值特有的属性，用于标识一个Object的内容。
  # print(ret.headers)
  # HTTP返回码。
  if ret and ret.status == 200:
    print("上传成功")

def headObject():
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key('test_encryption')
  if k:
    print(k.name, k.size, k.last_modified, k.object_type, k.tagging_count)

def downloadObjectAndPrint(keyname, byte_range=(0, 1), headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(keyname)
  ret = k.get_contents_as_string(byte_range=byte_range, headers=headers)
  print('request_id: %s' % ret.response_metadata.request_id)
  s = ret.data.decode()
  print('打印字符串: %s' % s)

# 定义一个模拟 I/O 操作的协程
async def io_task(task_id, delay):
    print(f"Task {task_id} started, will sleep for {delay} seconds")
    await asyncio.sleep(delay)  # 模拟 I/O 操作
    print(f"Task {task_id} finished")

async def _wrap_func(method, keyname_or_filename):
    start = datetime.now()
    result = await method(keyname_or_filename)
    end = datetime.now()
    return result, start, end
async def download_async(keynames, headers=None):
  async_start_time = datetime.now()
  bucket = conn.get_bucket(bucket_name)
  tasks = []
  for index, keyname in enumerate(keynames):
    k = bucket.get_key(keyname)
    # task = _wrap_func(k.download_file_async, os.path.expanduser("~") + '/Downloads/' + keyname)
    print('download_async[%s]: %s' % (async_start_time, os.path.expanduser("~") + '/Downloads/down_' + keyname))
    task = k.download_file_async(os.path.expanduser("~") + '/Downloads/down_' + keyname)
    tasks.append(task)
  rets = await asyncio.gather(*tasks, return_exceptions=True)
  # 打印某一个任务的requestid
  print('rets[0] requestid:', rets[0].response_metadata.request_id)
  async_end_time = datetime.now()
  # print('下载异步耗时: ', async_end_time - async_start_time)
  return rets

def upload_files(keynames, headers=None):
  bucket = conn.get_bucket(bucket_name)
  tasks = []
  for keyname in keynames:
    k = bucket.new_key(keyname)
    print('upload_files', os.path.expanduser("~") + '/Downloads/' + keyname)
    k.set_contents_from_filename(os.path.expanduser("~") + '/Downloads/' + keyname, headers=headers)

async def upload_async(filenames, headers=None):
  async_start_time = datetime.now()
  bucket = conn.get_bucket(bucket_name)
  tasks = []
  for index, filename in enumerate(filenames):
    k = bucket.new_key(filename)
    print('upload_async[%s]: %s' % (async_start_time, os.path.expanduser("~") + '/Downloads/' + filename))
    task = k.upload_file_async(os.path.expanduser("~") + '/Downloads/' + filename)
    tasks.append(task)
  results = await asyncio.gather(*tasks, return_exceptions=True)
  # 打印某一个任务的requestid
  print('results[0] requestid:', results[0].response_metadata.request_id)
  return results

  # 打印结果
  for i, result in enumerate(results, 1):
      if isinstance(result, Exception):
          print(f"Task {i} raised an exception: {result}")
      else:
        if result and result.status == 200:
          print(f"Task {i} 上传成功")
  async_end_time = datetime.now()
  # print('上传异步耗时: ', async_end_time - async_start_time)

def download_file(keyname, headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(keyname)
  print('download_file', os.path.expanduser("~") + '/Downloads/' + keyname)
  ret = k.get_contents_to_filename(os.path.expanduser("~") + '/Downloads/' + keyname, headers=headers)
  print('download_file request_id: %s' % ret.response_metadata.request_id)

def download_files(keynames, headers=None):
  bucket = conn.get_bucket(bucket_name)
  tasks = []
  for keyname in keynames:
    k = bucket.get_key(keyname)
    print('download_files', os.path.expanduser("~") + '/Downloads/down_' + keyname)
    k.get_contents_to_filename(os.path.expanduser("~") + '/Downloads/down_' + keyname, headers=headers)

def downloadObjectAsStreamAndPrint():
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key('shake.txt')
  bytes = k.read(300)
  print('start: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
  while bytes:
    s = bytes.decode()
    print('bytes decoded:', s)
    time.sleep(1)
    bytes = k.read(300)
  print('end: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

def downloadObjectAndSave(key_name, byte_range=(0, 1), headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(key_name)
  k.get_contents_to_filename('/Users/jabbar/Downloads/DSC03380.encrypt.非分块.jpg.download', headers=headers)

def deleteObject(key_name):
  bucket = conn.get_bucket(bucket_name)
  try:
    ret = bucket.delete_key(key_name)
    print("删除成功, request_id: ", ret.response_metadata.request_id)
  except Exception as e:
    print("删除失败")
    print(e)

def getObjectAcl():
  bucket = conn.get_bucket(bucket_name)
  policy = bucket.get_acl('article.txt')
  print("got acl_policy, request_id: ", policy.response_metadata.request_id)
  for grant in policy.acl.grants:
    print(grant.permission, grant.display_name, grant.email_address, grant.id)
  print(policy.to_xml())

def setObjectAcl():
  bucket = conn.get_bucket(bucket_name)
  # object policy : private | public-read | public-read-write
  bucket.set_acl("public-read", '<YOUR_KEY_NAME>')

def setObjectMeta():
  b = conn.get_bucket(bucket_name)
  b.copy_key('<yourKeyName>', '<yourBucketName>', '<yourKeyName>',
             headers={'content-type': 'text/plain', 'x-kss-metadata-directive': 'REPLACE'})

def setObjectStorageClass():
  b = conn.get_bucket(bucket_name)
  b.copy_key('<yourKeyName>', '<yourBucketName>', '<yourKeyName>', headers={'x-kss-storage-class': 'STANDARD_IA'})

def copy(dstKey, srcKey, dst_bucket_name=None, headers=None):
  # bucket_name = 'happyhour'
  b = conn.get_bucket(bucket_name)
  ret = b.copy_key(dstKey, dst_bucket_name, srcKey, headers=headers)
  print("copy_key, request_id: ", ret.response_metadata.request_id)
  return ret

def copy_encryption(dstKey, srcKey, encrypt_key=None):
  b = conn.get_bucket(bucket_name)
  b.copy_key(dstKey, bucket_name, srcKey, encrypt_key=encrypt_key)

def list_objects_truncated():
  bucket = conn.get_bucket('test-bucket')
  keys = bucket.get_all_keys(max_keys=3)
  print("got keys: request_id is: ", keys.response_metadata["request_id"])
  for k in keys:
    print('object:', k.name)

def list_objects():
  bucket = conn.get_bucket('test-bucket')
  keys = bucket.list(prefix='16')
  print("list, request_id: ", keys.response_metadata.request_id)
  res1 = [k.name for k in keys]
  print('res1 : ', res1)

  keys2 = bucket.listObjects(prefix='16')
  # res2 = [k.name for k in keys2]
  print('keys2 : ', keys2)
  # for k in keys:
  #   print('object:', k.name)

def list_objects_v2_truncated():
  bucket = conn.get_bucket('test-bucket')
  keys = bucket.get_all_keys(list_type=2, max_keys=3)
  print("got keys: request_id is: ", keys.response_metadata["request_id"])
  for k in keys:
    print('object:', k.name)

def list_objects_v2(delimiter='#', prefix=None, max_keys=None, marker=None, encoding_type='', fetch_owner=True):
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list_v2(delimiter=delimiter, prefix=prefix, max_keys=max_keys, marker=marker, encoding_type=encoding_type, fetch_owner=fetch_owner)
  for k in keys:
    print('object:', k.name)

def list_objects_v2_no_params():
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list_v2()
  for k in keys:
    print('object:', k.name)


def listObjectsMore(bucket_name, delimiter=None, prefix=None, max_keys=None, marker=None):
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list(delimiter=delimiter, prefix=prefix, max_keys=max_keys, marker=marker)
  # print(len(keys))
  res = [k.name for k in keys]
  print('res: ', res)
  # print('item:', k.name, type(k))

def listAndDelete():
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list(delimiter='/', max_keys=10, prefix='15')
  print(keys.marker)
  for k in keys:
    print('object:', k.name)
    deleteObject(k.name)

def listObjectsAndFilter(endTime=None):
  bucket = conn.get_bucket('auto-test-bucket')
  keys = bucket.listObjects(delimiter='/', max_keys=2) # start_time=1640331446, end_time=1641895096
  for k in keys:
    print(k)

def getObjectTagging():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.get_key('testTagging')
  tagging = key.get_object_tagging()
  print("get_object_tagging, request_id: ", tagging.response_metadata.request_id)
  print(tagging.to_xml())

def setObjectTagging():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.get_key('testTagging')
  tagging = [Tag('0'), Tag('1', '1')]
  ret = key.set_object_tagging(tagging)
  print("set_object_tagging, request_id: ", ret.response_metadata.request_id)

def deleteObjectTagging():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.get_key('testTagging')
  ret = key.delete_object_tagging()
  print("delete_object_tagging, request_id: ", key.response_metadata.request_id)

def calcFolderSize(bucket, folder):
  length = 0
  keys = bucket.list(prefix=folder)
  for k in keys:
    if isinstance(k, Key):
      length += k.size
  return length

from ks3.prefix import Prefix

# 列举指定目录下的文件大小
def getFolderSizeInBucket():
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list(delimiter='/')
  for k in keys:
    if isinstance(k, Prefix):
      print('dir: ' + k.name + '  size:' + str(calcFolderSize(bucket, k.name)) + "Byte")


def test_multipart_upload(file_path = None, encrypt_key=None):
  import math, os
  from filechunkio import FileChunkIO
  bucket = conn.get_bucket(bucket_name)

  source_path = '/Users/jiahua/Downloads/DSC03380.JPG' if not file_path else file_path
  # 源文件大小
  source_size = os.stat(source_path).st_size

  mp = bucket.initiate_multipart_upload("DSC03380.mp.jpg", encrypt_key=encrypt_key)
  print(mp)
  print('initiate_multipart_upload, requestid: ', mp.response_metadata.request_id)

  chunk_size = 5242880
  chunk_count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))

  # 通过 FileChunkIO 将文件分片
  for i in range(chunk_count):
    offset = chunk_size * i
    bytes = min(chunk_size, source_size - offset)
    with FileChunkIO(source_path, 'r', offset=offset, bytes=bytes) as fp:
      # 逐个上传分片
      ret = mp.upload_part_from_file(fp, part_num=i + 1)
      print('upload_part_from_file, requestid: ', ret.response_metadata.request_id)
  print(mp.to_xml())
  # 发送请求，合并分片，完成分片上传
  cmp = mp.complete_upload()
  print('complete_upload, requestid: ', cmp.response_metadata.request_id)
  if cmp and cmp.status == 200:
    print("上传成功")

def test_fetch_object():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.new_key('www-logo')
  ret = key.fetch_object(source_url='http://fe.ksyun.com/project/resource/img/www-logo.png',
                      headers={'x-kss-acl': 'public-read'})
  print(ret.headers['x-kss-request-id'])
  if ret and ret.status == 200:
    print('fetch成功')

def test_generate_url(key_name, image_attrs=None):
  b = conn.get_bucket(bucket_name)
  k = b.get_key(key_name)
  if k:
    url = k.generate_url(600, image_attrs=image_attrs)  # 60s 后该链接过期
    print(url)
  else:
    print('object not found')

def test_get_presigned_url(method=None, response_headers=None, key_name=None):
  b = conn.get_bucket(bucket_name)
  url = b.get_presigned_url(600, method=method, response_headers=response_headers, key_name=key_name)  # 60s 后该链接过期
  print(url)
  return url

def restoreObject(key_name):
  b = conn.get_bucket(bucket_name)
  k = b.get_key(key_name)
  ret = k.restore_object()
  print('restore_object, request_id: ', ret.response_metadata.request_id)

def test_put_via_presigned_url(key):
  url = test_get_presigned_url(key)
  with open('./article.txt', 'rb') as fp:
    result = requests.put(url, data=fp)
    print(result)

from ks3.sts import assumeRole
def test_assumeRole():
  try:
    print(assumeRole(ak, sk, "krn:ksc:iam::xxx:role/xx-test-bucket", "ks3", 3600))
  except Exception as e:
    print(e.request_id)
    print(e)

def put_object_callback(key_name):
  b = conn.get_bucket('hanjing-test000')
  # 新建对象key
  k = b.new_key(key_name)
  # 上传成功后，向回调地址POST数据
  # 需要设置`x-kss-callbackurl`和`x-kss-callbackbody`请求头，详见文档[上传回调处理](https://docs.ksyun.com/documents/956)。
  # x-kss-callbackurl 为发起回调时请求的服务器地址
  # x-kss-callbackbody 为发起回调时请求的body的值
  headers = {"x-kss-callbackurl": "https://yh-sh.ks3-cn-shanghai.ksyuncs.com", "x-kss-callbackbody": "objectKey=${key}&etag=${etag}&bucket=${bucket}&objectSize=${objectSize}&mimeType=${mimeType}&createTime=${createTime}", "x-kss-callbackauth":1}
  ret = k.set_contents_from_string("test-callback", headers=headers)
  if ret and ret.status == 200:
    print("上传成功")

def append_object_from_file(key_name, filename, position=0):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key(key_name)
  ret = k.append_object_from_filename('/Users/jiahua/Downloads/' + filename, position=position)
  if ret and ret.status == 200:
    print("上传成功")


def append_object_from_string(key_name, content, position=0):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key(key_name)
  ret = k.append_object_from_string(content, position=position)
  print("x-kss-next-append-position:", ret.headers['x-kss-next-append-position'])
  print("requestid:", ret.response_metadata.request_id)
  if ret and ret.status == 200:
    print("上传成功")
  return ret

def getObjectMeta(object_key_name, headers=None):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.get_key_meta(object_key_name, headers=headers)
  if resp:
    print("获取文件header成功: ", resp.headers)
    print("next-append: ", type(resp.headers['x-kss-next-append-position']))
  return resp

async def up_down():
  async_start_time = datetime.now()
  ret = await asyncio.gather(
    download_async(
      ['DSC03380.JPG']),
    upload_async(
      ['DSC03380.JPG'])
  )
  # await download_async(['DSC03380.JPG', 'DSC03380.cp.jpg'])
  async_end_time = datetime.now()
  print('异步耗时: ', async_end_time - async_start_time)
  return ret

# try:
#   result = append_object_from_string("test_append1", "hello ")
# except S3ResponseError as e:
#   print('status: %s, reason: %s, request_id: %s, body: %s' % (e.status, e.reason, e.request_id, e.body))

#
# result = getObjectMeta("test_append4")
# append_object_from_string("test_append3", "world", position=int(result.headers['x-kss-next-append-position']))
# append_object_from_file("test_append3", "test_append", position=int(result.headers['x-kss-next-append-position']))

# getAllBuckets()
# head_bucket_shadowcopy('a-beijing-bucket')
# getBucketLocation('test-host-style')
# createBucket('test-bucket-222222', location='SHANGHAI')
# deleteBucket('test-bucket-222222')
# getBucketAcl('test-bucket')
# setBucketAcl('test-bucket')
# try:
#   getBucketLifeCycle(bucket_name)
# except:
#   setBucketLifeCycle(bucket_name)

# setBucketLifeCycle2(bucket_name)
# getBucketLifeCycle(bucket_name)
# deleteBucketLifeCycle(bucket_name)
# getBucketLogging(bucket_name)
# setBucketLogging(bucket_name)
# disableBucketLogging(bucket_name)
# enableBucketLogging(bucket_name)
# putBucketCors(bucket_name)
# getBucketCors(bucket_name)
# deleteBucketCors(bucket_name)
# setBucketCrr(bucket_name)
# getBucketCrr(bucket_name)
# deleteBucketCrr(bucket_name)
# setBucketMirror(bucket_name)
# getBucketMirror(bucket_name)
# deleteBucketMirror(bucket_name)
# manageBucketPolicy(bucket_name)
# getBucketMirror(bucket_name)
# setBucketInventory(bucket_name)
# getBucketInventory(bucket_name)
# listBucketInventory(bucket_name)
# deleteBucketInventory(bucket_name)
##### object #####
# get_object_meta(bucket_name, 'article.txt')
# list_objects_truncated()
# list_objects()
# list_objects_v2_truncated()
# list_objects_v2(delimiter=None)
# list_objects_v2_no_params()
# listObjectsMore("auto-test-bucket", delimiter='/', max_keys=2, marker='1050')
# listObjectsMore("auto-test-bucket", delimiter='/', max_keys=2, marker='105/')
# listObjectsMore("auto-test-bucket", delimiter='/', max_keys=2, marker='105%2F')
# listObjectsAndFilter()
# setObjectTagging()
# getObjectTagging()
# deleteObjectTagging()
# getFolderSizeInBucket();
# downloadObjectAndPrint(keyname="1659684872.torrent")
# downloadObjectAsStreamAndPrint()
# downloadObjectAndSave(bucket_name, 'DSC03380.encrypt.非分块.jpg', headers={
#   'range': 'bytes=0-5242880'
# })
# count = 20
# while True:
# uploadObjectFromFile('3_7240456.jpeg')

# 异步下载和同步下载对比

#
# try:
#   # 'DSC03380.cp.jpg', 'DSC03380.mp.jpg', 'DSC03384.JPG', 'DSC03384.cp.JPG', 'DSC03384.cp2.JPG'
# run_ret = asyncio.run(up_down())
# print(run_ret)

# download_file('DSC03380.JPG')
#   # asyncio.run(upload_async(
#   #   ['DSC03380.JPG', 'DSC03380.jpg', 'DSC03380.cp.jpg', 'DSC03380.mp.jpg', 'DSC03384.JPG', 'DSC03384.cp.JPG',
#   #    'DSC03384.cp2.JPG']))
#   # print(download_results[0].request_id)
#   # print(download_results[1].request_id)
#   # print(download_results[2].request_id)
#   # start_time = datetime.now()
#   # download_files(['DSC03380.JPG', 'DSC03380.jpg', 'DSC03380.cp.jpg', 'DSC03380.mp.jpg', 'DSC03384.JPG', 'DSC03384.cp.JPG'])
#   # upload_files(
#   #   ['DSC03380.JPG', 'DSC03380.jpg', 'DSC03380.cp.jpg', 'DSC03380.mp.jpg', 'DSC03384.JPG', 'DSC03384.cp.JPG',
#   #    'DSC03384.cp2.JPG'])
#   # end_time = datetime.now()
#   # print('同步耗时: ', end_time - start_time)
# except Exception as e:
#   print('下载失败', e)
#   raise

# # 异步上传和同步上传对比
# try:
#   asyncio.run(upload_async(
#     ['DSC03380.JPG', 'DSC03380.jpg', 'DSC03380.cp.jpg', 'DSC03380.mp.jpg', 'DSC03384.JPG', 'DSC03384.cp.JPG',
#      'DSC03384.cp2.JPG']))
#
#   start_time = datetime.now()
#   upload_files(
#     ['DSC03380.JPG', 'DSC03380.jpg', 'DSC03380.cp.jpg', 'DSC03380.mp.jpg', 'DSC03384.JPG', 'DSC03384.cp.JPG',
#      'DSC03384.cp2.JPG'])
#   end_time = datetime.now()
#   print('上传同步耗时: ', end_time - start_time)
# except Exception as e:
#   print('上传失败', e)

# upload_files(['DSC03380.JPG'])

# uploadObjectFromFile('xab')
# uploadObjectFromFile('法治.jpeg')
# upload_async('11.jpeg')
# uploadObjectFromFile('11.jpeg')
# uploadObjectFromFile('xac')
#   time.sleep(5)
#   count = count - 1
# uploadObjectFromString()
# headObject()
# downloadObjectAndPrint('test_directory/')
# deleteObject("大家好")
# getObjectAcl()

# test_multipart_upload()

# test_fetch_object()
# def test_generate_url(key_name, image_attrs=None):
#   b = conn.get_bucket(bucket_name)
#   k = b.get_key(key_name)
#   if k:
#     url = k.generate_url(600, image_attrs=image_attrs)  # 60s 后该链接过期
#     print(url)
#   else:
#     print('object not found')

# bucket = conn.get_bucket('test-bucket')
# keys = bucket.list()
# for k in keys:
#   print(k)
#   if isinstance(k, Key):
#     url = k.generate_url(600)
#     res = requests.get(url)
#     if res.status_code != 200:
#       print(url)


# res = requests.get(url)
# assert res.status_code != 403
# test_generate_url('\\a\\\\:<>*?|:q.jpeg')
# test_generate_url('#x2;.jp.csv')
# test_generate_url('10086/198.18-reset-共计9条.txt')
# test_generate_url('10086/getbucket.csv')
# test_put_via_presigned_url('index.html')
# list_objects_v2(delimiter='/', encoding_type='url', fetch_owner=False)
# list_objects()
# listObjectsMore()
# deleteObject()
# listObjectsAndFilter()
# listAndDelete()
# uploadObjectFromString()
# restoreObject("大家好")
# getBucketsData("test-bucket")
# queryKs3Data("test-bucket")
# queryBucketRank(10)
# test_assumeRole()
# getBucketLogging(bucket_name)

# copy_encryption('article.encryption.txt', 'article.txt', encrypt_key=True)

# fileName = "\u006b\u0073\u005f\u0073\u0063\u0061\u006e\u005f\u006f\u0063\u0072\u002f\u0032\u0030\u0031\u0038\u002d\u0030\u0033\u002d\u0031\u0032\u002f\u0010\ufffd\u0070\ufffd\ufffd\ufffd\u0002\u002e\u0057\u007f\u005b\ufffd\u0008\ufffd\u002a\ufffd\u002e\u006a\u0070\u0067";
# hehe = "�p���.W[�*�.jpg"
# for c in hehe:
#     print(repr(c), c)
# urlcoded = urllib.parse.quote(fileName)
# unquoted = urllib.parse.unquote('%FF')
# quoted = urllib.parse.quote(unquoted)
# print(unquoted)
# print(quoted)

# getObjectMeta('test-bucket', 'article.txt')
# key = copy('article.txt', 'article.txt', dst_bucket_name='test-bucket')
# getObjectMeta('test-bucket', 'article.txt')
# getObjectMeta('test-bucket', 'DSC03380.ssec.jpg')
# uploadObjectFromFile('DSC03380.jpg')

# import base64
# import hmac
# import hashlib
# import urllib
# h = hmac.new("accesskey",
#              "GET\n\n\n1141889120\n/examplebucket/oss-api.pdf",
#              hashlib.sha1)
# urllib.quote (base64.encodestring(h.digest()).strip())

# b = conn.get_bucket(bucket_name)
# all_uploads = b.get_all_multipart_uploads()
# print("get_all_multipart_uploads, request_id: ", all_uploads.response_metadata.request_id)
# for p in all_uploads:
#   some_mp = p
#   ret = p.cancel_upload()
#   if ret and ret.status == 204:
#     print('cancel_upload success')
#   print('cancel_upload, id: %s, status: %s, requestid: %s' % (p.id, ret.status, ret.response_metadata.request_id))
#   break

# all_parts = some_mp.get_all_parts()
# print("get_all_parts, request_id: ", all_parts.response_metadata.request_id)
# for part in all_parts:
#   print('part etag:%s' % part.etag)
#   print('part_number:%s' % part.part_number)


# 获取指定分片上传
# p = b.get_all_multipart_uploads(key_marker='DSC03380.encrypt.jpg-dddddddd')[0]
# p.cancel_upload()

# all_uploads = b.get_all_multipart_uploads(key_marker='DSC03380.encrypt.jpg-dddddddd')#max_uploads=27)
# print(len(all_uploads))
# for p in all_uploads:
#   print(p, p.id)
# put_object_callback('test-callback')

# import math, os
#
# b = conn.get_bucket(bucket_name)
# # 目标key名
# target_key_name = 'test_copy_part'
# # 获取源key的元数据信息
# source_key = b.get_key("DSC03380.jpg")
# source_size = source_key.size
#
# mp = b.initiate_multipart_upload(target_key_name)
# print('initiate_multipart_upload, requestid: ', mp.response_metadata.request_id)
#
# chunk_size = 5242880
# count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))
#
# for i in range(count):
#     start = chunk_size * i
#     end = min(start + chunk_size - 1, source_size - 1)
#     ret = mp.copy_part_from_key(bucket_name, source_key.name, i + 1, start, end)
#     print(ret.etag, ret.last_modified, ret.ChecksumCRC64ECMA)
#     print('copy_part_from_key, requestid: ', ret.response_metadata.request_id)
#
# cmp = mp.complete_upload()
# print('complete_upload, requestid: ', cmp.response_metadata.request_id)
# if cmp and cmp.status == 200:
#     print("复制成功")

# 生成listObjects外链
b = conn.get_bucket('happyhour')
# # 拉取prefix为16/的对象列表
# list_params = {'prefix': '16/'}
# # conditions = [['starts-with','$key', '16/'], {'bucket': bucket_name}]
# conditions = [
#   {"bucket": "gzz-test"},
#   ["starts-with", "$key", "abc/"],
#   ["starts-with", "$key", "aaa/abc/"],
#   ["eq", "$key", "exampleobject"],
#   ["eq", "$key", "exampleobject1"]
# ]
# # 外链地址60s后过期
# url = b.presign(1741746992, method="GET", params=list_params, conditions=conditions, expires_in_absolute=True)
# print(url)

share_code = b.create_share_code(auth_code=b'123456', prefix="16/")
print('share_code:', share_code)

from ks3.share_encryption import ShareCryptor
shareCryptor = ShareCryptor(b'123456')
dec_url = shareCryptor.decrypt(share_code)
print(dec_url)

# # 生成分块上传的外链
# init_mpu_url = b.get_presigned_url(60, method="POST", key_name='DSC03380.mp.jpg', params={'uploads': None})
# print(init_mpu_url)
# result = requests.post(url=init_mpu_url)
# print(result.headers['x-kss-request-id'])
# print(result)


# # list分块上传任务
# list_mpu_params = {'key-marker': 'DSC03380.mp.jpg', 'upload-id-marker': '!', 'uploads': None, 'max-uploads': '2'}
# list_mpu_url = b.get_presigned_url(60, method="GET", params=list_mpu_params)
# print(list_mpu_url)
# list_mpu_result = requests.get(url=list_mpu_url)
# # print(list_mpu_result.content)
# # xml序列化content，然后取最后一个
# from xml.etree import ElementTree
# root = ElementTree.fromstring(list_mpu_result.content)
# # 提取命名空间
# namespace = {'ns': 'http://s3.amazonaws.com/doc/2006-03-01/'}
# uploads = root.findall('.//ns:Upload', namespace)
# last_upload = uploads[0]
# key = last_upload.find('ns:Key', namespace).text
# upload_id = last_upload.find('ns:UploadId', namespace).text
# print(key, upload_id)
#
# upload_mpu_url = b.get_presigned_url(60, method="PUT", key_name=key, params={'partNumber': '1', 'uploadId': upload_id})
# print(upload_mpu_url)
# result = requests.put(url=upload_mpu_url, data='hello')
# print(result)
# print(result.headers['x-kss-request-id'])
#
# # list分块
# list_parts_params = {'uploadId': upload_id}
# list_parts_url = b.get_presigned_url(60, method="GET", params=list_parts_params, key_name=key)
# print(list_parts_url)
# result = requests.get(url=list_parts_url)
# print(result)
# print(result.content)
# print(result.headers['x-kss-request-id'])
# # 分块上传合并
# # complete_data = '''<?xml version="1.0" encoding="UTF-8"?>
# # <CompleteMultipartUpload>
# #   <Part>
# #     <PartNumber>1</PartNumber>
# #   </Part>
# # </CompleteMultipartUpload>'''
# # complete_mpu_url = b.get_presigned_url(60, method="POST", key_name=key, params={'uploadId':upload_id})
# # print(complete_mpu_url)
# # result = requests.post(url=complete_mpu_url, data=complete_data)
# # print(result)
# # print(result.content)
# # print(result.headers['x-kss-request-id'])
#
#
# # 终止分块上传
# abort_mpu_url = b.get_presigned_url(60, method="DELETE", key_name='DSC03380.mp.jpg', params={'uploadId': upload_id})
# print(abort_mpu_url)
# result = requests.delete(url=abort_mpu_url)
# print(result)
# print(result.content)
# print(result.headers['x-kss-request-id'])
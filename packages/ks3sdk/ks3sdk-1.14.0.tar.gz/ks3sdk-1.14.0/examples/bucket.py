# -*- coding: utf-8 -*-
from ks3.connection import Connection
from datetime import datetime

####################公共头#########################

# 金山云主账号 AccessKey 拥有所有API的访问权限，风险很高。强烈建议您创建并使用子账号账号进行 API 访问或日常运维，请登录 https://uc.console.ksyun.com/pro/iam/#/user/list 创建子账号。
# 通过指定 host(Endpoint)，您可以在指定的地域创建新的存储空间。host(Endpoint) 以北京为例，其它 Region 请按实际情况填写。
conn = Connection('<yourAccessKeyId>', '<yourAccessKeySecret>', host='ks3-cn-beijing.ksyuncs.com')


####################内容#########################

# 创建存储空间。
# 如果需要在创建存储空间时设置存储空间访问权限，请参考以下代码。
# 以下以配置存储空间为私有访问权限。
# conn.create_bucket(bucket_name, policy='private')
# 默认创建私有访问权限的存储空间
conn.create_bucket('<yourBucketName>')
# 创建项目 id 为 105150 的归档存储空间
# header 中的 x-kss-bucket-type 为存储空间类型
conn.create_bucket('<yourBucketName>', project_id=105150, headers={"x-kss-bucket-type": "ARCHIVE"})

# 列举所有的存储空间。
# projectIds 为项目id，多个项目用,间隔的
buckets = conn.get_all_buckets(project_ids="25532")
for b in buckets:
	print(b.name)
# 列举存储空间的更多详情，请参见GetService（api地址）

# 获取存储空间的访问权限（暂时无法说明）
# 获取存储空间的访问权限，并打印出ACL设置以及授权的信息
b = conn.get_bucket('<yourBucketName>')
policy = b.get_acl()
for grant in policy.acl.grants:
	print(grant.id, grant.permission)

# 设置存储空间的访问权限
# 获取存储空间实例
b = conn.get_bucket('<yourBucketName>')
# 存储空间的访问权限, private or public-read or public-read-write
b.set_acl("public-read")

# 删除存储空间
conn.delete_bucket('<yourBucketName>')

# 如果存储空间下面存在文件，那么需要首先删除所有文件
for k in b.list():
	k.delete()
conn.delete_bucket('<yourBucketName>')

# 设置存储空间策略
b = conn.get_bucket('<yourBucketName>')
# 存储空间策略，授权id为32432423iam用户对此存储空间有完全控制的权限
policy = '{"Statement":[{"Resource":["krn:ksc:ks3:::jiangran123","krn:ksc:ks3:::jiangran123/*"],"Principal":{"KSC":["krn:ksc:iam::32432423:root"]},"Action":["ks3:*"],"Effect":"Allow"}]}'
# 设置存储空间策略
b.set_bucket_policy(policy=policy)
# 获取存储空间策略
policy = b.get_bucket_policy()
# 删除存储空间策略
b.delete_bucket_policy()

# 抓取网络资源上传
# 从第三方URL拉取文件，并上传至KS3某个 bucket 中存储成名为 object 的文件。
b.fetch_object('www-logo', source_url='http://fe.ksyun.com/project/resource/img/www-logo.png')
# 参见：[金山云官方文档-Put Object Fetch](https://docs.ksyun.com/documents/949)

# 在源存储空间设置复制规则
# 参数为目标桶名称和『是否开启删除复制』
# 若deleteMarkerStatus参数指定为Enabled为开启，若为Disabled或不指定均为关闭状态，若开启删除复制，则当源Bucket删除一个对象时，该对象在目标Bucket的副本也会删除
# 前缀匹配，如果object匹配了前缀规则才会对该对象进行复制，每条复制规则最多添加10条前缀匹配规则，且前缀之间不同重叠
b.set_bucket_crr('<yourTargetBucketName>', deleteMarkerStatus='Disabled', prefix_list=['hello'])
# 获取存储空间复制规则
bucket_crr = b.get_bucket_crr()
print(bucket_crr.to_xml())
# 删除存储空间复制规则
b.delete_bucket_crr()

# 管理生命周期规则
# 查看生命周期规则。
lifecycle = b.get_bucket_lifecycle()
print(lifecycle.to_xml())
# 设置生命周期规则
from ks3.xmlParsers.bucketLifecycle import BucketLifecycle, Rule as LifecycleRule, Filter as LifecycleFilter, Expiration as LifecycleExpiration, Transition as LifecycleTransition
from ks3.tagging import Tag
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
lifecycle = BucketLifecycle([rule1, rule2, rule3, rule4])
b.set_bucket_lifecycle(lifecycle)
# 删除生命周期规则
b.delete_bucket_lifecycle()

# 管理存储空间日志设置功能
# 注：只有bucket的所有者才有权限使用该接口
# 查看日志设置
print(b.get_bucket_logging().to_xml())
# 开启日志设置
from ks3.xmlParsers.bucketLogging import BucketLogging
# 第一个参数为目标桶实例或者目标桶的名称；target_prefix 为日志文件的前缀
b.enable_logging(b, target_prefix='test')
# 或者
# target为目标桶实例或者目标桶的名称；target_prefix 为日志文件的前缀
blogging = BucketLogging(target=b.name, target_prefix='test_log')
print(b.set_bucket_logging(blogging.to_xml()))
# 关闭日志设置
print(b.disable_logging())

# 管理存储空间 CORS 跨域规则
# 查看 CORS 跨域规则
print(b.get_bucket_cors().to_xml())
# 设置 CORS 跨域规则
from ks3.xmlParsers.bucketCors import BucketCors, CORSRule
# origins：允许跨域请求的来源地址；methods：允许跨域的请求方法；max_age: 指定浏览器对特定资源的预取(OPTIONS)请求返回结果的缓存时间,单位为秒; headers: 允许跨域的请求头部；exposed_headers: 允许跨域的响应头部
cors = BucketCors([CORSRule(origins=["http://dev.ksyun.com"], methods=["GET", "HEAD"], max_age="200", headers=["content-type"], exposed_headers=["content-type", "x-kss-acl"])])
# print('cors rules: ', cors.to_xml())
print(b.set_bucket_cors(cors))
# 删除 CORS 跨域规则
b.delete_bucket_cors()

# 管理存储空间回源功能
# 查看回源功能
print(b.get_bucket_mirror())
# 设置回源功能
from ks3.xmlParsers.bucketMirror import HeaderSetting, MirrorRequestSetting, AsyncMirrorRule, SyncMirrorRules, BucketMirror
'''
  异步回源规则，该字段与sync_mirror_rules必须至少有一个，可同时存在。
  mirror_urls: 一组源站url，数量不超过10个，url必须以http或者https开头
  saving_setting_acl: 文件上传KS3时，指定文件的权限。
'''
async_mirror_rule = AsyncMirrorRule.rule_with_acl(mirror_urls=["http://abc.om", "http://www.wps.cn"], saving_setting_acl="private")
# 自定义header，这些header的key和value均是固定的，ks3请求源站时会带上这些header。
set_headers = [{
    "key": "d",
    "value": "b"
}]
# 从客户端发给ks3的header中移除以下指定的header，通常与pass_all或者pass_headers配合使用，只能指定header中的key，不能指定value。
remove_headers = [{
    "key": "d"
}]
# 将客户端发给ks3的header中指定的几个透传给源站，只能指定header中的key，不能指定value。
pass_headers = [{
    "key": "abc"
}]

# pass_all: 将客户端发给ks3的header全部透传给源站，该字段与pass_headers互斥。
header_setting = HeaderSetting(set_headers=set_headers, remove_headers=remove_headers, pass_all=False, pass_headers=pass_headers)

# pass_query_string: ks3请求源站时是否将客户端请求ks3时的query string透传给源站。
# follow3xx: 设置访问源站时，是否follow 302/301。ks3是否响应源站的301和302跳转，如果为false且源站返回了302，则ks3会返回424给客户端，如果为true则ks3收到302后会请求302的location。
mirror_request_setting = MirrorRequestSetting(pass_query_string=False, follow3xx=False, header_setting=header_setting)
sync_mirror_rules = SyncMirrorRules.rules_with_prefix_acl(key_prefixes=["abc"], mirror_url="http://v-ks-a-i.originalvod.com", mirror_request_setting=mirror_request_setting, saving_setting_acl="private")

# use_default_robots: 是否使用默认的robots.txt，如果为true则会在bucket下生成一个robots.txt。
mirror = BucketMirror(use_default_robots=False, async_mirror_rule=async_mirror_rule, sync_mirror_rules=[sync_mirror_rules])
print(b.set_bucket_mirror(mirror))
# 删除回源功能
b.delete_bucket_mirror()



# -*- coding: utf-8 -*-
from ks3.billing import query_bucket_rank, query_ks3_data

####################公共头#########################

# 金山云主账号 AccessKey 拥有所有API的访问权限，风险很高。强烈建议您创建并使用子账号账号进行 API 访问或日常运维，请登录 https://uc.console.ksyun.com/pro/iam/#/user/list 创建子账号。

# bucket_names 为一个或者多个 bucket 名称，逗号间隔
# start_time 和 end_time 分别为起始时间和结束时间，时间格式为%Y%m%d%H%M%S，比如202503010000
# ks3_product 指的是查询单个或者多个计费项名称，逗号间隔；比如DataSize,RequestsGet；如果不填，则查询所有计费项（除带宽，带宽需单独查询）
# transfer 和 request 分别为可以查询单个或多个统计项的流量/请求次数情况，统计项以逗号分隔。可填参数：Object、Referer、IP、UA，返回TOP200数据
# 详情参考：https://docs.ksyun.com/documents/41328
query_ks3_data('<yourAccessKeyId>', '<yourAccessKeySecret>', bucket_names="<yourBucketName1>,<yourBucketName2>",
               start_time="202503010000", end_time="202503020000", date_type="Day", ks3_product="DataSize,RequestsGet",
               transfer='transfer', request='request')

# bucket_names 为一个或者多个 bucket 名称，逗号间隔
# start_time 和 end_time 分别为起始时间和结束时间，时间格式为%Y%m%d%H%M%S，比如202503010000
# ks3_product 指的是查询单个或者多个计费项名称，逗号间隔；比如DataSize,RequestsGet；如果不填，则查询所有计费项（除带宽，带宽需单独查询）
# number 为TOP排序的 Bucket 数量，取值范围为[1-200]
# 详情参考：https://docs.ksyun.com/documents/43119
query_bucket_rank('<yourAccessKeyId>', '<yourAccessKeySecret>', bucket_names="<yourBucketName1>,<yourBucketName2>",
               start_time="202503010000", end_time="202503020000", date_type="Day", ks3_product="DataSize,RequestsGet",
                  number=10)


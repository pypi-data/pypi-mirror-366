# coding:utf-8
import json

from ks3.exception import KS3ResponseError
from ks3.http import make_request_v4


def get_buckets_data(access_key_id, access_key_secret, start_time=None, end_time=None, action='QueryKs3Data',
                     bucket_names=None, products=None, date_type="Day", inner_api=False, **kwargs):
    """
    :param access_key_id: 金山云提供的ACCESS KEY ID
    :param access_key_secret: 金山云提供的SECRET KEY ID
    """
    query_args = {
        'Action': action,
        'Version': 'v1',
        'StartTime': start_time,
        'EndTime': end_time,
        'DateType': date_type
    }
    # not None and not ""
    if products:
        query_args['Ks3Product'] = products

    if bucket_names:
        query_args['Bucketname'] = bucket_names

    for k, v in list(kwargs.items()):
        if v:
            if k == 'transfer':
                query_args['Transfer'] = v
            elif k == 'request':
                query_args['Request'] = v
            elif k == 'number':
                query_args['Number'] = v
            else:
                query_args[k] = v

    response = make_request_v4(access_key_id, access_key_secret, method='GET', service='ks3bill',
                               region='cn-beijing-6', query_args=query_args, inner_api=inner_api)
    body = response.read()
    if response.status != 200:
        raise KS3ResponseError(response.status, response.reason, body)
    return json.loads(body)


def query_bucket_rank(access_key_id, access_key_secret, start_time=None, end_time=None, date_type="Day", number=10,
                      ks3_product=None, inner_api=False):
    """
    查询bucket使用量排行
    :param access_key_id: 金山云提供的ACCESS KEY ID
    :param access_key_secret: 金山云提供的SECRET KEY ID
    :param end_time: 查询用量开始时间：yyyyMMddHHmm
    :param start_time: 查询用量结束时间（与开始时间同月，不支持跨月查询）：yyyyMMddHHmm
    :param date_type: 支持按天粒度查询，固定值：Day
    :param ks3_product: 可以查询单个或多个统计项，以逗号分隔，如果不填，则查询所有统计项
    :param number: TOP排序的Bucket数量，取值范围为[1-200]
    """
    return get_buckets_data(access_key_id, access_key_secret, start_time=start_time, end_time=end_time, number=number,
                            action='QueryBucketRank', date_type=date_type, products=ks3_product, inner_api=inner_api)


def query_ks3_data(access_key_id, access_key_secret, start_time=None, end_time=None, date_type="Day", bucket_names=None,
                   ks3_product=None, transfer=None, request=None, inner_api=False):
    """
    查询bucket用量详情数据，包括容量、流量、带宽、请求次数、数据取回量、对象标签数等。
    查询业务分析数据，包括以Object、Referer、IP、UA为统计维度的流量或请求次数。

    :param access_key_id: 金山云提供的ACCESS KEY ID
    :param access_key_secret: 金山云提供的SECRET KEY ID
    :param end_time: 查询用量开始时间：yyyyMMddHHmm
    :param start_time: 查询用量结束时间（与开始时间同月，不支持跨月查询）：yyyyMMddHHmm
    :param date_type: 支持按天粒度查询，固定值：Day
    :param bucket_names: 存储空间名称，最多支持同时查询5个存储桶的用量明细，以逗号分隔
    :param ks3_product: 可以查询单个或多个统计项，以逗号分隔，如果不填，则查询所有统计项
    :param transfer: 可以查询单个或多个统计项的流量情况，以逗号分隔。可填参数：Object、Referer、IP、UA，返回TOP200数据
    :param request: 可以查询单个或多个统计项的请求次数情况，以逗号分隔。可填参数：Object、Referer、IP、UA，返回TOP200数据
    """
    return get_buckets_data(access_key_id, access_key_secret, start_time=start_time, end_time=end_time,
                            action='QueryKs3Data', date_type=date_type, bucket_names=bucket_names, products=ks3_product,
                            transfer=transfer, request=request, inner_api=inner_api)

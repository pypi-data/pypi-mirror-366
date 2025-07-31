# -*- coding: utf-8 -*-
import os
from ks3.connection import Connection

ak = os.getenv('KS3_IAM_ACCESS_KEY_ID', '<YOUR_ACCESS_KEY>')
sk = os.getenv('KS3_IAM_ACCESS_KEY_SECRET', '<YOUR_SECRET_KEY>')
bucket_name = os.getenv('KS3_BUCKET', '<KS3_TEST_BUCKET>')


def postProcessAndCheck(region=None, key=None):
    endpoint = 'ks3-cn-' + region + '.ksyuncs.com'
    conn = Connection(ak, sk, host=endpoint)
    bucket = conn.get_bucket("a-" + region + "-bucket")
    newKey = bucket.new_key(key)



postProcessAndCheck(region='qingyang-pre', key='static.png')


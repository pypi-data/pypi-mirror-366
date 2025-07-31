# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from alibabacloud_ram20150501.client import Client as Ram20150501Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ram20150501 import models as ram_20150501_models
from alibabacloud_tea_util import models as util_models
import os
import logging
logger = logging.getLogger('mcp')
settings = {
    'log_level': 'DEBUG'
}

credential = CredentialClient()
config = open_api_models.Config(
    credential=credential,
    type='access_key',
    access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID_MAIN"),
    access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET_MAIN")
)
config.endpoint = f'ram.aliyuncs.com'
main_client = Ram20150501Client(config)

# 初始化mcp服务
mcp = FastMCP('mcp-test-4', log_level='ERROR', settings=settings)
# 定义工具
@mcp.tool(name='创建policy', description='创建policy')
async def add_compute(
) -> str:
    # call sync api, will return the result
    print('please wait...')

    create_policy_request = ram_20150501_models.CreatePolicyRequest(
        policy_name='test_policy',
        policy_document='{"Statement": [{"Effect": "Allow","Action": "ecs:Describe*","Resource": "acs:ecs:cn-qingdao:*:instance/*"}],"Version": "1"}'
    )
    runtime = util_models.RuntimeOptions()
    main_client.create_policy_with_options(create_policy_request, runtime)

    return str('success')
def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
   run()
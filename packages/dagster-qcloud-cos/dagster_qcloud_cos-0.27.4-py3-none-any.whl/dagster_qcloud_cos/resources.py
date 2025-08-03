import os
from typing import Optional
from pydantic import Field
from dagster import ConfigurableResource, InitResourceContext

from qcloud_cos import CosConfig, CosS3Client


class ExtendedCosS3Client(CosS3Client):
    def __init__(self, _conf, _bucket_id):
        super().__init__(_conf)
        self.BucketId = _bucket_id


class QcloudCosResource(ConfigurableResource):
    """
## 腾讯云对象存储

此资源会实例化并返回一个 CosS3Client 类。

```python
from dagster_qcloud_cos import CosResource
```

### 配置项:

- **Scheme** (str):
    指定使用 http/https 协议来访问 COS，默认为 https，可不填
- **SecretId** (str):
    用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
- **SecretKey** (str):
    用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
- **Token** (str, optional):
    如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
- **Region** (str):
    替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket。COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
- **Endpoint** (str):
    替换为用户的 endpoint 或者 cos 全局加速域名，如果使用桶的全球加速域名，需要先开启桶的全球加速功能，请参见 https://cloud.tencent.com/document/product/436/38864
- **Domain** (str):
    用户自定义域名，需要先开启桶的自定义域名，具体请参见 https://cloud.tencent.com/document/product/436/36638
- **BucketId** (str):
    用户存储桶 BucketId，默认为 None，如果不传入，也可以在操作文件时再传入。
    """

    Scheme: str = Field(default='https', description='指定使用 http/https 协议来访问 COS')
    SecretId: str = Field(default=os.environ.get("COS_SECRET_ID"), description="用户的 SecretId")
    SecretKey: str = Field(default=os.environ.get("COS_SECRET_KEY"), description="用户的 SecretKey")
    Token: Optional[str] = Field(default=os.environ.get("COS_TOKEN"), description='如果使用临时密钥需要填入 Token。')

    Region: Optional[str] = Field(default=os.environ.get("COS_REGION"), description='用户存储桶归属 Region')
    Endpoint: Optional[str] = Field(default=os.environ.get("COS_ENDPOINT"), description='可设置为用户的 Endpoint 或者全局加速域名')
    Domain: Optional[str] = Field(default=os.environ.get("COS_DOMAIN"), description='用户自定义 CDN 域名')
    BucketId: Optional[str] = Field(default=os.environ.get("COS_BUCKET_ID"), description='用户存储桶 BucketId')

    @classmethod
    def _is_dagster_maintained(cls) -> bool:
        return False

    def create_resource(self, context: InitResourceContext) -> ExtendedCosS3Client:
        """
        返回一个 `CosS3Client` 实例。
        :param context:
        :return:
        """
        config_dict = {
            "SecretId": self.SecretId,
            "SecretKey": self.SecretKey,
            "Scheme": self.Scheme,
            "Region": self.Region,
        }
        if self.Token:
            config_dict["Token"] = self.Token
        if self.Endpoint:
            config_dict["Endpoint"] = self.Endpoint
        if self.Domain:
            config_dict["Domain"] = self.Domain
        return ExtendedCosS3Client(CosConfig(**config_dict), self.BucketId)

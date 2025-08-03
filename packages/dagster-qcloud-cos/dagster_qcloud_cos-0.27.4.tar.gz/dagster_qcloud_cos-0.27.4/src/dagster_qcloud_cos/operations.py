from dagster import In, OpExecutionContext, op, Out, OpDefinition

from dagster_qcloud_cos.resources import ExtendedCosS3Client



class InitCosOperations:
    def __init__(self, resource_key: str):
        self.resource_key = resource_key
        self.op_upload_file = self.op_upload_file()
        """
        上传文件并获取预签名的下载链接
        
        IN:
        
        - key: str, 上传文件KEY
        - file: bytes, 文件字节数据
        - expired: int, 预签名下载链接的过期时间，0 为不获取，默认为 0
        - bucket: str, bucket_id，默认为资源的 bucket_id
        
        OUT:
        
        - etag: str, ETag
        - pre_signed_url: str, 预签名的下载链接
        """

    def op_upload_file(self) -> OpDefinition:
        @op(description="上传照片到COS",
            required_resource_keys={self.resource_key},
            ins={
                "key": In(str, description="上传文件KEY"),
                "file": In(bytes, description="文件字节数据"),
                "expired": In(int, default_value=0, description="预签名下载链接的过期时间，0 为不获取，默认为 0"),
                "bucket": In(str, default_value='', description="bucket_id，默认为资源设置的bucket_id")},
            out={
                "etag": Out(str, description='ETag'),
                "pre_signed_url": Out(str, description='预签名的下载链接')
            })
        def __op_upload_file(context: OpExecutionContext, key, file: bytes, expired: int, bucket: str):

            qcloud_cos: ExtendedCosS3Client = context.resources.qcloud_cos
            response = qcloud_cos.put_object(Bucket=qcloud_cos.BucketId, Body=file, Key=key)
            bucket = bucket if bucket else qcloud_cos.BucketId

            if expired:
                filename = key.split('/')[-1]
                url = qcloud_cos.get_presigned_url(
                    Bucket=bucket,
                    Key=key,
                    Method='GET',
                    Expired=expired,
                    Headers={'response-content-disposition': f'attachment; filename={filename}'}
                )
            else:
                url = ''
            return response['ETag'], url
        return __op_upload_file


cos_op = InitCosOperations('qcloud_cos')
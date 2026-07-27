class StorageSDK:
    @staticmethod
    def upload(key, data, content_type=None):
        from apps.storage.services import StorageService
        return StorageService.upload_file(key, data, content_type)

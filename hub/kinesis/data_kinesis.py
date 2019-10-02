class DataKinesis:
    def __init__(self, uuid: str, task: str, headers: dict, body: dict):
        self.uuid = uuid
        self.task = task
        self.headers = headers
        self.body = body

    def to_dict(self) -> dict:
        return dict(
            uuid=self.uuid,
            task=self.task,
            headers=self.headers,
            body=self.body,
        )

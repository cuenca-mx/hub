from hub.db.dynamo import write_to_db
from hub.kinesis.data_kinesis import DataKinesis


def hub_task(stream: str):
    def decorator(function):
        def proccess_record(record):
            unique_trans = write_to_db(record.get("uuid"))
            if unique_trans:
                r_body = function(record['body'])
                res = DataKinesis(
                    uuid=record.get("uuid"),
                    task=record.get("task"),
                    body=r_body,
                    headers=dict(),
                )
                return res.to_dict()

        setattr(proccess_record, "hub_task", stream)
        return proccess_record

    return decorator

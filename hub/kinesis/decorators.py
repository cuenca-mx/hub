def hub_task(stream: str):
    def decorator(function):
        def proccess_record(record):
            return function(record)

        setattr(proccess_record, "hub_task", stream)
        return proccess_record

    return decorator

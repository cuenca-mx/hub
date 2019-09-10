
def kinesis():
    def decorator(function):
        function()
    return decorator

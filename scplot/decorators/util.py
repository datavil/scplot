from lets_plot import ggtb

def interactive(func):
    def wrapper(*args, **kwargs):

        inter = kwargs.get("interactive")
        if inter is True:
            return func(*args, **kwargs) + ggtb()
        elif inter is False:
            return func(*args, **kwargs)
        else:
            msg = f"expected True or False for  'interactive' argument, but received {inter}"
            raise ValueError(msg)
        
    return wrapper



from .util.recursors import recursor

def change_value(data="",key="",value="",flags={
        "se":False,
        "cs":True,
        "findOne":False,
        "chain":False
    }): 
    """
    Change the value of a key in the given data using specified flags.

    Parameters
    ----------
    data : data structure, 
        The input data structure to be searched or modified. Defaults to an empty string.
    key : str, 
        The key whose value is to be changed. Defaults to an empty string.
    value : any, 
        The new value to assign to the given key. Defaults to an empty string.
    flags : dict, optional
        A dictionary of control flags:
            - 'cs' (bool): Case sensitive key matching. Default is True.
            - 'findOne' (bool): Stop after finding the first match. Default is False.
    Returns
    -------
    dict
        A dictionary containing:
            - 'verdict' (bool): True if change was successful, otherwise False.
            - 'data' (any or None): Modified data if successful, otherwise None.
    """  
    flags["mode"]="valueChange"
    res=recursor(flags,True, [], data, key, value)
    if len(res)!=0:
        return {"verdict":True, "data":res}
    else:
        return {"verdict":False, "data":None}

# def reformat_data():
#     pass

from .util.recursors import recursor
import copy
tracker=[]  #used by evaluator 


def check_field(data="",fieldName="",flags={
        "se":False,
        "cs":True,
        "findOne":False,
        "chain":False
    }): #DONE and TESTED
    """
    Check whether a specified field exists in the given data using control flags.

    Parameters
    ----------
    data : data structure, 
        The input data structure to be searched. Defaults to an empty string.
    fieldName : str, 
        The name of the field to check for existence. Defaults to an empty string.
    flags : dict, optional
        A dictionary of control flags:
            - 'cs' (bool): Case-sensitive search. Default is True.
            - 'findOne' (bool): Return after first match. Default is False.
            - 'chain' (bool): Enable chained operations. Default is False.

    Returns
    -------
    dict
        A dictionary containing:
            - 'verdict' (bool): True if field was found, otherwise False.
            - 'data' (any or None): Matched field data if found, otherwise None.
    """
    flags["mode"]="fieldCheck"
    flags["Found"]=False
    res=recursor(flags,True, [], data, fieldName)
    if len(res)!=0:
        return {"verdict":True, "data":res}
    else:
        return {"verdict":False, "data":None}

def check_value(data="", operator="", value="",flags={
        "se":False,
        "cs":True,
        "findOne":False,
        "chain":False
    },):  #DONE and TESTED
    """
    Check whether a value in the data satisfies a given condition using an operator.

    Parameters
    ----------
    data : data structure, 
        The input data structure to evaluate. Defaults to an empty string.
    operator : str, 
        The comparison operator to apply (e.g., 'eq', 'match', 'gt', 'lt', 'gte', 'lte'). Defaults to an empty string.
    value : str, 
        The value to compare against. Defaults to an empty string.
    flags : dict, optional
        A dictionary of control flags:
            - 'cs' (bool): Case-sensitive comparisons. Default is True.
            - 'findOne' (bool): Return after first match. Default is False.

    Returns
    -------
    dict
        A dictionary containing:
            - 'verdict' (bool): True if a matching value was found, otherwise False.
            - 'data' (any or None): Matching data if found, otherwise None.
    """

    flags["mode"]="valueCheck"
    flags["Found"]=False
    res=recursor(flags,True, [], data, value, operator)
    if len(res)!=0:
        return {"verdict":True, "data":res}
    else:
        return {"verdict":False, "data":None}

def check_key_value(data="", keyword="", op="", value="",flags={
        "se":False,
        "cs":True,
        "findOne":False,
        "chain":False
    },): #DONE and TESTED
    """
    Check whether a keyword-value pair exists within the data structure using recursive search.

    Parameters
    ----------
    data : data structure, 
        The input data structure to evaluate (typically a dictionary or list). Defaults to an empty string.
    keyword : str or dict,
        The key to search for in the data. Can be a string (for key search) or a dict (for key-value matching). Defaults to an empty string.
    op : str,
        Operation for value -  eq, match, gt, lt, gte, lte.
    value : str, 
        The value to be matched against the specified key. Defaults to an empty string. can be bypassed when object mode is used
    flags : dict, optional
        A dictionary of control flags:
            - 'cs' (bool): Case-sensitive comparisons. Default is True.
            - 'findOne' (bool): Return after the first match is found. Default is False.
            - 'chain' (bool): Enables chained key resolution or advanced lookup. Default is False.

    Returns
    -------
    dict
        A dictionary containing:
            - 'verdict' (bool): True if a matching key-value pair was found, otherwise False.
            - 'data' (list or None): A list of matched results if found, otherwise None.
    """
    if type(keyword)==dict:
        if type(value)==dict:
            flags=copy.deepcopy(value)
        flags["mode"]="keyValueCheck"
        flags["Found"]=False
        value=list(keyword.values())[0]
        # print(flags, True, [], data, keyword, {"Op":op,"value":value}, "obj")
        res=recursor(flags, True, [], data, keyword, {"Op":op,"value":value}, "obj")
    else:
        flags["mode"]="keyValueCheck"
        flags["Found"]=False
        res=recursor(flags, True, [], data, keyword, {"Op":op,"value":value})
    if len(res)!=0:
        return {"verdict":True, "data":res}
    else:
        return {"verdict":False, "data":None}

def check_multi_value(data="", condition="",flags={
        "se":False,
        "cs":True,
        "findOne":False,
        "chain":False
    },): #DONE and TESTED
    """
    Check whether the data contains values that satisfy a complex multi-value condition.

    Parameters
    ----------
    data : data structure, 
        The input data structure to evaluate (e.g., list, dict, or nested structures). Defaults to an empty string.
    condition : dict, 
        A compound condition string that defines the value criteria to be matched. The syntax depends on your internal `recursor` logic. Defaults to an empty string.
    flags : dict, optional
        A dictionary of control flags:
            - 'cs' (bool): Case-sensitive comparisons. Default is True.
            - 'findOne' (bool): Return after the first match is found. Default is False.

    Returns
    -------
    dict
        A dictionary containing:
            - 'verdict' (bool): True if any values satisfy the condition, otherwise False.
            - 'data' (list or None): A list of matched results if found, otherwise None.
    """
    flags["mode"]="multiValueCheck"
    res=recursor(flags,True, [], data, condition)
    if len(res)!=0:
        return {"verdict":True, "data":res}
    else:
        return {"verdict":False, "data":None}

def check_SE_multi_key_value(data="",condition="",flags={
        "se":True,
        "cs":True,
        "findOne":False,
        "chain":False
    },):
    """
    Check structured data for matches to multiple key-value conditions on SE (Single Entity/Dict/object) within the data structure.

    Parameters
    ----------
    data : data structure, 
        The input data structure to be evaluated. Defaults to an empty string.
    condition : dict, 
        A string representing the condition(s) to evaluate against the data. Defaults to an empty string.
    flags : dict, optional
        A dictionary of control flags:
            - 'se' (bool): Use Single entity logic. Default is True.(MUST BE TRUE)
            - 'cs' (bool): Perform case-sensitive matching. Default is True.
            - 'findOne' (bool): Return after the first matching result. Default is False.

    Returns
    -------
    dict
        A dictionary containing:
            - 'verdict' (bool): True if matching key-value pair(s) found, otherwise False.
            - 'data' (list or None): The matched data as a list if found, otherwise None.
    """
    flags["mode"]="multicheck_key_value"
    res=recursor(flags,True, [], data, condition)
    if len(res)!=0:
        return {"verdict":True, "data":res}
    else:
        return {"verdict":False, "data":None}

def match_object(data="",matcher="",flags={
        "se":False,
        "cs":True,
        "findOne":False,
        "chain":False
}):
    """
    Match objects within structured data based on a given matcher object.

    Parameters
    ----------
    data : data structure, 
        The input data structure to be evaluated. Defaults to an empty string.
    matcher : dict, 
        A string representing the pattern or object structure to match against the data. Defaults to an empty string.
    flags : dict, optional
        A dictionary of control flags:
            - 'cs' (bool): Perform case-sensitive matching. Default is True.
            - 'findOne' (bool): Return after the first match. Default is False.

    Returns
    -------
    dict
        A dictionary containing:
            - 'verdict' (bool): True if a matching object was found, otherwise False.
            - 'data' (list or None): A list of matched objects if found, otherwise None.
    """
    flags["mode"]="matchObject"
    flags["Found"]=False
    res=recursor(flags,True, [], data, matcher)
    if len(res)!=0:
        return {"verdict":True, "data":res}
    else:
        return {"verdict":False, "data":None}   

def evaluate_object(data="",condition="",initial=True):
    """
    Evaluate an Object/Dict using a condition (dict that contains and/or operators).

    Parameters
    ----------
    data : data structure, 
        The input data structure (typically a dictionary or object) to evaluate. Defaults to an empty string.
    condition : dict, 
        A nested condition dictionary containing:
            - 'Op' (str): Logical operator ('and', 'or', 'eq').
            - 'field' (str): Field to check
            - 'Value' (any): List of sub-conditions or field-based conditions.
              Sub-conditions may themselves be nested using 'Op' and 'Value'.
    initial : bool, optional
        Indicates whether this is the top-level call in a recursive evaluation. 
        Used to manage internal tracking state. Defaults to True. DO NOT ALTER

    Returns
    -------
    bool
        True if the condition is satisfied based on the logical structure, otherwise False.
    """
    global tracker
    if initial:
        tracker=[]
    else:
        newTracker=[]
    if condition.get("Op")=="and" or condition.get("Op")=="or":
        for item in condition.get("Value"):
            if item.get("Op")=="and" or item.get("Op")=="or":
                res=evaluate_object(data,item,False)
                if initial:
                    tracker.append(res)
                else:
                    newTracker.append(verdict)
            else:
                flags={
                    "chain":False,
                    "se":False,
                    "cs":True,
                    "findOne":False
                }
                res=check_key_value(data,item.get("field"),item.get("Op"),item.get("Value"),flags)
                verdict=res.get("verdict")
                if initial:
                    tracker.append(verdict)
                else:
                    newTracker.append(verdict)
        if initial:
            if condition.get("Op")=="and":
                if len(tracker)==len(condition.get("Value")) and False not in tracker:
                    return True
                else:
                    return False
            elif condition.get("Op")=="or":
                if len(tracker)==len(condition.get("Value")) and True in tracker:
                    return True
                else:
                    return False
        else:
            if condition.get("Op")=="and":
                if len(newTracker)==len(condition.get("Value")) and False not in newTracker:
                    return True
                else:
                    return False
            elif condition.get("Op")=="or":
                if len(newTracker)==len(condition.get("Value")) and True in newTracker:
                    return True
                else:
                    return False

   


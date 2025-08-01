import re
import copy


def handle_operation(data, op, value, flags={
        "cs":True,
    }):
    if op=="eq":
        if flags.get("cs"):
            return data==value
        else:
            if type(data)==str:
                data=data.lower()
            if type(value)==str:
                value=value.lower()
            return data==value
    elif op=="match":
        if type(data)==str and type(value)==str:
            matcher = fr".*{re.escape(value)}.*"
            if re.fullmatch(matcher, data):
                return True
            else:
                return False
        elif type(data)==dict and type(value)==dict:
            collector=[]
            for k,v in value.items():
                if k in data.keys():
                    if flags.get("cs"):
                        comp= v==data.get(k)
                    else:
                        if type(v)==str:
                            v=v.lower()
                        if type(data.get(k))==str:
                            dv=data.get(k).lower()
                        comp=v==dv
                    if comp:
                        collector.append(True)
                    else:
                        collector.append(False)
                else:
                    collector.append(False)
            if len(collector)==len(list(value.keys())) and False not in collector:
                return True
            else:
                return False
        
        else:
            return False
    elif op=="gt":
        if isinstance(data, (int, float)) and isinstance(data, (int, float)):
            return data>value
        else:
            return False
    elif op=="lt":
        if isinstance(data, (int, float)) and isinstance(data, (int, float)):
            return data<value
        else:
            return False
    elif op=="gte":
        if isinstance(data, (int, float)) and isinstance(data, (int, float)):
            return data>=value
        else:
            return False
    elif op=="lte":
        if isinstance(data, (int, float)) and isinstance(data, (int, float)):
            return data<=value
        else:
            return False

def handle_condition(data, condition, mode="value", flags={}): # wrong implementation, field and value need to be checked at the same time
    verdict=[]
    if mode=="object":
        if condition.get("Op")=="and" or condition.get("Op")=="or":
            collector=[]
            for item in condition.get("Value"):
                subcollector=[]
                if item.get("Op")!="and" and item.get("Op")!="or":
                    for k,v in data.items():
                        res=handle_condition({k:v},item,"key:value",flags)
                        subcollector.append(res)
                    if True in subcollector:
                        collector.append(True)
                    else:
                        collector.append(False)
                else:
                    res=handle_condition(data,item,"object",flags)
                    collector.append(res.get("conditionCheck"))
                
            if condition.get("Op")=="and":
                if False in collector:
                    return {"conditionCheck":False,"data":None}
                else:
                    return {"conditionCheck":True,"data":data}

            elif condition.get("Op")=="or":
                if True in collector:
                    return {"conditionCheck":True,"data":data}
                else:
                    return {"conditionCheck":False,"data":None}
        else:
            verdict=handle_operation(data,condition.get("Op"),condition.get("Value"),flags)
            return verdict
    elif mode=="key:value":
        if flags.get("cs"):
            verdict=handle_operation(data,condition.get("Op"),{condition.get("field"):condition.get("Value")},flags)
        else:
            dataKey=list(data.keys())[0]
            dataValue=list(data.values())[0]
            conKey=copy.deepcopy(condition.get("field"))
            conValue=copy.deepcopy(condition.get("Value"))
            if type(dataKey)==str:
                dataKey=dataKey.lower()
            if type(dataValue)==str:
                dataValue=dataValue.lower()
            if type(conKey)==str:
                conKey=conKey.lower()
            if type(conValue)==str:
                conValue=conValue.lower()
            verdict=handle_operation({dataKey:dataValue},condition.get("Op"),{conKey:conValue},flags)
        return verdict
    elif mode=="value" or mode=="field":
        verdict=[]
        if condition.get("Op")=="and" or condition.get("Op")=="or":
            resCollection=[]
            for item in condition.get("Value"):
                res=handle_condition(data,item,mode,flags)
                resCollection.append(res)
            if condition.get("Op")=="and":
                if False in resCollection:
                    return False
                else:
                    return True
            elif condition.get("Op")=="or":
                if True in resCollection:
                    return True
                else:
                    return False
        else:
            if mode=="value":
                verdict=handle_operation(data,condition.get("Op"),condition.get("Value"),flags)
                return verdict
            elif mode=="field":
                verdict=handle_operation(data,condition.get("Op"),condition.get("field"),flags)
                return verdict

    else:
        print("condition mode ELSE trigered !!!!!!!!!!!!!!!!!!!!!!!!!!")

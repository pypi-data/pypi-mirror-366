import copy
from .evaluators import handle_operation,handle_condition

def recursor(flags,initial=True,result=[],data="", keyword="", op="eq", tip="", temp={}):
    mode=flags.get("mode")
    if initial:
        result=[]
        temp={
            "path":None,
            "value":None,
            "parent":"main",
            "prevParent":[],
        }

    if mode=="fieldCheck": # viable flags:- chains,caseSens,findone (TESTED)
        dataType=type(data)
        if dataType==dict:
            for item in list(data.keys()):
                if flags.get("found") and flags.get("findOne"):
                    break
                if temp.get("path")!= None:
                    cleanPath=copy.deepcopy(temp.get("path")).split(".")
                    cleanPath = [path for path in cleanPath if not path.startswith("[")]

                    cleanPath=".".join(cleanPath)
                else:
                    cleanPath=""
                if flags.get("chain"):
                    compareString=cleanPath+"."+item
                else:
                    compareString=item
                if flags.get("cs"):
                    checker=compareString==keyword
                else:
                    checker=compareString.lower()==keyword.lower()
                if checker:
                    newData=copy.deepcopy(temp)
                    newData["value"]=data.get(item)
                    newData.pop("prevParent")
                    if temp.get("path")==None:
                        newData["path"]=copy.deepcopy(item)
                        temp["path"]=copy.deepcopy(item)
                    else:
                        newData["path"]=copy.deepcopy(temp.get("path")+"."+item)
                        temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                    result.append(newData)
                    flags["found"]=True
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                        temp["parent"]=copy.deepcopy({item:data.get(item)})
                    recursor(flags,False,result, data.get(item), keyword, op, tip, temp)
                else:
                    if temp.get("path")==None:
                        temp["path"]=copy.deepcopy(item)
                    else:
                        temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                        temp["parent"]=copy.deepcopy({item:data.get(item)})
                    recursor(flags,False,result, data.get(item), keyword, op, tip, temp)
                if temp.get("prevParent")!=[]:
                    temp["parent"]=temp.get("prevParent").pop()
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    temp["path"]=None
                else:
                    temp["path"]=newPath
            return result               
        elif dataType==list:
            for i in range(len(data)):
                if flags.get("found") and flags.get("findOne"):
                    break    
                if temp.get("path")!=None:           
                    temp["path"]=temp.get("path")+"."+f"[{i}]"
                else:
                    temp["path"]=f"[{i}]"
                recursor(flags,False,result, data[i], keyword, op, tip, temp)
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust) 
                if newPath=="":
                    newPath=None
                temp["path"]=newPath
            return result
        else:
            # print("else triggered", result)
            if initial:
                print("The data is not a dictionary or a list",data)
            return result
    
    elif mode=="valueCheck": # viable flags:- caseSens,findOne (TESTED)
        dataType=type(data)
        # if flags.get("tab")!=None:
        #     flags["tab"]=flags.get("tab")+1
        # else:
        #     flags["tab"]=1
        # tab=flags.get("tab")
        # print(":-:-:-:",temp.get("path"))
        if dataType==dict:
            copmareData=copy.deepcopy(data)
            verdict=handle_operation(copmareData,op,keyword)
            if verdict:
                newData=copy.deepcopy(temp)
                newData["value"]=data
                if newData.get("prevParent")==None:
                    newData["parent"]="main"
                elif len(newData.get("prevParent"))>=2:
                    newData["parent"]=copy.deepcopy(newData.get("prevParent"))[-1]
                else:
                    newData["parent"]="main"
                if newData.get("path")==None:
                    newData["path"]="main"
                newData.pop("prevParent")
                result.append(newData)
                flags["found"]=True
            
            for item in list(data.keys()):
                if flags.get("found") and flags.get("findOne"):
                    break
                if flags.get("cs"):
                    copmareData=copy.deepcopy(data.get(item))
                else:
                    if type(data.get(item))==str:
                        copmareData=copy.deepcopy(data.get(item).lower())
                    else:
                        copmareData=copy.deepcopy(data.get(item))
                    keyword=copy.deepcopy(keyword.lower())

                verdict=handle_operation(copmareData,op,keyword)
                if verdict:
                    newData=copy.deepcopy(temp)
                    newData["value"]=data.get(item)
                    newData.pop("prevParent")
                    if temp.get("path")==None:
                        newData["path"]=copy.deepcopy(item)
                        temp["path"]=copy.deepcopy(item)
                    else:
                        newData["path"]=copy.deepcopy(temp.get("path")+"."+item)
                        temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                    # print("\t"*tab,"+++++++++++++",item,temp.get("path"))

                    result.append(newData)
                    flags["found"]=True
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                        temp["parent"]=copy.deepcopy({item:data.get(item)})
            
                    recursor(flags,False,result, data.get(item), keyword, op, item,temp)
                else:
                    if temp.get("path")==None:
                        temp["path"]=copy.deepcopy(item)
                    else:
                        temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                    # print("\t"*tab,"+++++++++++++",item,temp.get("path"))
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                        temp["parent"]=copy.deepcopy({item:data.get(item)})

                    recursor(flags,False,result, data.get(item), keyword, op, item,temp)
                        
                if temp.get("prevParent")!=[] and (type(data.get(item))==dict or type(data.get(item))==list):
                    temp["parent"]=temp.get("prevParent").pop()
                PathReadjust=temp.get("path").split(".")
                # print("\t"*tab,"-----------",PathReadjust[-1],temp.get("path"))
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    temp["path"]=None
                else:
                    temp["path"]=newPath
            # flags["tab"]=flags.get("tab")-1
            return result               
        
        elif dataType==list:
            # print("----------------setting parent list",data)
            if initial:
                copmareData=copy.deepcopy(data)
                verdict=handle_operation(copmareData,op,keyword,flags)
                if verdict:
                    newData=copy.deepcopy(temp)
                    newData["value"]=data
                    if newData.get("prevParent")==None:
                        newData["parent"]="main"
                    elif len(newData.get("prevParent"))>=2:
                        newData["parent"]=copy.deepcopy(newData.get("prevParent"))[-1]
                    else:
                        newData["parent"]="main"
                    if newData.get("path")==None:
                        newData["path"]="main"
                    newData.pop("prevParent")
                    result.append(newData)
                    flags["found"]=True
            
            temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
            temp["parent"]=copy.deepcopy(data)
            # compare list it self
            for i in range(len(data)):
                if flags.get("found") and flags.get("findOne"):
                    break
                if temp.get("path")!=None:
                    temp["path"]=temp.get("path")+"."+f"[{i}]"
                else:
                    temp["path"]=f"[{i}]"
                # print("\t"*tab,"for+++++++++++++",f"[{i}]",temp.get("path"))
                LooPdataType=type(data[i])
                if LooPdataType==list or LooPdataType==dict:
                    # compare data needs to be done here for sub array and object handling
                    temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                    temp["parent"]=copy.deepcopy(data[i])

                    recursor(flags,False,result, data[i], keyword, op, tip,temp)

                    if temp.get("prevParent")!=[]:

                        temp["parent"]=temp.get("prevParent").pop()
                else:
                    verdict=handle_operation(data[i],op,keyword,flags)

                    if verdict:
                        if tip=="":
                            tip="main"
                        newData=copy.deepcopy(temp)
                        newData["value"]=data[i]
                        newData.pop("prevParent")
                        result.append(newData)
                if temp.get("path")!=None:
                    PathReadjust=temp.get("path").split(".")
                    # print("\t"*tab,"-----------",PathReadjust[-1],temp.get("path"))
                    del PathReadjust[-1]
                    newPath=".".join(PathReadjust)
                    if newPath=="":
                        newPath=None
                    temp["path"]=newPath
            if temp.get("prevParent")!=[]:
                temp["parent"]=temp.get("prevParent").pop()
            # flags["tab"]=flags.get("tab")-1
            return result
        else:
            if initial:
                verdict=handle_operation(data,op,keyword,flags)
                result.append({"main-listElement":keyword})
            # flags["tab"]=flags.get("tab")-1
            return result
    
    elif mode=="keyValueCheck": # viable flags:- chains,caseSens,findone (TESTED)
        dataType=type(data)
        if dataType==dict:
            if tip=="obj":
                listOfKeys=list(data.keys())
                if flags.get("cs"):
                    if flags.get("chain"):
                        pathExtraction=list(keyword.keys())[0].split(".")
                        newKeyward=pathExtraction[-1]
                    else:
                        newKeyward=list(keyword.keys())[0]
                    # operation handler version
                    check=handle_operation(data.get(newKeyward),op.get("Op"),keyword.get(list(keyword.keys())[0]))
                    # con=newKeyward in listOfKeys and data.get(newKeyward)==keyword.get(list(keyword.keys())[0]) # use OP handler
                    con=newKeyward in listOfKeys and check

                else:
                    if flags.get("chain"):
                        pathExtraction=list(keyword.keys())[0].split(".")
                        newKeyward=pathExtraction[-1]
                    else:
                        newKeyward=list(keyword.keys())[0]
                    if type(data.get(newKeyward))==str:
                        data_value=data.get(newKeyward).lower()
                    else:
                        data_value=data.get(newKeyward)
                    if type(keyword.get(list(keyword.keys())[0]))==str:
                        keyword_value=keyword.get(list(keyword.keys())[0]).lower()
                    else:
                        keyword_value=keyword.get(list(keyword.keys())[0])
                    check=handle_operation(data_value,op.get("Op"),keyword_value)
                    # con=newKeyward in listOfKeys and data.get(newKeyward).lower()==keyword.get(list(keyword.keys())[0]).lower() # use OP handler
                    con=newKeyward in listOfKeys and check
                if flags.get("chain"):
                    if temp.get("path")!=None:
                        pathExtraction=copy.deepcopy(temp.get("path").split("."))
                        pathExtraction = [path for path in pathExtraction if not path.startswith("[")]
                        
                    else:
                        pathExtraction=[]
                    pathCon=list(keyword.keys())[0]==".".join(pathExtraction)+"."+newKeyward
                    # print("======",pathCon)
                else:
                    pathCon=True
                if con and pathCon:
                    item=newKeyward
                    newData=copy.deepcopy(temp)
                    newData["value"]=data.get(item)
                    if temp.get("path")==None:
                        newData["path"]=copy.deepcopy(item)
                    else:
                        newData["path"]=copy.deepcopy(temp.get("path")+"."+newKeyward)
                    newData.pop("prevParent")
                    result.append(newData)
                    flags["found"]=True
                    for item in list(data.keys()):
                        if flags.get("found") and flags.get("findOne"):
                            break
                        if temp.get("path")==None:
                            temp["path"]=copy.deepcopy(item)
                        else:
                            temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                        if type(data.get(item))==dict or type(data.get(item))==list:
                            temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                            temp["parent"]=copy.deepcopy({item:data.get(item)})
                        recursor(flags,False,result, data.get(item), keyword, op, tip,temp) #op used
                        if temp.get("prevParent")!=[]:
                            temp["parent"]=temp.get("prevParent").pop()

                        PathReadjust=temp.get("path").split(".")
                        del PathReadjust[-1]
                        newPath=".".join(PathReadjust)
                        if newPath=="":
                            temp["path"]=None
                        else:
                            temp["path"]=newPath
                else:
                    for item in list(data.keys()):
                        if flags.get("found") and flags.get("findOne"):
                            break
                        if temp.get("path")==None:
                            temp["path"]=copy.deepcopy(item)
                        else:
                            temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                        if type(data.get(item))==dict or type(data.get(item))==list:
                            temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                            temp["parent"]=copy.deepcopy({item:data.get(item)})
                        recursor(flags,False,result, data.get(item), keyword, op, tip,temp) #op used
                        if temp.get("prevParent")!=[]:
                            temp["parent"]=temp.get("prevParent").pop()
                        PathReadjust=temp.get("path").split(".")
                        del PathReadjust[-1]
                        newPath=".".join(PathReadjust)
                        if newPath=="":
                            temp["path"]=None
                        else:
                            temp["path"]=newPath
            else:
                for item in list(data.keys()):
                        if flags.get("found") and flags.get("findOne"):
                            break
                        if flags.get("cs"):
                            if flags.get("chain"):
                                pathExtraction=keyword.split(".")
                                newKeyward=pathExtraction[-1]
                            else:
                                newKeyward=keyword
                            check=handle_operation(data.get(item),op.get("Op"),op.get("value"))
                            # con=item==newKeyward and op.get("value")==data.get(item) # use OP handler #op used
                            con=item==newKeyward and check # use OP handler #op used
                        else:
                            if flags.get("chain"):
                                pathExtraction=keyword.split(".")
                                newKeyward=pathExtraction[-1]
                            else:
                                newKeyward=keyword
                            if type(op.get("value"))==str:
                                keyword_value=op.get("value").lower()
                            else:
                                keyword_value=op.get("value")
                            if type(data.get(item))==str:
                                data_value=data.get(item).lower()
                            else:
                                data_value=data.get(item)
                            check=handle_operation(data_value,op.get("Op"),keyword_value)
                            # con=item==newKeyward and op.get("value").lower()==data.get(item).lower() # use OP handler #op used
                            con=item==newKeyward and check # use OP handler #op used
                        if flags.get("chain"):
                            if temp.get("path")!=None:
                                    pathExtraction=copy.deepcopy(temp.get("path").split("."))
                                    pathExtraction = [path for path in pathExtraction if not path.startswith("[")]
                            else:
                                pathExtraction=[]
                            pathCon=keyword==".".join(pathExtraction)+"."+newKeyward
                            print("======",pathCon)
                        else:
                            pathCon=True
                        if con and pathCon:
                            newData=copy.deepcopy(temp)
                            newData["value"]=data.get(item)
                            if temp.get("path")==None:
                                newData["path"]=copy.deepcopy(item)
                                temp["path"]=copy.deepcopy(item)
                            else:
                                newData["path"]=copy.deepcopy(temp.get("path")+"."+item)
                                temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                            newData.pop("prevParent")
                            result.append(newData)
                            flags["found"]=True
                            if type(data.get(item))==dict or type(data.get(item))==list:
                                temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                                temp["parent"]=copy.deepcopy({item:data.get(item)})
                            recursor(flags,False,result, data.get(item), keyword, op, tip, temp) #op used
                            if temp.get("prevParent")!=[]:
                                temp["parent"]=temp.get("prevParent").pop()
                        else:
                            if temp.get("path")==None:
                                temp["path"]=copy.deepcopy(item)
                            else:
                                temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                            if type(data.get(item))==dict or type(data.get(item))==list:
                                temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                                temp["parent"]=copy.deepcopy({item:data.get(item)})
                            recursor(flags,False,result, data.get(item), keyword, op, tip, temp) #op used
                            if temp.get("prevParent")!=[]:
                                temp["parent"]=temp.get("prevParent").pop()
                        PathReadjust=temp.get("path").split(".")
                        del PathReadjust[-1]
                        newPath=".".join(PathReadjust)
                        if newPath=="":
                            temp["path"]=None
                        else:
                            temp["path"]=newPath
            return result               
        elif dataType==list:
            # print("list triggered", result)
            for i in range(len(data)):
                if flags.get("found") and flags.get("findOne"):
                    break
                if temp.get("path")!=None:
                    temp["path"]=temp.get("path")+"."+f"[{i}]"
                else:
                    temp["path"]=f"[{i}]"
                temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                temp["parent"]=copy.deepcopy(data[i])
                recursor(flags,False,result, data[i], keyword, op, tip,temp)
                if temp.get("prevParent")!=[]:
                    temp["parent"]=temp.get("prevParent").pop()
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    newPath=None
                temp["path"]=newPath
            return result
        else:
            # print("else triggered", result)
            if initial:
                print("The data is not a dictionary or a list")
            return result

    elif mode=="multiValueCheck": # viable flags:- caseSens, findone (TESTED)
        dataType=type(data)        
        if dataType==dict:
            temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
            temp["parent"]=data
            for item in list(data.keys()):
                if flags.get("found") and flags.get("findOne"):
                    break
                verdict=handle_condition(data.get(item),keyword,"value",flags=flags) # path se flag, cs flag and parent path, so it will take care of the logic
                if verdict:
                    newData=copy.deepcopy(temp)
                    newData.pop("prevParent")
                    newData["value"]=data.get(item)
                    if temp.get("path")==None:
                        newData["path"]=copy.deepcopy(item)
                        temp["path"]=copy.deepcopy(item)
                    else:
                        newData["path"]=copy.deepcopy(temp.get("path")+"."+item)
                        temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                    result.append(newData)
                    flags["found"]=True
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                        temp["parent"]=copy.deepcopy({item:data.get(item)})
                    recursor(flags,False,result, data.get(item), keyword, op, {item:data.get(item)}, temp)
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        if temp.get("prevParent")!=[]:
                            temp["parent"]=copy.deepcopy(temp.get("prevParent").pop())
                        else:
                            temp["parent"]=None
                else:
                    if temp.get("path")==None:
                        temp["path"]=copy.deepcopy(item)
                    else:
                        temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                        temp["parent"]=copy.deepcopy({item:data.get(item)})
                        # print("_____________",temp.get("prevParent"),temp.get("parent"))
                    recursor(flags,False,result, data.get(item), keyword, op, {item:data.get(item)},temp)
                    if type(data.get(item))==dict or type(data.get(item))==list:
                        if temp.get("prevParent")!=[]:
                            temp["parent"]=copy.deepcopy(temp.get("prevParent").pop())
                        else:
                            temp["parent"]=None
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    temp["path"]=None
                else:
                    temp["path"]=newPath
            
            if temp.get("prevParent")!=[]:
                temp["parent"]=copy.deepcopy(temp.get("prevParent").pop())
            else:
                temp["parent"]=None
            return result               
        elif dataType==list:
            # if initial:
            #     # temp["parent"]={"main":data}
            #     temp["parent"]=data
            # else:
            #     # if type(tip)==dict:
            #     #     key=list(tip.keys())[0]         
            #     # temp["parent"]={key:data}
            #     temp["parent"]=data
            temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
            temp["parent"]=data
            for i in range(len(data)):
                if flags.get("found") and flags.get("findOne"):
                    break
                # if tip=="":
                    # temp["parent"]={f"main":data}
                LooPdataType=type(data[i])
                if LooPdataType==list or LooPdataType==dict:
                    if temp.get("path")!=None:
                        temp["path"]=temp.get("path")+"."+f"[{i}]"
                    else:
                        temp["path"]=f"[{i}]"
                    temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                    temp["parent"]=copy.deepcopy(data[i])
                    # print("_____________",temp.get("prevParent"),temp.get("parent"))
                    recursor(flags,False,result, data[i], keyword, op, tip,temp)
                    if temp.get("prevParent")!=[]:
                        temp["parent"]=copy.deepcopy(temp.get("prevParent").pop())
                    else:
                        temp["parent"]=None
                    PathReadjust=temp.get("path").split(".")
                    del PathReadjust[-1]
                    newPath=".".join(PathReadjust)
                    if newPath=="":
                        newPath=None
                    temp["path"]=newPath
                else:
                    print("elements of array",data)
                    verdict=handle_condition(data[i],keyword,flags=flags)
                    if verdict:
                            newData=copy.deepcopy(temp)
                            newData["value"]=data[i]
                            if temp.get("path")==None:
                                newData["path"]=copy.deepcopy(f"[{i}]")
                            else:
                                newData["path"]=copy.deepcopy(temp.get("path")+"."+f"[{i}]")
                            result.append(newData) 
                            flags["found"]=True
            if temp.get("prevParent")!=[]:
                temp["parent"]=copy.deepcopy(temp.get("prevParent").pop())
            else:
                temp["parent"]=None
            return result
        elif initial:
            verdict=handle_condition(data,keyword,flags=flags)
            print("handling plan data--", data, keyword,verdict)
            if verdict:
                newData=copy.deepcopy(temp)
                newData["value"]=data
                if temp.get("path")==None:
                    if type(tip)==dict:
                        newData["path"]=copy.deepcopy(list(tip.keys())[0])
                else:
                    newData["path"]=copy.deepcopy(temp.get("path"))
                result.append(newData) 
                flags["found"]=True
            return result

    elif mode=="multiKeyValueCheck": # viable flags:- caseSens, findone and singleElement (TESTED)
        """
        SE verses Chaining
            can they work togather?
            No imposible, because you either have to spacify the same chain again and again in the conditions, which is unessary
            Then which to keep?
            SE.
        SE verses logical operators and/or
            can it work with and?
            yes because you can check if a single object contains all the specified field and values
            can it work with or?
            No because if you set SE and an or, then even the or will allow it to be true if only one matchs, tese single element by its deffination
            only works with and
            can i do and/or without single element?
            yes
        data managment?
            in order to monitor and/or, the and/or list of conditions must be monitored in the condition handler
            where to monitor SE, since we are checking if all conditions are met it has to be the condition handler
            but, the condition handler needs access to all of the object at once.

            These in the recursor, if we find an objct, we must pass it to the condition handler as a whole.
            then the condition handler will check all of the proporties without going deeper.
            going deeper will be handlerd by the recursor.

        """
        dataType=type(data)
        if flags.get("se"):
            if dataType==dict:
                res=handle_condition(data,keyword,"object",flags)
                if res.get("conditionCheck"):
                    newRes=copy.deepcopy(temp)
                    newRes["value"]=res.get("data") 
                    newRes.pop("prevParent")
                    result.append(newRes)
                    flags["found"]=True
                temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
                temp["parent"]=data
                for item in data.keys():
                    if flags.get("found") and flags.get("findOne"):
                        break
                    if  temp["path"]!=None:
                        temp["path"]=temp.get("path")+"."+item
                    else:
                        temp["path"]=item
                    recursor(flags,False,result,data.get(item),keyword,op,tip,temp)
                    PathReadjust=temp.get("path").split(".")
                    del PathReadjust[-1]
                    newPath=".".join(PathReadjust)
                    if newPath=="":
                        temp["path"]=None
                    else:
                        temp["path"]=newPath
                if temp.get("prevParent")!=[]:
                    temp["parent"]=copy.deepcopy(temp.get("prevParent").pop())
                else:
                    temp["parent"]=None
                return result
            elif dataType==list:
                temp.get("prevParent").append(copy.deepcopy(temp.get("prevParent")))
                temp["parent"]=data
                for i in range(len(data)):
                    if flags.get("found") and flags.get("findOne"):
                        break
                    if  temp["path"]!=None:
                        temp["path"]=temp.get("path")+"."+f"[{i}]"
                    else:
                        temp["path"]=f"[{i}]"
                    recursor(flags,False,result,data[i],keyword,op,tip,temp)
                    PathReadjust=temp.get("path").split(".")
                    del PathReadjust[-1]
                    newPath=".".join(PathReadjust)
                    if newPath=="":
                        temp["path"]=None
                    else:
                        temp["path"]=newPath
                if temp.get("prevParent")!=[]:
                    temp["parent"]=copy.deepcopy(temp.get("prevParent").pop())
                else:
                    temp["parent"]=None
                return result
            else:
                if initial:
                    print("The data is nither a dict nor a list")
                    return result
                else:
                    return result
        else:
            raise Exception(" The following function only works with Single Element flag, please set flag 'se' True ")
    
    elif mode=="valueChange": #viable flags:- caseSense, findOne (TESTED)
        dataType=type(data)
        if initial:
            flags["isChanged"]=False
        if dataType==dict:
            for item in list(data.keys()):
                if flags.get("found") and flags.get("findOne"):
                    break
                if flags.get("cs"):
                        con=item==keyword
                else:
                        con=item.lower()==keyword.lower()
                if con:
                    data[item]=op
                    result.append({item: data.get(item)})
                    flags["isChanged"]=True
                    flags["found"]=True
                    if temp.get("path")==None:
                        temp["path"]=item
                    else:
                        temp["path"]=temp.get("path")+"."+item
                    recursor(flags,False,result, data.get(item), keyword, op,tip,temp)
                else:
                    if temp.get("path")==None:
                        temp["path"]=item
                    else:
                        temp["path"]=temp.get("path")+"."+item
                    recursor(flags,False,result, data.get(item), keyword, op,tip,temp)
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    temp["path"]=None
                else:
                    temp["path"]=newPath
            if flags.get("isChanged"):
                return [data]
            else:
                return []              
        elif dataType==list:
            for i in range(len(data)):
                if flags.get("found") and flags.get("findOne"):
                    break
                if temp.get("path")==None:
                    temp["path"]=f"[{i}]"
                else:
                    temp["path"]=temp.get("path")+"."+f"[{i}]"
                recursor(flags,False,result, data[i], keyword, op,tip,temp)
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    temp["path"]=None
                else:
                    temp["path"]=newPath
            if flags.get("isChanged"):
                return [data]
            else:
                return []   
        else:
            if initial:
                print("The data is not a dictionary or a list")
            
            if flags.get("isChanged"):
                return [data]
            else:
                return []   
  
    elif mode=="matchObject": # viable flags:- caseSense,findOne (TESTED)
        dataType=type(data)
        if dataType==dict:
            verdict=handle_operation(data,"match",keyword,flags)
            if verdict:
                newData=copy.deepcopy(temp)
                newData["value"]=data
                newData.pop("prevParent")
                result.append(newData)
                flags["found"]=True
            temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
            temp["parent"]=data
            for item in list(data.keys()):
                if flags.get("findOne") and flags.get("found"):
                    break
                if temp.get("path")==None:
                    temp["path"]=copy.deepcopy(item)
                else:
                    temp["path"]=copy.deepcopy(temp.get("path")+"."+item)
                recursor(flags,False,result,data.get(item),keyword,op,tip,temp)
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    newPath=None
                temp["path"]=newPath
            if temp.get("prevParent")!=[]:
                temp["parent"]=temp.get("prevParent").pop()
            else:
                temp["parent"]=None
            return result
        elif dataType==list:
            temp.get("prevParent").append(copy.deepcopy(temp.get("parent")))
            temp["parent"]=data
            for i in range(len(data)):
                if flags.get("findOne") and flags.get("found"):
                    break
                if temp.get("path")==None:
                    temp["path"]=f"[{i}]"
                else:
                    temp["path"]=copy.deepcopy(temp.get("path")+"."+f"[{i}]")
                recursor(flags,False,result,data[i],keyword,op,tip,temp)
                PathReadjust=temp.get("path").split(".")
                del PathReadjust[-1]
                newPath=".".join(PathReadjust)
                if newPath=="":
                    newPath=None
                temp["path"]=newPath
            if temp.get("prevParent")!=[]:
                temp["parent"]=temp.get("prevParent").pop()
            else:
                temp["parent"]=None
            return result
        else:
            return result
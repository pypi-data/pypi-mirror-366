def organize_chain(keyword):
    keyword_list=keyword.split(".")
    clean_list=[path for path in keyword_list if not path.startswith("[")]
    word=keyword_list[-1]
    return keyword_list,clean_list,word

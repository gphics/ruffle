import math


def paginate(data, limit=20, page=1):
    data_length = len(data)
    if not data_length:
        return []
    total_page_num = math.ceil(data_length / limit)
    result = []
    cur_page = page
    if cur_page > total_page_num:
        cur_page = total_page_num
    if cur_page == 1:
        res = data[:limit]
        result = res
    else:
        prev = limit * (cur_page - 1)
        cur = limit * cur_page
        res = data[prev:cur]
        result = res
    return {"result": result, "total_pages": total_page_num}

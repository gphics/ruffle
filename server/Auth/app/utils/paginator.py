import math


def paginate(data, limit=20, page=1):
    data_length = len(data)
    if not data_length:
        return {"cur_page": 0, "total_pages": 0, "result": []}
    total_page = math.ceil(data_length / limit)
    result = []
    cur_page = page
    if cur_page > total_page:
        cur_page = total_page
    if cur_page == 1:
        res = data[:limit]
        result = res
    else:
        prev = limit * (cur_page - 1)
        cur = limit * cur_page
        res = data[prev:cur]
        result = res
    return {"cur_page": cur_page, "total_pages": total_page, "result": result}

import math


def paginate(data, page=1, limit=20):
    data_length = len(data)
    if not data_length:
        return {"cur_page": 0, "total_pages": 0, "result": []}
    total_pages = math.ceil(data_length / limit)
    result = []
    cur_page = page
    if cur_page > total_pages:
        cur_page = total_pages
    if page == 1:
        result = data[:limit]
    else:
        cur = limit * cur_page
        prev = limit * (cur_page - 1)
        result = data[prev:cur]
    return {"cur_page": cur_page, "total_pages": total_pages, "result": result}

# encoding: utf-8

def filter_fields(response_dict, fields):
    if fields:
        return {
            k: v for k, v in response_dict.items() if k in fields
        }
    else:
        return response_dict

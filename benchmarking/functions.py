import json
from django.db.models import Q
from esganalyse.models import Campany
from django.core import serializers
    
def get_info_campany(campany_name,date):   
    """function to get info about campany for a given campany for benchmarking""" 
    campany_object= Campany.objects.filter(Q(campany_name=campany_name) & Q(year=date))
    campany_dict = serializers.serialize("json", campany_object)
    res = json.loads(campany_dict)
    list_infos=[]
    for i in range(0, len(res)):
        res[i].pop('model')
        campany_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = campany_id
        list_infos.append(res[i]['fields'])
    return list_infos



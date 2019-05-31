import numpy as np
import pandas as pd
import json
import re
import requests
import random
import neurolab as nl
from tqdm import tqdm
from time import sleep

def decode(input):
    if input == 1:
        output = 9
    elif input == 2:
        output = 7
    elif input == 3:
        output = 5
    elif input == 4:
        output = 3
    elif input == 5:
        output = 1
    elif input == 6:
        output = 1/3
    elif input == 7:
        output = 1/5
    elif input == 8:
        output = 1/7
    else:
        output = 1/9
    return output

def count_APSA(df, feeder):
    temp_df=df.drop(set(np.where(df['feedername']!=feeder+'VB01')[0])).copy()
    print(temp_df)
    if temp_df['total'].vals==0:
        return {'percent_complete':0}
    else:
        return {'percent_complete':1-(temp_df['complete']/temp_df['total'])}


def count_counter(df, feeder):
    temp_df=df.drop(set(np.where(df['ฟีดเดอร์']!=feeder)[0])).copy()
    return {'T/R':list(temp_df['ประเภทการทำงาน']).count('T/R'), 'T/L':list(temp_df['ประเภทการทำงาน']).count('T/L')}

def nor_input_layer(df):
    df['sum_TR']=[item/10   if item < 10 else 1 for item in df['sum_TR']]
    df['sum_TL']=[item/10   if item < 10 else 1 for item in df['sum_TL']]
    df['Peak load']=[item/10   for item in df['Peak load']]
    df['Average load']=[item/10   for item in df['Average load']]
    return df



def get_max_load_N1(area, feeder, year,month):
    if area == 1:
        url = "http://172.30.7.209/services/get_load.php"

        querystring = {"region":"11","year":year,"month":month,"substation":feeder[:3],"feeder":"out{}".format(feeder[3:]),"type":"P"}
        headers = {
            'Cache-Control': "no-cache",
#             'Postman-Token': "eecdd298-920a-4726-91ba-f3f8d48ef2a8"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response=response.json()
        if response['data'] != []:
            return float(response['max'])
        else:
            return float(0)

def get_ava_load_N1(area, feeder, year,month):
    if area == 1:
        url = "http://172.30.7.209/services/get_load.php"

        querystring = {"region":"11","year":year,"month":month,"substation":feeder[:3],"feeder":"out{}".format(feeder[3:]),"type":"P"}


        headers = {
            'Cache-Control': "no-cache",
#             'Postman-Token': "eecdd298-920a-4726-91ba-f3f8d48ef2a8"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response=response.json()

        if response['data'] != []:
            return float(response['avg'])
        else:
            return float(0)

def get_max_load_N2(area, feeder, year,month):
    if area == 2:
        url = "http://172.30.7.209/services/get_load.php"

        querystring = {"region":"12","year":"{}".format(year),"month":"{}".format(month),"substaion":"{}".format(feeder[:3]),"feeder":"OUT{}".format(feeder[3:])}


        headers = {
            'Cache-Control': "no-cache",
#             'Postman-Token': "eecdd298-920a-4726-91ba-f3f8d48ef2a8"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response=response.json()
        if response['data'] != []:
            return float(response['max'])
        else:
            return float(0)


def get_ava_load_N2(area, feeder, year,month):
    if area == 2:
        url = "http://172.30.7.209/services/get_load.php"

        querystring = {"region":"12","year":"{}".format(year),"month":"{}".format(month),"substaion":"{}".format(feeder[:3]),"feeder":"OUT{}".format(feeder[3:])}

        headers = {
            'Cache-Control': "no-cache",
#             'Postman-Token': "eecdd298-920a-4726-91ba-f3f8d48ef2a8"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response=response.json()

        if response['data'] != []:
            return float(response['avg'])
        else:
            return float(0)

def get_peak_load_N3(area, feeder, year, month):
    if area == 3:
#         print(feeder)
        url = "http://172.30.200.113/webcenter/views/peakload.php"
        querystring = {"year":"{}".format(year),"month":"{}".format(month),"region":"13", 'feedername':'{}'.format(feeder)+'VB01'}
        headers = {
        'Cache-Control': "no-cache",
        #     'Postman-Token': "15f82df5-f82f-4596-bc0b-efd65dd23b28"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

        response=response.json()
        if response['PeakLoad'] == []:
            return float(0)
        else:
            return float(response['PeakLoad'][0]['MW'])

def clean_feeder(feeder):
    correct_feeder = ['OUT01', 'OUT02','OUT03','OUT04','OUT05','OUT06','OUT07','OUT08','OUT09','OUT10', 'OUT11','OUT12']
    if feeder not in correct_feeder:
        if feeder == 'OUT010':
            return 'OUT10'
        else:
            return 'OUT0'+feeder[3:]
    else:
        return feeder

def get_max_avarage_load(df, feeder):
    temp_df=df.drop(np.where(df['feeder']!=feeder)[0]).copy()
    return abs(temp_df['WERT_MAX'].max()), abs(temp_df['WERT_EFF'].mean())

def get_TL_TR_values(df1, df2, df3, List_feeder_name):

    df1=df1.drop(set(np.where(df1['ประเภทการทำงาน']=='D/F')[0]).union(set(np.where(df1['ประเภทการทำงาน']=='Operate')[0])))
    df1=df1.reset_index()
    del df1['index']
    del df1['หมายเลขเหตุการณ์']
    del df1['ลำดับ']
    del df1['วันที่/เวลาไฟดับ']
    del df1['เวลา']
    del df1['วันที่/เวลา ที่จ่ายไฟคืนระบบได้ครั้งแรก']
    del df1['วันที่/เวลา ที่จ่ายไฟคืนครบทั้งหมด']
    del df1['รวมเวลาไฟดับ (นาที)']
    del df1['เฟส']
    del df1['สาเหตุ/รายละเอียด']
    del df1['ทราบสาเหตุ']
    del df1['กฟฟ.รับผิดชอบ']
    del df1['สภาพอากาศ']
    del df1['ผชฟ. ถูกกระทบ (ราย)']
    del df1['สถานที่จุดเกิดเหตุ']
    del df1['รายละเอียดการแก้ไข']
    del df1['ค่าโหลด (MW)']
    del df1['ประเภทเหตุการณ์']

    df2=df2.drop(set(np.where(df2['ประเภทการทำงาน']=='D/F')[0]).union(set(np.where(df2['ประเภทการทำงาน']=='Operate')[0])))
    df2=df2.reset_index()
    del df2['index']
    del df2['หมายเลขเหตุการณ์']
    del df2['ลำดับ']
    del df2['วันที่/เวลาไฟดับ']
    del df2['เวลา']
    del df2['วันที่/เวลา ที่จ่ายไฟคืนระบบได้ครั้งแรก']
    del df2['วันที่/เวลา ที่จ่ายไฟคืนครบทั้งหมด']
    del df2['รวมเวลาไฟดับ (นาที)']
    del df2['เฟส']
    del df2['สาเหตุ/รายละเอียด']
    del df2['ทราบสาเหตุ']
    del df2['กฟฟ.รับผิดชอบ']
    del df2['สภาพอากาศ']
    del df2['ผชฟ. ถูกกระทบ (ราย)']
    del df2['สถานที่จุดเกิดเหตุ']
    del df2['รายละเอียดการแก้ไข']
    del df2['ค่าโหลด (MW)']
    del df2['ประเภทเหตุการณ์']

    df3=df3.drop(set(np.where(df3['ประเภทการทำงาน']=='D/F')[0]).union(set(np.where(df3['ประเภทการทำงาน']=='Operate')[0])))
    df3=df3.reset_index()
    del df3['index']
    del df3['หมายเลขเหตุการณ์']
    del df3['ลำดับ']
    del df3['วันที่/เวลาไฟดับ']
    del df3['เวลา']
    del df3['วันที่/เวลา ที่จ่ายไฟคืนระบบได้ครั้งแรก']
    del df3['วันที่/เวลา ที่จ่ายไฟคืนครบทั้งหมด']
    del df3['รวมเวลาไฟดับ (นาที)']
    del df3['เฟส']
    del df3['สาเหตุ/รายละเอียด']
    del df3['ทราบสาเหตุ']
    del df3['กฟฟ.รับผิดชอบ']
    del df3['สภาพอากาศ']
    del df3['ผชฟ. ถูกกระทบ (ราย)']
    del df3['สถานที่จุดเกิดเหตุ']
    del df3['รายละเอียดการแก้ไข']
    del df3['ค่าโหลด (MW)']
    del df3['ประเภทเหตุการณ์']

    df4=df1.append(df2)
    print(df4)
    df4=df4.reset_index()
    del df4['index']

    df4=df4.append(df3)
    print(df4)


    df4=df4.reset_index()
    del df4['index']

    return {feeder:count_counter(df4, feeder) for feeder in List_feeder_name}

# def get_OMS_data(region, month):



class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


year = 2019
month = 4
region = 1 #N


number_Criteria=10
dict_RI={1:0, 2:0, 3:0.58, 4:0.9, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.46, 10:1.5}
data=pd.read_csv('surveys.csv')
data=data.dropna()
data=data.reset_index()
df3=pd.DataFrame()
weights_list=['w1','w2','w3','w4','w5','w6','w7','w8','w9','w10']
df3=pd.DataFrame(columns=weights_list)
list(data.index)
CR_val=[]
dict={}
for index in list(data.index):
    input_file=list(data.iloc[index,:])
    prepared_file=[]
    for x in input_file:
        prepared_file.append(decode(x))
    columns_name=['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
    #columns_name =['CB', 'RCS', 'Load Break', 'LRC', 'Recloser', 'SCB', 'SCB(FRTU)', 'FCB', 'LRR', 'AVR']
    #w1, w2, w4, w7
    df = pd.DataFrame(np.zeros([number_Criteria,number_Criteria]), columns=columns_name, index=columns_name)
    for name in columns_name:
        df[name][name]=1

        mini_list1=np.array(prepared_file[0:9].copy())  #9-0 =9
    df.iloc[0,1:10]=mini_list1
    df.iloc[1:10,0]=1/mini_list1

    mini_list2 = np.array(prepared_file[9:17].copy())   # 17-9 =8
    df.iloc[1,2:10]=mini_list2
    df.iloc[2:10,1]=1/mini_list2

    mini_list3 = np.array(prepared_file[17:24].copy())   #.  24-17 = 7
    df.iloc[2,3:10]=mini_list3
    df.iloc[3:10,2]=1/mini_list3

    mini_list4 = np.array(prepared_file[24:30].copy())   #.  30-24 = 6
    df.iloc[3,4:10]=mini_list4
    df.iloc[4:10,3]=1/mini_list4

    mini_list5 = np.array(prepared_file[30:35].copy())   #.  35-30 = 5
    df.iloc[4,5:10]=mini_list5
    df.iloc[5:10,4]=1/mini_list5

    mini_list6 = np.array(prepared_file[35:39].copy())   #.  39-35 = 4
    df.iloc[5,6:10]=mini_list6
    df.iloc[6:10,5]=1/mini_list6

    mini_list7 = np.array(prepared_file[39:42].copy())   #.  42-39 = 3
    df.iloc[6,7:10]=mini_list7
    df.iloc[7:10,6]=1/mini_list7

    mini_list8 = np.array(prepared_file[42:44].copy())   #.  44-42 = 2
    df.iloc[7,8:10]=mini_list8
    df.iloc[8:10,7]=1/mini_list8

    mini_list9 = np.array(prepared_file[44:45].copy())   #.  45-44 = 1
    df.iloc[8,9:10]=mini_list9
    df.iloc[9:10,8]=1/mini_list9

    df.loc['sum'] = df.sum()
    df2=pd.DataFrame(columns=columns_name, index=columns_name)
    for item in columns_name:
        df2.loc[item]=df.loc[item]/df.loc['sum']
    df2['total'] = df2[df2.columns].sum(axis=1)
    df2['weight'] = df2['total']/df2['total'].sum()
    df2.loc['sum'] = df2.sum()
    df3.loc[index]=np.array(list(df2['weight'][0:-1]))

    CI_list=[np.array(df.iloc[item,:].sum()*np.array(df2.iloc[0:10,11]))/df2.iloc[item,11] for item in np.arange(0,number_Criteria,1)]
    df2['CM']=np.array(CI_list+[np.mean(CI_list)])

    CI_val=(df2.iloc[10,12]-df2.iloc[10,10])/(df2.iloc[10,10]-1)
    CR_val.append(CI_val/dict_RI[number_Criteria])
    dict.update({index:{'weight':list(df2['weight']), 'CR':CI_val/dict_RI[number_Criteria]}})

df3['CR_val']=np.array(CR_val)

number_obs=56 #manual added
dict_weights={weight: np.prod(np.array(df3[weight]))**(1/number_obs) for weight in weights_list}
sum=dict_weights['w1']+dict_weights['w2']+dict_weights['w3']+dict_weights['w4']+dict_weights['w5']+dict_weights['w6']+dict_weights['w7']+dict_weights['w8']+dict_weights['w9']+dict_weights['w10']

#dict_nor_weights is output weight
dict_nor_weights={weight:dict_weights[weight]/sum for weight in weights_list}
# print(dict_nor_weights)


pattern = '[A-Z]{3}\d\d'
rex=re.compile(pattern)

json1 = json.loads(open('n1.json').read())
List_N1_feeder_name= [rex.findall(dict['attributes']['FACILITYID'][0:5]) for dict in json1['features']]
List_N1_feeder_name=[a[0] for a in List_N1_feeder_name if a]

set_A=set([x for x in List_N1_feeder_name if List_N1_feeder_name.count(x)>1])
# print(set_A)
List_N1_feeder_name=list(set(List_N1_feeder_name))
set_A=set([x for x in List_N1_feeder_name if List_N1_feeder_name.count(x)>1])
# print(set_A)

List_N1_CB=[item + 'VB01' for item in List_N1_feeder_name]

json2 = json.loads(open('n2.json').read())
List_N2_feeder_name= [rex.findall(dict['attributes']['FACILITYID'][0:5]) for dict in json2['features']]
List_N2_feeder_name=[a[0] for a in List_N2_feeder_name if a]

set_A=set([x for x in List_N2_feeder_name if List_N2_feeder_name.count(x)>1])
# print(set_A)
List_N2_feeder_name=list(set(List_N2_feeder_name))
set_A=set([x for x in List_N2_feeder_name if List_N2_feeder_name.count(x)>1])
# print(set_A)

List_N2_CB=[item + 'VB01' for item in List_N2_feeder_name]

json3 = json.loads(open('n3.json').read())
List_N3_feeder_name= [rex.findall(dict['attributes']['FACILITYID'][0:5]) for dict in json3['features']]
List_N3_feeder_name=[a[0] for a in List_N3_feeder_name if a]
set_A=set([x for x in List_N3_feeder_name if List_N3_feeder_name.count(x)>1])
# print(set_A)
List_N3_feeder_name=list(set(List_N3_feeder_name))
set_A=set([x for x in List_N3_feeder_name if List_N3_feeder_name.count(x)>1])
# print(set_A)
List_N3_CB=[item + 'VB01' for item in List_N3_feeder_name]


for area in [1,2,3]:
    print('-------------start area {}-------------'.format(area))
    list_of_equipment_code=[10,11,14,16] #SCB, CB, Recloser, Switch
    if area == 1:
        all_list_feeder_name=List_N1_feeder_name
    elif area ==2:
         all_list_feeder_name=List_N2_feeder_name
    elif area ==3:
        all_list_feeder_name=List_N3_feeder_name

    list_feeder_name=[]
    list_FRTU_name=[]
    list_type=[]

    print('-------------retrieve GIS data of area {}-------------'.format(area))
    # for equipment_code in list_of_equipment_code:
    #     # print('GIS equiment code', equipment_code)
    #     for feeder_name in tqdm(all_list_feeder_name, desc='equipment code {}'.format(equipment_code)):
    #         temp_list_feeder_name=[]
    #         temp_list_FRTU_name=[]
    #         temp_list_type=[]
    #         res1=requests.get('http://gisn{}.pea.co.th/arcgis/rest/services/PEA/MapServer/{}/query?where=1%3D1+AND+FEEDERID+%3D+%27{}%27&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&f=pjson'.format(area, equipment_code, feeder_name))
    #         res=res1.json()
    #         if len(res['features'])>0:
    #             temp_list_feeder_name=[feeder_name]*len(res['features'])
    #             temp_list_FRTU_name=[dict['attributes']['FACILITYID'] for dict in res['features']]
    #             if equipment_code == 10:
    #                 temp_list_type=['SCB']*len(res['features'])
    #             elif equipment_code == 11:
    #                 temp_list_type=['CB']*len(res['features'])
    #             elif equipment_code == 14:
    #                 temp_list_type=['Recloser']*len(res['features'])
    #             else:
    #                 temp_list_type=['Switch']*len(res['features'])
    #             list_feeder_name=list_feeder_name+temp_list_feeder_name
    #             list_FRTU_name=list_FRTU_name+temp_list_FRTU_name
    #             list_type=list_type+temp_list_type
    # df_equipment=pd.DataFrame()
    # df_equipment['feeder']=list_feeder_name
    # df_equipment['equipment']=list_FRTU_name
    # df_equipment['type']=list_type
    # df_equipment['type'].unique()
    # df_equipment.to_csv('equipment_{}.csv'.format(area), sep=',')
    # # print(df_equipment)
    #
    # dict_feeder = {item1:{item2:[df_equipment.iloc[item3, 1] for item3 in set(np.where(df_equipment['type']==item2)[0]).intersection(np.where(df_equipment['feeder']==item1)[0])] for item2 in df_equipment['type'].unique()} for item1 in all_list_feeder_name}
    #
    # json_dict = json.dumps(dict_feeder)
    # f = open("dict_area_{}.json".format(area),"w")
    # f.write(json_dict)
    # f.close()

    df_equipment=pd.read_csv('equipment_{}.csv'.format(area), sep=',')

    with open("dict_area_{}.json".format(area), "r") as read_file:
        dict_feeder = json.load(read_file)

    #retieve APSA data
    print('-------------retrieve APSA data of area {}-------------'.format(area))
    res2=requests.get("https://region1.pea.co.th/api/apsa/status/2019")
    res2=res2.json()
    list_feedername=[dict['feedername'] for dict in res2['records']]
    list_finished=[int(dict['finished']) for dict in res2['records']]
    list_operation=[int(dict['operation']) for dict in res2['records']]
    df_APSA=pd.DataFrame()
    df_APSA['feedername']=list_feedername
    df_APSA['complete']=list_finished
    df_APSA['in_progress']=list_operation
    df_APSA['total']=df_APSA['in_progress']+df_APSA['complete']

    if area == 1:
        list_feeder=List_N1_CB
    elif area ==2:
         list_feeder=List_N2_CB
    elif area ==3:
        list_feeder=List_N3_CB

    df2_APSA=pd.DataFrame()
    for feeder in tqdm(list_feeder):
        if feeder in set(df_APSA['feedername']):
            df2_APSA=df2_APSA.append(df_APSA.loc[df_APSA['feedername'].values==feeder])
        else:
            df_empty=pd.DataFrame()
            df_empty['feedername']=[feeder]
            df_empty['complete']=[0]
            df_empty['in_progress']=[0]
            df_empty['total']=[0]
            df2_APSA=df2_APSA.append(df_empty)

    df2_APSA=df2_APSA.reset_index()
    df2_APSA.to_csv('APSA_DataFrame_{}.csv'.format(area), sep=',')

    df2_APSA=pd.read_csv('APSA_DataFrame_{}.csv'.format(area), sep=',')
    df2_APSA['%in_complete']=1-df2_APSA['complete']/df2_APSA['total']
    df2_APSA=df2_APSA.fillna(0)
    # df_e_counter=pd.read_csv('e_counter_DataFrame_{}.csv'.format(area), sep=',')
    df_equipment=pd.read_csv('equipment_{}.csv'.format(area), sep=',')
    df_equipment= df_equipment.dropna()
    df_equipment = df_equipment.drop_duplicates(subset='equipment')
    df_equipment=df_equipment.reset_index()
    df_equipment=df_equipment.drop(df_equipment.index[[ind for ind in df_equipment.index if 'F-' in df_equipment.iloc[ind,3]]])
    df_equipment=df_equipment.reset_index()

    del df_equipment['level_0']
    del df_equipment['index']
    del df_equipment['Unnamed: 0']


    print('-------------retrieve OMS data of area {}-------------'.format(area))
#     if area == 1:
#         list_feeder_name=List_N1_feeder_name
#     elif area ==2:
#          list_feeder_name=List_N2_feeder_name
#     elif area ==3:
#         list_feeder_name=List_N3_feeder_name
#     dict_feeder = {item1:{item2:[df_equipment.iloc[item3, 1] for item3 in set(np.where(df_equipment['type']==item2)[0]).intersection(np.where(df_equipment['feeder']==item1)[0])] for item2 in df_equipment['type'].unique()} for item1 in list_feeder_name}

    if area == 1:
        list_feeder_name=List_N1_feeder_name
    elif area ==2:
        list_feeder_name=List_N2_feeder_name
    elif area ==3:
        list_feeder_name=List_N3_feeder_name
    num_feeder=1
    dict_counter={}
    for feeder in tqdm(list_feeder_name):
#         print(feeder)
        num_feeder=num_feeder+1
        res2=requests.get("http://172.30.200.113/webcenter/views/omsp50.php?feeder={}&year={}".format(feeder, year))
        res2=res2.json()
        if res2 !=['{Not found DATA..}']:
            list_month_oms=[int(oms_detail['month'].replace(" ", "")) for oms_detail in res2]
            list_type_oms=[oms_detail['type_oper'] for oms_detail in res2]
            df_OMS=pd.DataFrame()
            df_OMS['month']=list_month_oms
            df_OMS['type']=list_type_oms
            temp_df_OMS=df_OMS.drop(np.where(df_OMS['month']!=month)[0]).copy()

            if 'T/L' in list(temp_df_OMS['type'].value_counts().keys()):
                num_TL=temp_df_OMS['type'].value_counts()['T/L']
            else:
                num_TL=0
            if 'T/R' in list(temp_df_OMS['type'].value_counts().keys()):
                num_TR=temp_df_OMS['type'].value_counts()['T/R']
            else:
                num_TR=0
        else:
    #             print('-- no OMS data --')
            num_TL, num_TR=0,0
    #         print(feeder , 'T/L:', num_TL, 'T/R:',num_TR)
        dict_counter.update({feeder:{'T/L':num_TL, 'T/R':num_TR}})
        pass
    print('-------------retrieve max, average load data of area {}-------------'.format(area))
    if area == 1:
        list_feeder_name=List_N1_feeder_name
    elif area ==2:
         list_feeder_name=List_N2_feeder_name
    elif area ==3:
        list_feeder_name=List_N3_feeder_name

    df_input_layer=pd.DataFrame()
    for feeder in tqdm(list_feeder_name):
        temp_df_input_layer=pd.DataFrame()
        input_layer1_2=df2_APSA.loc[df2_APSA['feedername'].values==feeder+'VB01']
        temp_df_input_layer['feeder']=[feeder]
        temp_df_input_layer['sum_TR']=dict_counter[feeder]['T/R']
        temp_df_input_layer['sum_TL']=dict_counter[feeder]['T/L']
        temp_df_input_layer['in_progress']=input_layer1_2['%in_complete'].values[0]

        if area == 1:
            temp_df_input_layer['Peak load']=abs(get_max_load_N1(area, feeder, year, month))
            temp_df_input_layer['Average load']=abs(get_ava_load_N1(area, feeder, year, month))
        elif area == 2:
            temp_df_input_layer['Peak load']=abs(get_max_load_N2(area, feeder, year, month))
            temp_df_input_layer['Average load']=abs(get_ava_load_N2(area, feeder, year, month))
        elif area == 3:
            temp_df_input_layer['Peak load']=abs(get_peak_load_N3(area, feeder, year, month))
            temp_df_input_layer['Average load']=abs(get_peak_load_N3(area, feeder, year, month)/4)
        df_input_layer=df_input_layer.append(temp_df_input_layer)
        pass

    df_input_layer=df_input_layer.reset_index()
    del df_input_layer['index']
    df_nor_input_layer=nor_input_layer(df_input_layer.copy())
    df_input_layer=df_input_layer.fillna(0)
    df_nor_input_layer=df_nor_input_layer.fillna(0)



    print('-------------FHM calculation of area {}-------------'.format(area))
    df_input_weight=pd.read_csv('weight_input.csv')
    del df_input_weight['Load Break']
    del df_input_weight['Recloser']
    del df_input_weight['SCB']
    del df_input_weight['Fixed Capacitor Bank']
    del df_input_weight['LRR(FRTU)']
    del df_input_weight['AVR']
    list_input=['sum_TR','sum_TL','in_progress','Peak load','Average load']

    input_range=[[0,1]]*(len(list(df_nor_input_layer))-1)  #[[x1_min, x1_max],[x2_min, x2_max],...,[xn_min, xn_max]]
    number_input=len(input_range)
    dict_FHI={}

    if area == 1:
        list_feeder_name=List_N1_feeder_name
    elif area ==2:
         list_feeder_name=List_N2_feeder_name
    elif area ==3:
        list_feeder_name=List_N3_feeder_name

    for feeder in tqdm(list_feeder_name):
    #     print(feeder)
        num_equipment = len(dict_feeder[feeder]['CB'])+len(dict_feeder[feeder]['SCB'])+len(dict_feeder[feeder]['Recloser'])+len(dict_feeder[feeder]['Switch'])
        num_CB=len(dict_feeder[feeder]['CB'])
        num_Switch=len(dict_feeder[feeder]['Switch'])
        num_Recloser=len(dict_feeder[feeder]['Recloser'])
        num_SCB=len(dict_feeder[feeder]['SCB'])
        if num_equipment !=0:
            list_equipment=[1]*num_CB + [2]*num_Switch + [3]*num_Recloser + [4]*num_SCB
            list_equipment_2=['w1']*num_CB + ['w2']*num_Switch + ['w4']*num_Recloser + ['w7']*num_SCB
            input_weight=np.array([[float(df_input_weight.iloc[np.where(df_input_weight['Input/Equipment']==input1)[0],equipment])for input1 in list_input] for equipment in list_equipment])
            nor_input_weight=np.array([input_weight[inp]/input_weight.sum(axis=1)[inp] for inp in np.arange(0,len(input_weight),1)])
            output_weight=np.array([dict_nor_weights[equipment]/{'w1':num_CB, 'w2':num_Switch, 'w4':num_Recloser, 'w7':num_SCB}[equipment] for equipment in list_equipment_2])
            nor_output_weight=output_weight/output_weight.sum(axis=0)
            net1 = nl.net.newff(input_range, [num_equipment, 1], [nl.trans.PureLin(), nl.trans.PureLin()])  #num_equipment =len [CB1, CB2, REC1, REC2, SW1, SW2]

            for input in np.arange(0,len(nor_input_weight),1):
                net1.layers[0].np['w'][input]= nor_input_weight[input]
            net1.layers[0].np['b']=[0]*num_equipment
            net1.layers[1].np['w'][0]=nor_output_weight
            net1.layers[0].np['b']=[0]*num_equipment
            net1.layers[1].np['b']=[0]
            df_nor_input_layer.iloc[np.where(df_nor_input_layer['feeder']==feeder)[0],1:]
            output=net1.sim(np.array(df_nor_input_layer.iloc[np.where(df_nor_input_layer['feeder']==feeder)[0],1:]).tolist())
    #         print(output)
            dict_FHI.update({feeder:1-output[0][0]})
        else:
            dict_FHI.update({feeder:1})


    # print(dict_FHI)
    df_input_layer['FHI']=[dict_FHI[feeder] for feeder in df_input_layer['feeder'].tolist()]
#     print(df_input_layer)

    with open("FHM_{}.json".format(are),'w') as outfile:
        json.dump(dict_FHI, outfile, cls=NumpyEncoder)

    print('-------------FHM area {} is saved-------------'.format(area))


print('-------------add urban area -------------')


#read all 3N json file
list_FHI=[]

list_urban={'1':['CMA01','CMA02','CMA03','CMA04','CMA05','CMA06','CMA07','CMA08','CMA09','CMA10','CMB01','CMB02','CMB03','CMB04','CMB05','CMB06','CMB07','CMB08','CMB09','CMB10','CMC01','CMC02','CMC03','CMD03','CMD07','CMD08','CMD10','CMF01','CMF02','CMF03','CMF04','CMF05','CMU01','CMU02','CMU03','CMU04','CMU05','CMV01','CMV02','CMV03','CMV04','CMV05','MRM07'],'2':['PLA02',
'PLA03','PLA04','PLA05','PLA06','PLA07','PLA08','PLC01','PLC02','PLC03','PLC04','PLC06','PLC07','PLT05','WGT05','MSA04','MSA05','MSA06','MSA11','MSA12'],'3':['LBA01','LBA02','LBA03','LBA04','LBA05','LBA06','LBA07','LBA08','LBC01','LBC02','LBC03','LBC04','LBC05']}
for area in tqdm([1,2,3]):
    with open('FHM_{}.json'.format(area)) as json_data:
        d=json.load(json_data)
        if area == 1:
            list_feeder_name=List_N1_feeder_name
        elif area ==2:
             list_feeder_name=List_N2_feeder_name
        elif area ==3:
            print(d)
            list_feeder_name=List_N3_feeder_name
        list_FHI.append([{'Region':'1{}'.format(area), 'sub':feeder[0:3], 'feeder':feeder, 'HI':d[feeder], 'Urban':feeder in list_urban['{}'.format(area)]} for feeder in list_feeder_name])

all_dict_FHM={'raw_data':[item2 for item1 in list_FHI for item2 in item1]}

with open("FHM.json",'w') as outfile:
    json.dump(all_dict_FHM, outfile, cls=NumpyEncoder)

print('-------------FHM.json file is saved -------------')

# coding=utf-8
"""
1、算法对比测试使用
2、调用不同算法取对应数据
3、对数据进行对比
"""

from openai_sdk_base import *
from sensoro.tools.ReadConfig import *
import threading

config = read_config()
db = DB()


# 1、根据图片类型，获取对应属性，并调用不同对象方法，将属性与标记字段映射存储到数据库
class WholeTarget:
    def __init__(self, url):
        self.url = url

    def whole_target(self):
        baidu = BaiduAi(config["sdk"]["DianJun"]["user"],
                        config["sdk"]["DianJun"]["password"],
                        config["sdk"]["DianJun"]["url"])

        # image = '/Users/sunzhaohui/Desktop/SensoroTestData/算法对比测试集/非机动车/非机动车0.jpeg'
        data = db.execute_sql(f"""
        select id,file_path,type from algorithm_precision where result1 is not null and result2 is null""")
        # data = db.execute_sql(f"""select id,file_path,type from algorithm_precision where result1 is NULL""")

        for im_id, image, im_type in data:
            num = 0  # 记录返回的对象数量，若大于1则放弃
            att = {}
            location = []  # 部分目标会识别成两个，判断是否相同，相同时取其中一个即可
            try:
                response = baidu.base_detect(
                    self.url, image, "filepath", enable_multiple=True)
                # print(json.dumps(response))
            except Exception as e:
                raise e
                print(e, "服务异常！")

            if im_type == 1:
                # print(im_id, response)
                try:
                    if 'data' in response:
                        for obj in response['data']['items']:
                            if obj['type'] == 'face':
                                num += 1
                                item = obj
                                location.append(obj)
                        if num == 1:
                            # print(1)
                            face(item, im_id, att)
                        elif num == 2:
                            if (location[0]['location']['left'] == location[1]['location']['left']
                                    and location[0]['location']['top'] == location[1]['location']['top']
                                    and location[0]['location']['width'] == location[1]['location']['width']
                                    and location[0]['location']['height'] == location[1]['location']['height']):

                                item = location[0]
                                face(item, im_id, att)
                            else:
                                face(location[0], im_id, att)
                        elif num > 2:
                            face(location[0], im_id, att)
                        elif num == 0:
                            print(im_id)
                    else:
                        print(im_id)
                except Exception as e:
                    # raise e
                    print('返回无数据', im_id)
                    continue

            elif im_type == 2:
                # data = db.execute_sql(f"""select id,file_path from algorithm_precision where type=2""")
                try:
                    if 'data' in response:
                        for obj in response['data']['items']:
                            if obj['type'] == 'human':
                                num += 1
                                item = obj
                                location.append(obj)
                        if num == 1:
                            human(item, im_id, att)
                        elif num == 2:
                            if (location[0]['location']['left'] == location[1]['location']['left']
                                    and location[0]['location']['top'] == location[1]['location']['top']
                                    and location[0]['location']['width'] == location[1]['location']['width']
                                    and location[0]['location']['height'] == location[1]['location']['height']):

                                item = location[0]
                                human(item, im_id, att)
                            else:
                                human(location[0], im_id, att)
                        elif num > 2:
                            human(location[0], im_id, att)
                        elif num == 0:
                            print(im_id)
                    else:
                        print(im_id)
                except Exception as e:
                    raise e
                    print('返回无数据', im_id)
                    continue

            elif im_type == 3:
                # print(im_id)
                try:
                    if 'data' in response:
                        for obj in response['data']['items']:
                            if obj['type'] == 'car':
                                num += 1
                                item = obj
                                location.append(obj)
                        if num == 1:
                            car(item, im_id, att)
                        elif num == 2:

                            if (location[0]['location']['left'] == location[1]['location']['left']
                                    and location[0]['location']['top'] == location[1]['location']['top']
                                    and location[0]['location']['width'] == location[1]['location']['width']
                                    and location[0]['location']['height'] == location[1]['location']['height']):

                                item = location[0]
                                car(item, im_id, att)
                            else:
                                car(location[0], im_id, att)
                        elif num > 2:
                            car(location[0], im_id, att)
                        elif num == 0:
                            print(im_id)
                    else:
                        print(im_id)

                except Exception as e:
                    # raise e
                    print('返回无数据', im_id)
                    continue

            else:
                try:
                    if 'data' in response:
                        for obj in response['data']['items']:
                            if obj['type'] == 'electric-car':
                                num += 1
                                item = obj
                                location.append(obj)
                        if num == 1:
                            ele(item, im_id, att)
                        elif num == 2:

                            if (location[0]['location']['left'] == location[1]['location']['left']
                                    and location[0]['location']['top'] == location[1]['location']['top']
                                    and location[0]['location']['width'] == location[1]['location']['width']
                                    and location[0]['location']['height'] == location[1]['location']['height']):

                                item = location[0]
                                ele(item, im_id, att)
                            else:
                                ele(location[0], im_id, att)
                        elif num > 2:
                            ele(location[0], im_id, att)
                        elif num == 0:
                            print(im_id)
                    else:
                        print(im_id)

                except Exception as e:
                    # raise e
                    print('返回无数据或调用异常，向下继续执行！', im_id)
                    continue
            # print(att)


def face(item, im_id, att):
    att['帽子'] = '未知'

    if item['gender']['name'] == 'male':
        att['性别'] = '男'
    elif item['gender']['name'] == 'female':
        att['性别'] = '女'
    else:
        att['性别'] = '未知'

    if item['glasses']['name'] == 'common':
        att['眼镜'] = '戴普通眼镜'
    elif item['glasses']['name'] == 'sun':
        att['眼镜'] = '戴墨镜'
    elif item['glasses']['name'] == 'none':
        att['眼镜'] = '未戴眼镜'
    else:
        att['眼镜'] = '未知'

    if item['age'] <= 6:
        att['年龄段'] = '小孩'
    elif 7 < item['age'] <= 40:
        att['年龄段'] = '青年'
    elif 40 < item['age'] <= 60:
        att['年龄段'] = '中年'
    elif item['age'] > 60:
        att['年龄段'] = '老年'
    else:
        att['年龄段'] = '未知'

    if item['mask']['name'] == '1':
        att['佩戴口罩'] = '佩戴口罩'
    elif item['mask']['name'] == '0':
        att['佩戴口罩'] = '未戴口罩'
    else:
        att['佩戴口罩'] = '未知'
    # print(att)
    db.execute_sql(
        f"""update algorithm_precision set result2='{json.dumps(att, ensure_ascii=False)}' where id={im_id}""")


def human(item, im_id, att):

    # 帽子
    if item['attribute']['headwear']['name'] == '无帽':
        att['帽子'] = '未戴帽子'
    elif item['attribute']['headwear']['name'] == '普通帽':
        att['帽子'] = '戴普通帽子'
    elif item['attribute']['headwear']['name'] == '安全帽':
        att['帽子'] = '戴安全帽子'
    else:
        att['帽子'] = '未知'

    # 性别
    if item['attribute']['gender']['name'] == '男性':
        att['性别'] = '男'
    elif item['attribute']['gender']['name'] == '女性':
        att['性别'] = '女'
    else:
        att['性别'] = '未知'

    # 眼镜
    if item['attribute']['glasses']['name'] == '戴眼镜':
        att['眼镜'] = '戴普通眼镜'
    elif item['attribute']['glasses']['name'] == '戴墨镜':
        att['眼镜'] = '戴墨镜'
    elif item['attribute']['glasses']['name'] == '无眼镜':
        att['眼镜'] = '未戴眼镜'
    else:
        att['眼镜'] = '未知'

    if item['attribute']['age']['name'] == '幼儿':
        att['年龄段'] = '小孩'
    elif item['attribute']['age']['name'] in ('青少年', '青年'):
        att['年龄段'] = '青年'
    elif item['attribute']['age']['name'] == '中年':
        att['年龄段'] = '中年'
    elif item['attribute']['age']['name'] == '老年':
        att['年龄段'] = '老年'
    else:
        att['年龄段'] = '未知'

    if item['attribute']['upper_wear_texture']['name'] in ('纯色', '图案', '条纹', '格子'):
        att['上身纹理'] = item['attribute']['upper_wear_texture']['name']
    elif item['attribute']['upper_wear_texture']['name'] == '碎花':
        att['上身纹理'] = '花纹'
    elif item['attribute']['upper_wear_texture']['name'] == '条纹或格子':
        att['上身纹理'] = '格子'
    else:
        att['上身纹理'] = '未知'

    # 上身颜色
    if item['attribute']['upper_color']['name'] in ('红', '橙', '黄', '绿', '蓝', '紫', '粉', '黑', '白', '灰', '棕'):
        att['上身颜色'] = f"{item['attribute']['upper_color']['name']}色"
    else:
        att['上身颜色'] = '未知'

    if item['attribute']['lower_wear']['name'] == '不确定':
        att['下身类别'] = '未知'
    else:
        att['下身类别'] = item['attribute']['lower_wear']['name']

    if item['attribute']['upper_color']['name'] in ('红', '橙', '黄', '绿', '蓝', '紫', '粉', '黑', '白', '灰', '棕'):
        att['下身颜色'] = f"{item['attribute']['lower_color']['name']}色"
    else:
        att['下身颜色'] = '未知'

    if item['attribute']['orientation']['name'] in ('正面', '背面', '左侧面', '右侧面'):
        att['人体朝向'] = item['attribute']['orientation']['name']
    else:
        att['人体朝向'] = '未知'

    if item['attribute']['face_mask']['name'] == '戴口罩':
        att['佩戴口罩'] = '佩戴口罩'
    elif item['attribute']['face_mask']['name'] == '无口罩':
        att['佩戴口罩'] = '未戴口罩'
    else:
        att['佩戴口罩'] = '未知'

    if item['attribute']['action']['name'] in ('站立', '蹲或坐', '走', '跑'):
        att['动作姿态'] = item['attribute']['action']['name']
    else:
        att['动作姿态'] = '未知'

    # 是否吸烟
    if item['attribute']['smoke']['name'] in ('吸烟', '未吸烟'):
        att['是否吸烟'] = item['attribute']['smoke']['name']
    else:
        att['是否吸烟'] = '未知'

    att['随身物品'] = []
    if item['attribute']['carrying_baby']['name'] == '抱小孩':
        att['随身物品'].append('抱小孩')
    if item['attribute']['bag']['name'] == '单肩包':
        att['随身物品'].append('单肩包或斜挎包')
    elif item['attribute']['bag']['name'] == '双肩包':
        att['随身物品'].append('双肩包')
    if item['attribute']['umbrella']['name'] == '打伞':
        att['随身物品'].append('打伞')
    if item['attribute']['carrying_item']['name'] == '有手提物':
        att['随身物品'].append('拎物品')
    if item['attribute']['luggage']['name'] == '有拉杆箱':
        att['随身物品'].append('行李箱')

    if item['attribute']['cellphone']['name'] in ('未使用手机', '看手机'):
        att['是否用手机'] = item['attribute']['cellphone']['name']
    elif item['attribute']['cellphone']['name'] == '打电话':
        att['是否用手机'] = '打手机'
    else:
        att['是否用手机'] = '未知'

    db.execute_sql(
        f"""update algorithm_precision set result2='{json.dumps(att, ensure_ascii=False)}' where id={im_id}""")


def car(item, im_id, att):
    # 车牌号码
    if 'plate' in item:
        att['车牌号码'] = item['plate']['plate_number']
    else:
        att['车牌号码'] = '未知'

    # 是否有车牌
    if item['attribute']['has_plate']['name'] == '有车牌':
        att['是否有车牌'] = '有车牌号码'
    elif item['attribute']['has_plate']['name'] == '无车牌':
        att['是否有车牌'] = '无车牌'
    else:
        att['是否有车牌'] = '未知'

    # 车牌颜色
    if 'plate' in item:
        if item['plate']['plate_color'] == 'blue':
            att['车牌颜色'] = '蓝色'
        elif item['plate']['plate_color'] == 'yellow':
            att['车牌颜色'] = '黄色'
        elif item['plate']['plate_color'] == 'white':
            att['车牌颜色'] = '白色'
        else:
            att['车牌颜色'] = '未知'
    else:
        att['车牌颜色'] = '未知'

    # 车牌状态
    att['车牌状态'] = []
    att['车牌状态'].append(item['attribute']['plate_cover']['name'])
    att['车牌状态'].append(item['attribute']['has_plate']['name'])
    att['车牌状态'].append(item['attribute']['plate_stained']['name'])

    # 机动车品牌
    att['机动车品牌'] = item['model']['brand']

    # 机动车类型；百度无此字段，取特殊车辆统计
    att['机动车类型'] = '未知'

    # 车身颜色
    vehicle_color = item['attribute']['vehicle_color']['name'].replace('车身颜色', '')
    if vehicle_color in ('红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '棕色', '粉色', '白色', '黑色'):
        att['车身颜色'] = vehicle_color
    elif vehicle_color == '深空灰':
        att['车身颜色'] = '灰色'
    elif vehicle_color == '金银色':
        att['车身颜色'] = '银色'
    else:
        att['车身颜色'] = '未知'

    # 车辆朝向
    if 'motor_direction' in item['attribute']:
        if item['attribute']['motor_direction']['name'] in ('车辆朝向正向', '车辆朝向背向', '车辆朝向左向', '车辆朝向右向'):
            att['车辆朝向'] = item['attribute']['motor_direction']['name']
        else:
            att['车辆朝向'] = '未知'
    else:
        att['车辆朝向'] = '未知'

    # 车辆行驶方向；direction	车辆行驶方向	车辆正向行驶、车辆背向行驶、车辆左侧行驶、车辆右侧行驶
    if item['attribute']['direction']['name'] in ('车辆正向行驶', '车辆背向行驶', '车辆左侧行驶', '车辆右侧行驶'):
        att['车辆行驶方向'] = item['attribute']['direction']['name']
    else:
        att['车辆行驶方向'] = '未知'

    # 车顶架状态；top_holder	是否有车顶架	无车顶架、有车顶架
    if item['attribute']['top_holder']['name'] in ('无车顶架', '有车顶架'):
        att['车顶架状态'] = item['attribute']['top_holder']['name']
    else:
        att['车顶架状态'] = '未知'

    # 天窗状态；skylight
    if item['attribute']['skylight']['name'] in ('有天窗', '无天窗'):
        att['天窗状态'] = item['attribute']['skylight']['name']
    else:
        att['天窗状态'] = '未知'

    # 车窗雨眉
    if item['attribute']['window_rain_eyebrow']['name'] in ('有车窗雨眉', '无车窗雨眉'):
        att['车窗雨眉'] = item['attribute']['window_rain_eyebrow']['name']
    else:
        att['车窗雨眉'] = '未知'

    # 车前摆放物；vehicle_front_item_placeitems	是否有车前摆放物	无车前摆放物、有车前摆放物
    if item['attribute']['vehicle_front_item_placeitems']['name'] in ('无车前摆放物', '有车前摆放物'):
        att['车前摆放物'] = item['attribute']['vehicle_front_item_placeitems']['name']
    else:
        att['车前摆放物'] = '未知'

    # 有无后视镜挂件;vehicle_front_item_pendant	是否有后视镜挂件	无后视镜挂件、有后视镜挂件
    if item['attribute']['vehicle_front_item_pendant']['name'] in ('无后视镜挂件', '有后视镜挂件'):
        att['有无后视镜挂件'] = item['attribute']['vehicle_front_item_pendant']['name']
    else:
        att['有无后视镜挂件'] = '未知'

    # 车身有无喷字;body_spray	是否车身喷字	车身无喷字、车身有喷字
    if item['attribute']['body_spray']['name'] in ('车身无喷字', '车身有喷字'):
        att['车身有无喷字'] = item['attribute']['body_spray']['name']
    else:
        att['车身有无喷字'] = '未知'

    # 有无备胎；spare_wheel
    if item['attribute']['spare_wheel']['name'] in ('有备胎', '无备胎'):
        att['有无备胎'] = item['attribute']['spare_wheel']['name']
    else:
        att['有无备胎'] = '未知'

    # 是否车前有纸巾盒；vehicle_front_item_tissuebox	是否车前有纸巾盒	车前无纸巾盒、车前有纸巾盒
    if item['attribute']['vehicle_front_item_tissuebox']['name'] in ('车前无纸巾盒', '车前有纸巾盒'):
        att['是否车前有纸巾盒'] = item['attribute']['vehicle_front_item_tissuebox']['name']
    else:
        att['是否车前有纸巾盒'] = '未知'

    # 是否有年检标;vehicle_inspection	是否有年检标	无年检标、有年检标
    if item['attribute']['vehicle_inspection']['name'] in ('无年检标', '有年检标'):
        att['是否有年检标'] = item['attribute']['vehicle_inspection']['name']
    else:
        att['是否有年检标'] = '未知'

    # 车门状态
    if item['attribute']['door_open']['name'] in ('车门关闭', '车门打开'):
        att['车门状态'] = item['attribute']['door_open']['name']
    else:
        att['车门状态'] = '未知'

    # 驾驶员状态
    if 'has_pilot' in item['attribute']:
        if item['attribute']['has_pilot']['name'] in ('有驾驶人', '无驾驶人'):
            att['驾驶员状态'] = item['attribute']['has_pilot']['name']
        else:
            att['驾驶员状态'] = '未知'
    else:
        att['驾驶员状态'] = '未知'

    # 驾驶员是否系安全带;safety_belt_pilot	驾驶员安全带是否系带	驾驶员未系安全带、驾驶员系安全带
    if item['attribute']['safety_belt_pilot']['name'] in ('驾驶员未系安全带', '驾驶员系安全带'):
        att['驾驶员是否系安全带'] = item['attribute']['safety_belt_pilot']['name']
    else:
        att['驾驶员是否系安全带'] = '未知'

    # 驾驶员遮阳板是否放下;sunvisor_pilot	驾驶员遮阳板是否放下	驾驶员遮阳板未放下、驾驶员遮阳板放下
    if item['attribute']['sunvisor_pilot']['name'] in ('驾驶员遮阳板未放下', '驾驶员遮阳板放下'):
        att['驾驶员遮阳板是否放下'] = item['attribute']['sunvisor_pilot']['name']
    else:
        att['驾驶员遮阳板是否放下'] = '未知'

    # 驾驶员是否打电话；calling	是否驾驶员打电话	驾驶员未打电话、驾驶员打电话
    if item['attribute']['calling']['name'] in ('驾驶员未打电话', '驾驶员打电话'):
        att['驾驶员是否打电话'] = item['attribute']['calling']['name']
    else:
        att['驾驶员是否打电话'] = '未知'

    # 副驾驶是否有人;has_copilot	副驾驶位是否有人	副驾驶无人、副驾驶有人
    if item['attribute']['has_copilot']['name'] in ('副驾驶无人', '副驾驶有人'):
        att['副驾驶是否有人'] = item['attribute']['has_copilot']['name']
    else:
        att['副驾驶是否有人'] = '未知'

    # 副驾驶是否系安全带;safety_belt_copilot	副驾驶安全带是否系带	副驾驶未系安全带、副驾驶系安全带
    if item['attribute']['safety_belt_copilot']['name'] in ('副驾驶未系安全带', '副驾驶系安全带'):
        att['副驾驶是否系安全带'] = item['attribute']['safety_belt_copilot']['name']
    else:
        att['副驾驶是否系安全带'] = '未知'

    # 副驾驶员是否打电话,无此属性
    att['副驾驶员是否打电话'] = ''

    # 副驾驶员遮阳板状态;sunvisor_copilot	副驾驶遮阳板是否放下	副驾驶遮阳板未放下、副驾驶遮阳板放下
    if item['attribute']['sunvisor_copilot']['name'] in ('副驾驶遮阳板未放下', '副驾驶遮阳板放下'):
        att['副驾驶员遮阳板状态'] = item['attribute']['sunvisor_copilot']['name']
    else:
        att['副驾驶员遮阳板状态'] = '未知'

    # 特殊车辆
    if item['attribute']['dangerous_vehicle']['name'] == '危险品车':
        att['特殊车辆'] = '危化品车'
    elif item['attribute']['special_vehicle']['name'] in ('普通车', '施工工程车', '校车', '搅拌车', '救护车',
                                                          '工程抢险车', '警车', '消防车', '洒水车'):
        att['特殊车辆'] = item['attribute']['special_vehicle']['name']
    elif item['attribute']['special_vehicle']['name'] == '施工工程车':
        att['特殊车辆'] = '市政工程&环卫&园林车'
    elif item['attribute']['slag_vehicle']['name'] == '渣土车':
        att['特殊车辆'] = '渣土车'
    else:
        att['特殊车辆'] = '未知'

    # 是否为危化品车;dangerous_vehicle	是否为危化品车  非危险品车、危险品车
    if item['attribute']['dangerous_vehicle']['name'] in ('非危险品车', '危险品车'):
        att['是否为危化品车'] = item['attribute']['dangerous_vehicle']['name']
    else:
        att['是否为危化品车'] = '未知'

    # 是否为渣土车;slag_vehicle	是否为渣土车	非渣土车、渣土车
    if item['attribute']['slag_vehicle']['name'] in ('非渣土车', '渣土车'):
        att['是否为渣土车'] = item['attribute']['slag_vehicle']['name']
    else:
        att['是否为渣土车'] = '未知'

    # 渣土车改装，slag_refit 渣土车未改装、渣土车改装
    if item['attribute']['slag_refit']['name'] in ('渣土车未改装', '渣土车改装'):
        att['渣土车改装'] = item['attribute']['slag_refit']['name']
    else:
        att['渣土车改装'] = '未知'

    # 渣土车满载；slag_full_loaded	渣土车满载	渣土车未满载、渣土车满载
    if item['attribute']['slag_full_loaded']['name'] in ('渣土车未满载', '渣土车满载'):
        att['渣土车满载'] = item['attribute']['slag_full_loaded']['name']
    else:
        att['渣土车满载'] = '未知'

    db.execute_sql(
        f"""update algorithm_precision set result2='{json.dumps(att, ensure_ascii=False)}' where id={im_id}""")


def ele(item, im_id, att):
    # 性别，无此属性
    att['性别'] = '未知'

    # 年龄段，无此属性
    att['年龄段'] = '未知'

    # 上身纹理，无此属性
    att['上身纹理'] = '未知'

    # 上身颜色；pilot_upper_color	骑车人上衣颜色
    if 'pilot_upper_color' in item['attribute']:
        color = item['attribute']['pilot_upper_color']['name'].replace('骑车人上衣颜色', '')
        att['上身颜色'] = color
    else:
        att['上身颜色'] = '未知'

    # 头部特征
    att['头部特征'] = []
    if 'has_helment' in item['attribute']:
        if item['attribute']['has_helment']['name'] == '带头盔':
            att['头部特征'].append('头盔')

    # 车身颜色;与car属性一致
    if 'vehicle_color' in item['attribute']:
        vehicle_color = item['attribute']['vehicle_color']['name'].replace('车身颜色', '')
        if vehicle_color in ('红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '棕色', '粉色', '白色', '黑色'):
            att['车身颜色'] = vehicle_color
        elif vehicle_color in ('深空灰', '金银色'):
            att['车身颜色'] = '灰色'
        else:
            att['车身颜色'] = '未知'
    else:
        att['车身颜色'] = '未知'

    # 车辆类型;category - desc
    if item['desc'] in ('摩托车', '电动摩托车', '电动自行车'):
        att['车辆类型'] = '摩托车/电瓶车（电动摩托车/电动自行车）'
    elif item['desc'] in ('儿童脚踏车', '手推车', '滑板车', '自行车', '三轮车'):
        att['车辆类型'] = item['desc']
    else:
        att['车辆类型'] = '未知'

    db.execute_sql(
        f"""update algorithm_precision set result2='{json.dumps(att, ensure_ascii=False)}' where id={im_id}""")


def update_day():   # 更新时间段
    data = db.execute_sql(
        f"""select id, attribute from algorithm_precision where result1 is not Null and day is null""")

    for im_id, att in data:  # 洗数据
        att = json.loads(att)
        day = att['时间段']
        db.execute_sql(
            f"""update algorithm_precision set day='{day}' where id={im_id}""")


# 2、对比数据
class Contrast:

    def __init__(self):
        self.true = {'face': {
                        '白天': {
                            '性别': {'男': 0, '女': 0, '未知': 0},
                            '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                            '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                            '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                            '帽子': '百度无此属性'
                                },
                        '夜间': {
                            '性别': {'男': 0, '女': 0, '未知': 0},
                            '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                            '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                            '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                            '帽子': '百度无此属性'
                                }
                             },
                     'human': {
                         '白天': {
                             '性别': {'男': 0, '女': 0, '未知': 0},
                             '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                             '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                             '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                             '帽子': {'未戴帽子': 0, '戴普通帽子': 0, '头盔': 0, '戴头巾': 0, '佩戴橙色安全帽': 0,
                                    '佩戴红色安全帽': 0, '佩戴黄色安全帽': 0, '佩戴白色安全帽': 0,
                                    '佩戴其他颜色安全帽': 0, '未知': 0},
                             '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                             '上身纹理': {'格子': 0, '花纹': 0, '纯色': 0, '条纹': 0, '图案': 0, '未知': 0},
                             '下身类别': {'短裤': 0, '裙子': 0, '长裤': 0, '长裙': 0, '短裙': 0, '未知': 0},
                             '下身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                             '随身物品': {'双肩包': 0, '手提包': 0, '拎物品': 0, '行李箱': 0, '婴儿车': 0,
                                      '抱小孩': 0, '打伞': 0, '单肩包或斜挎包': 0, '未知': 0},
                             '动作姿态': {'站立': 0, '蹲或坐': 0, '走': 0, '跑': 0, '未知': 0},
                             '人体朝向': {'正面': 0, '背面': 0, '左侧面': 0, '右侧面': 0, '未知': 0},
                             '是否吸烟': {'吸烟': 0, '未吸烟': 0, '未知': 0},
                             '是否用手机': {"打手机": 0, '看手机': 0, '未使用手机': 0, '未知': 0}
                                },
                         '夜间': {
                             '性别': {'男': 0, '女': 0, '未知': 0},
                             '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                             '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                             '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                             '帽子': {'未戴帽子': 0, '戴普通帽子': 0, '头盔': 0, '戴头巾': 0, '佩戴橙色安全帽': 0,
                                    '佩戴红色安全帽': 0, '佩戴黄色安全帽': 0, '佩戴白色安全帽': 0,
                                    '佩戴其他颜色安全帽': 0, '未知': 0},
                             '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                             '上身纹理': {'格子': 0, '花纹': 0, '纯色': 0, '条纹': 0, '图案': 0, '未知': 0},
                             '下身类别': {'短裤': 0, '裙子': 0, '长裤': 0, '长裙': 0, '短裙': 0, '未知': 0},
                             '下身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                             '随身物品': {'双肩包': 0, '手提包': 0, '拎物品': 0, '行李箱': 0, '婴儿车': 0,
                                      '抱小孩': 0, '打伞': 0, '单肩包或斜挎包': 0, '未知': 0},
                             '动作姿态': {'站立': 0, '蹲或坐': 0, '走': 0, '跑': 0, '未知': 0},
                             '人体朝向': {'正面': 0, '背面': 0, '左侧面': 0, '右侧面': 0, '未知': 0},
                             '是否吸烟': {'吸烟': 0, '未吸烟': 0, '未知': 0},
                             '是否用手机': {"打手机": 0, '看手机': 0, '未使用手机': 0, '未知': 0}
                                }
                              },
                     'car': {
                         '白天': {
                             '车牌号码': 0,
                             '是否有车牌': {'有车牌号码': 0, '无车牌': 0, '未知': 0},
                             '车牌颜色': {'黄色': 0, '黄绿色': 0, '绿色': 0, '蓝色': 0, '白色': 0, '黑色': 0, '未知': 0},
                             '车牌状态': {'部分遮挡': 0, '全部遮挡': 0, '未遮挡': 0, '没有车牌': 0, '状态未知': 0,
                                      '车牌污损': 0, '车牌模糊': 0, '车牌反光': 0, '其它类型遮挡': 0, '未知': 0},
                             '机动车品牌': {'jeep': 0, '奥迪': 0, '宝骏': 0, '宝马': 0, '保时捷': 0, '北奔重卡': 0,
                                       '奔驰': 0, '本田': 0, '比亚迪': 0, '标致': 0, '别克': 0, '丰田': 0,
                                       '福特': 0, '哈弗': 0, '吉利': 0, '江淮': 0, '凯迪拉克': 0, '雷克萨斯': 0,
                                       '马自达': 0, '奇瑞': 0, '起亚': 0, '日产': 0, '荣威': 0, '斯柯达': 0,
                                       '特斯拉': 0, '沃尔沃': 0, '五菱': 0, '雪佛兰': 0, '长城': 0, '众泰': 0,
                                       '大众': 0,'未知': 0},
                             '机动车类型': '百度在算法为特殊车辆类型',
                             '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '未知': 0},
                             '车辆朝向': {'车辆朝向正向': 0, '车辆朝向背向': 0, '车辆朝向左向': 0, '车辆朝向右向': 0, '未知': 0},
                             '车辆行驶方向': {'车辆正向行驶': 0, '车辆背向行驶': 0, '车辆左侧行驶': 0, '车辆右侧行驶': 0, '未知': 0},
                             '车顶架状态': {'有车顶架': 0, '无车顶架': 0, '未知': 0},
                             '天窗状态': {'有天窗': 0, '无天窗': 0, '未知': 0},
                             '车窗雨眉': {'有车窗雨眉': 0, '无车窗雨眉': 0, '未知': 0},
                             '车前摆放物': {'有车前摆放物': 0, '无车前摆放物': 0, '未知': 0},
                             '有无后视镜挂件': {'有后视镜挂件': 0, '无后视镜挂件': 0, '未知': 0},
                             '车身有无喷字': {'车身无喷字': 0, '车身有喷字': 0, '未知': 0},
                             '有无备胎': {'有备胎': 0, '无备胎': 0, '未知': 0},
                             '是否车前有纸巾盒': {'车前有纸巾盒': 0, '车前无纸巾盒': 0, '未知': 0},
                             '是否有年检标': {'有年检标': 0, '无年检标': 0, '未知': 0},
                             '车门状态': {'车门关闭': 0, '车门打开': 0, '未知': 0},
                             '驾驶员状态': {'有驾驶人': 0, '无驾驶人': 0, '未知': 0},
                             '驾驶员是否系安全带': {'驾驶员未系安全带': 0, '驾驶员系安全带': 0, '未知': 0},
                             '驾驶员遮阳板是否放下': {'驾驶员遮阳板放下': 0, '驾驶员遮阳板未放下': 0, '未知': 0},
                             '驾驶员是否打电话': {'驾驶员打电话': 0, '驾驶员未打电话': 0, '未知': 0},
                             '副驾驶是否有人': {'副驾驶有人': 0, '副驾驶无人': 0, '未知': 0},
                             '副驾驶是否系安全带': {'副驾驶系安全带': 0, '副驾驶未系安全带': 0, '未知': 0},
                             '副驾驶员是否打电话': '百度无此属性',
                             '副驾驶员遮阳板状态': {'副驾驶遮阳板放下': 0, '副驾驶遮阳板未放下': 0, '未知': 0},
                             '特殊车辆': {'危化品车': 0, '校车': 0, '搅拌车': 0, '黄标车': 0, '渣土车': 0,
                                      '邮政车': 0, '市政工程&环卫&园林车': 0, '救护车': 0, '工程抢险车': 0,
                                      '警车': 0, '安保车': 0, '消防车': 0, '未知': 0},
                             '是否为危化品车': {'危险品车': 0, '非危险品车': 0, '未知': 0},
                             '是否为渣土车': {'渣土车': 0, '非渣土车': 0, '未知': 0},
                             '渣土车满载': {'渣土车满载': 0, '渣土车未满载': 0, '未知': 0},
                             '渣土车改装': {'渣土车改装': 0, '渣土车未改装': 0, '未知': 0}
                                },
                         '夜间': {
                             '车牌号码': 0,
                             '是否有车牌': {'有车牌号码': 0, '无车牌': 0, '未知': 0},
                             '车牌颜色': {'黄色': 0, '黄绿色': 0, '绿色': 0, '蓝色': 0, '白色': 0, '黑色': 0, '未知': 0},
                             '车牌状态': {'部分遮挡': 0, '全部遮挡': 0, '未遮挡': 0, '没有车牌': 0, '状态未知': 0,
                                      '车牌污损': 0, '车牌模糊': 0, '车牌反光': 0, '其它类型遮挡': 0, '未知': 0},
                             '机动车品牌': {'jeep': 0, '奥迪': 0, '宝骏': 0, '宝马': 0, '保时捷': 0, '北奔重卡': 0,
                                       '奔驰': 0, '本田': 0, '比亚迪': 0, '标致': 0, '别克': 0, '丰田': 0,
                                       '福特': 0, '哈弗': 0, '吉利': 0, '江淮': 0, '凯迪拉克': 0, '雷克萨斯': 0,
                                       '马自达': 0, '奇瑞': 0, '起亚': 0, '日产': 0, '荣威': 0, '斯柯达': 0,
                                       '特斯拉': 0, '沃尔沃': 0, '五菱': 0, '雪佛兰': 0, '长城': 0, '众泰': 0,
                                       '大众': 0,'未知': 0},
                             '机动车类型': '百度在算法为特殊车辆类型',
                             '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '未知': 0},
                             '车辆朝向': {'车辆朝向正向': 0, '车辆朝向背向': 0, '车辆朝向左向': 0, '车辆朝向右向': 0, '未知': 0},
                             '车辆行驶方向': {'车辆正向行驶': 0, '车辆背向行驶': 0, '车辆左侧行驶': 0, '车辆右侧行驶': 0, '未知': 0},
                             '车顶架状态': {'有车顶架': 0, '无车顶架': 0, '未知': 0},
                             '天窗状态': {'有天窗': 0, '无天窗': 0, '未知': 0},
                             '车窗雨眉': {'有车窗雨眉': 0, '无车窗雨眉': 0, '未知': 0},
                             '车前摆放物': {'有车前摆放物': 0, '无车前摆放物': 0, '未知': 0},
                             '有无后视镜挂件': {'有后视镜挂件': 0, '无后视镜挂件': 0, '未知': 0},
                             '车身有无喷字': {'车身无喷字': 0, '车身有喷字': 0, '未知': 0},
                             '有无备胎': {'有备胎': 0, '无备胎': 0, '未知': 0},
                             '是否车前有纸巾盒': {'车前有纸巾盒': 0, '车前无纸巾盒': 0, '未知': 0},
                             '是否有年检标': {'有年检标': 0, '无年检标': 0, '未知': 0},
                             '车门状态': {'车门关闭': 0, '车门打开': 0, '未知': 0},
                             '驾驶员状态': {'有驾驶人': 0, '无驾驶人': 0, '未知': 0},
                             '驾驶员是否系安全带': {'驾驶员未系安全带': 0, '驾驶员系安全带': 0, '未知': 0},
                             '驾驶员遮阳板是否放下': {'驾驶员遮阳板放下': 0, '驾驶员遮阳板未放下': 0, '未知': 0},
                             '驾驶员是否打电话': {'驾驶员打电话': 0, '驾驶员未打电话': 0, '未知': 0},
                             '副驾驶是否有人': {'副驾驶有人': 0, '副驾驶无人': 0, '未知': 0},
                             '副驾驶是否系安全带': {'副驾驶系安全带': 0, '副驾驶未系安全带': 0, '未知': 0},
                             '副驾驶员是否打电话': {'副驾驶员打电话': 0, '副驾驶员未打电话': 0, '未知': 0},
                             '副驾驶员遮阳板状态': {'副驾驶遮阳板放下': 0, '副驾驶遮阳板未放下': 0, '未知': 0},
                             '特殊车辆': {'危化品车': 0, '校车': 0, '搅拌车': 0, '黄标车': 0, '渣土车': 0,
                                      '邮政车': 0, '市政工程&环卫&园林车': 0, '救护车': 0, '工程抢险车': 0,
                                      '警车': 0, '安保车': 0, '消防车': 0, '未知': 0},
                             '是否为危化品车': {'危险品车': 0, '非危险品车': 0, '未知': 0},
                             '是否为渣土车': {'渣土车': 0, '非渣土车': 0, '未知': 0},
                             '渣土车满载': {'渣土车满载': 0, '渣土车未满载': 0, '未知': 0},
                             '渣土车改装': {'渣土车改装': 0, '渣土车未改装': 0, '未知': 0}
                                }
                            },
                     'ele-car': {
                         '白天': {
                             '车辆类型': {'自行车': 0, '摩托车/电瓶车（电动摩托车/电动自行车）': 0, '儿童脚踏车': 0,
                                      '手推车': 0, '滑板车': 0, '三轮车（有顶篷）': 0, '三轮车（封闭驾驶舱）': 0,
                                      '三轮车（无顶篷/无封闭）': 0, '未知': 0},
                             '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '花色': 0, '未知': 0},
                             '性别': '百度无此属性',
                             '年龄段': '百度无此属性',
                             '上身纹理': '百度无此属性',
                             '头部特征': {'眼镜': 0, '帽子': 0, '头盔': 0, '佩戴口罩': 0, '未知': 0},
                             '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0}
                                },
                         '夜间': {
                             '车辆类型': {'自行车': 0, '摩托车/电瓶车（电动摩托车/电动自行车）': 0, '儿童脚踏车': 0,
                                      '手推车': 0, '滑板车': 0, '三轮车（有顶篷）': 0, '三轮车（封闭驾驶舱）': 0,
                                      '三轮车（无顶篷/无封闭）': 0, '未知': 0},
                             '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '花色': 0, '未知': 0},
                             '性别': '百度无此属性',
                             '年龄段': '百度无此属性',
                             '上身纹理': '百度无此属性',
                             '头部特征': {'眼镜': 0, '帽子': 0, '头盔': 0, '佩戴口罩': 0, '未知': 0},
                             '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                                      '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0}
                                }
                                }
                     }
        self.false = {'face': {
            '白天': {
                '性别': {'男': 0, '女': 0, '未知': 0},
                '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                '帽子': '百度无此属性'
            },
            '夜间': {
                '性别': {'男': 0, '女': 0, '未知': 0},
                '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                '帽子': '百度无此属性'
            }
        },
            'human': {
                '白天': {
                    '性别': {'男': 0, '女': 0, '未知': 0},
                    '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                    '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                    '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                    '帽子': {'未戴帽子': 0, '戴普通帽子': 0, '头盔': 0, '戴头巾': 0, '佩戴橙色安全帽': 0,
                           '佩戴红色安全帽': 0, '佩戴黄色安全帽': 0, '佩戴白色安全帽': 0,
                           '佩戴蓝色安全帽': 0, '佩戴其他颜色安全帽': 0, '未知': 0},
                    '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                    '上身纹理': {'格子': 0, '花纹': 0, '纯色': 0, '条纹': 0, '图案': 0, '未知': 0},
                    '下身类别': {'短裤': 0, '裙子': 0, '长裤': 0, '长裙': 0, '短裙': 0, '未知': 0},
                    '下身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                    '随身物品': {'双肩包': 0, '手提包': 0, '拎物品': 0, '行李箱': 0, '婴儿车': 0,
                             '抱小孩': 0, '打伞': 0, '单肩包或斜挎包': 0, '未知': 0},
                    '动作姿态': {'站立': 0, '蹲或坐': 0, '走': 0, '跑': 0, '未知': 0},
                    '人体朝向': {'正面': 0, '背面': 0, '左侧面': 0, '右侧面': 0, '未知': 0},
                    '是否吸烟': {'吸烟': 0, '未吸烟': 0, '未知': 0},
                    '是否用手机': {"打手机": 0, '看手机': 0, '未使用手机': 0, '未知': 0}
                },
                '夜间': {
                    '性别': {'男': 0, '女': 0, '未知': 0},
                    '年龄段': {'小孩': 0, '青年': 0, '中年': 0, '老年': 0, '未知': 0},
                    '佩戴口罩': {'佩戴口罩': 0, '未戴口罩': 0, '未知': 0},
                    '眼镜': {'未戴眼镜': 0, '戴普通眼镜': 0, '戴太阳镜': 0, '未知': 0},
                    '帽子': {'未戴帽子': 0, '戴普通帽子': 0, '头盔': 0, '戴头巾': 0, '佩戴橙色安全帽': 0,
                           '佩戴红色安全帽': 0, '佩戴黄色安全帽': 0, '佩戴白色安全帽': 0,
                           '佩戴其他颜色安全帽': 0, '未知': 0},
                    '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                    '上身纹理': {'格子': 0, '花纹': 0, '纯色': 0, '条纹': 0, '图案': 0, '未知': 0},
                    '下身类别': {'短裤': 0, '裙子': 0, '长裤': 0, '长裙': 0, '短裙': 0, '未知': 0},
                    '下身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0},
                    '随身物品': {'双肩包': 0, '手提包': 0, '拎物品': 0, '行李箱': 0, '婴儿车': 0,
                             '抱小孩': 0, '打伞': 0, '单肩包或斜挎包': 0, '未知': 0},
                    '动作姿态': {'站立': 0, '蹲或坐': 0, '走': 0, '跑': 0, '未知': 0},
                    '人体朝向': {'正面': 0, '背面': 0, '左侧面': 0, '右侧面': 0, '未知': 0},
                    '是否吸烟': {'吸烟': 0, '未吸烟': 0, '未知': 0},
                    '是否用手机': {"打手机": 0, '看手机': 0, '未使用手机': 0, '未知': 0}
                }
            },
            'car': {
                '白天': {
                    '车牌号码': 0,
                    '是否有车牌': {'有车牌号码': 0, '无车牌': 0, '未知': 0},
                    '车牌颜色': {'黄色': 0, '黄绿色': 0, '绿色': 0, '蓝色': 0, '白色': 0, '黑色': 0, '未知': 0},
                    '车牌状态': {'部分遮挡': 0, '全部遮挡': 0, '未遮挡': 0, '没有车牌': 0, '状态未知': 0,
                             '车牌污损': 0, '车牌模糊': 0, '车牌反光': 0, '其它类型遮挡': 0, '未知': 0},
                    '机动车品牌': {'jeep': 0, '奥迪': 0, '宝骏': 0, '宝马': 0, '保时捷': 0, '北奔重卡': 0,
                              '奔驰': 0, '本田': 0, '比亚迪': 0, '标致': 0, '别克': 0, '丰田': 0,
                              '福特': 0, '哈弗': 0, '吉利': 0, '江淮': 0, '凯迪拉克': 0, '雷克萨斯': 0,
                              '马自达': 0, '奇瑞': 0, '起亚': 0, '日产': 0, '荣威': 0, '斯柯达': 0,
                              '特斯拉': 0, '沃尔沃': 0, '五菱': 0, '雪佛兰': 0, '长城': 0, '众泰': 0,
                              '大众': 0,'未知': 0},
                    '机动车类型': '百度在算法为特殊车辆类型',
                    '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '未知': 0},
                    '车辆朝向': {'车辆朝向正向': 0, '车辆朝向背向': 0, '车辆朝向左向': 0, '车辆朝向右向': 0, '未知': 0},
                    '车辆行驶方向': {'车辆正向行驶': 0, '车辆背向行驶': 0, '车辆左侧行驶': 0, '车辆右侧行驶': 0, '未知': 0},
                    '车顶架状态': {'有车顶架': 0, '无车顶架': 0, '未知': 0},
                    '天窗状态': {'有天窗': 0, '无天窗': 0, '未知': 0},
                    '车窗雨眉': {'有车窗雨眉': 0, '无车窗雨眉': 0, '未知': 0},
                    '车前摆放物': {'有车前摆放物': 0, '无车前摆放物': 0, '未知': 0},
                    '有无后视镜挂件': {'有后视镜挂件': 0, '无后视镜挂件': 0, '未知': 0},
                    '车身有无喷字': {'车身无喷字': 0, '车身有喷字': 0, '未知': 0},
                    '有无备胎': {'有备胎': 0, '无备胎': 0, '未知': 0},
                    '是否车前有纸巾盒': {'车前有纸巾盒': 0, '车前无纸巾盒': 0, '未知': 0},
                    '是否有年检标': {'有年检标': 0, '无年检标': 0, '未知': 0},
                    '车门状态': {'车门关闭': 0, '车门打开': 0, '未知': 0},
                    '驾驶员状态': {'有驾驶人': 0, '无驾驶人': 0, '未知': 0},
                    '驾驶员是否系安全带': {'驾驶员未系安全带': 0, '驾驶员系安全带': 0, '未知': 0},
                    '驾驶员遮阳板是否放下': {'驾驶员遮阳板放下': 0, '驾驶员遮阳板未放下': 0, '未知': 0},
                    '驾驶员是否打电话': {'驾驶员打电话': 0, '驾驶员未打电话': 0, '未知': 0},
                    '副驾驶是否有人': {'副驾驶有人': 0, '副驾驶无人': 0, '未知': 0},
                    '副驾驶是否系安全带': {'副驾驶系安全带': 0, '副驾驶未系安全带': 0, '未知': 0},
                    '副驾驶员是否打电话': '百度无此属性',
                    '副驾驶员遮阳板状态': {'副驾驶遮阳板放下': 0, '副驾驶遮阳板未放下': 0, '未知': 0},
                    '特殊车辆': {'危化品车': 0, '校车': 0, '搅拌车': 0, '黄标车': 0, '渣土车': 0,
                             '邮政车': 0, '市政工程&环卫&园林车': 0, '救护车': 0, '工程抢险车': 0,
                             '警车': 0, '安保车': 0, '消防车': 0, '未知': 0},
                    '是否为危化品车': {'危险品车': 0, '非危险品车': 0, '未知': 0},
                    '是否为渣土车': {'渣土车': 0, '非渣土车': 0, '未知': 0},
                    '渣土车满载': {'渣土车满载': 0, '渣土车未满载': 0, '未知': 0},
                    '渣土车改装': {'渣土车改装': 0, '渣土车未改装': 0, '未知': 0}
                },
                '夜间': {
                    '车牌号码': 0,
                    '是否有车牌': {'有车牌号码': 0, '无车牌': 0, '未知': 0},
                    '车牌颜色': {'黄色': 0, '黄绿色': 0, '绿色': 0, '蓝色': 0, '白色': 0, '黑色': 0, '未知': 0},
                    '车牌状态': {'部分遮挡': 0, '全部遮挡': 0, '未遮挡': 0, '没有车牌': 0, '状态未知': 0,
                             '车牌污损': 0, '车牌模糊': 0, '车牌反光': 0, '其它类型遮挡': 0, '未知': 0},
                    '机动车品牌': {'jeep': 0, '奥迪': 0, '宝骏': 0, '宝马': 0, '保时捷': 0, '北奔重卡': 0,
                              '奔驰': 0, '本田': 0, '比亚迪': 0, '标致': 0, '别克': 0, '丰田': 0,
                              '福特': 0, '哈弗': 0, '吉利': 0, '江淮': 0, '凯迪拉克': 0, '雷克萨斯': 0,
                              '马自达': 0, '奇瑞': 0, '起亚': 0, '日产': 0, '荣威': 0, '斯柯达': 0,
                              '特斯拉': 0, '沃尔沃': 0, '五菱': 0, '雪佛兰': 0, '长城': 0, '众泰': 0,
                              '大众': 0,'未知': 0},
                    '机动车类型': '百度在算法为特殊车辆类型',
                    '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '未知': 0},
                    '车辆朝向': {'车辆朝向正向': 0, '车辆朝向背向': 0, '车辆朝向左向': 0, '车辆朝向右向': 0, '未知': 0},
                    '车辆行驶方向': {'车辆正向行驶': 0, '车辆背向行驶': 0, '车辆左侧行驶': 0, '车辆右侧行驶': 0, '未知': 0},
                    '车顶架状态': {'有车顶架': 0, '无车顶架': 0, '未知': 0},
                    '天窗状态': {'有天窗': 0, '无天窗': 0, '未知': 0},
                    '车窗雨眉': {'有车窗雨眉': 0, '无车窗雨眉': 0, '未知': 0},
                    '车前摆放物': {'有车前摆放物': 0, '无车前摆放物': 0, '未知': 0},
                    '有无后视镜挂件': {'有后视镜挂件': 0, '无后视镜挂件': 0, '未知': 0},
                    '车身有无喷字': {'车身无喷字': 0, '车身有喷字': 0, '未知': 0},
                    '有无备胎': {'有备胎': 0, '无备胎': 0, '未知': 0},
                    '是否车前有纸巾盒': {'车前有纸巾盒': 0, '车前无纸巾盒': 0, '未知': 0},
                    '是否有年检标': {'有年检标': 0, '无年检标': 0, '未知': 0},
                    '车门状态': {'车门关闭': 0, '车门打开': 0, '未知': 0},
                    '驾驶员状态': {'有驾驶人': 0, '无驾驶人': 0, '未知': 0},
                    '驾驶员是否系安全带': {'驾驶员未系安全带': 0, '驾驶员系安全带': 0, '未知': 0},
                    '驾驶员遮阳板是否放下': {'驾驶员遮阳板放下': 0, '驾驶员遮阳板未放下': 0, '未知': 0},
                    '驾驶员是否打电话': {'驾驶员打电话': 0, '驾驶员未打电话': 0, '未知': 0},
                    '副驾驶是否有人': {'副驾驶有人': 0, '副驾驶无人': 0, '未知': 0},
                    '副驾驶是否系安全带': {'副驾驶系安全带': 0, '副驾驶未系安全带': 0, '未知': 0},
                    '副驾驶员是否打电话': {'副驾驶员打电话': 0, '副驾驶员未打电话': 0, '未知': 0},
                    '副驾驶员遮阳板状态': {'副驾驶遮阳板放下': 0, '副驾驶遮阳板未放下': 0, '未知': 0},
                    '特殊车辆': {'危化品车': 0, '校车': 0, '搅拌车': 0, '黄标车': 0, '渣土车': 0,
                             '邮政车': 0, '市政工程&环卫&园林车': 0, '救护车': 0, '工程抢险车': 0,
                             '警车': 0, '安保车': 0, '消防车': 0, '未知': 0},
                    '是否为危化品车': {'危险品车': 0, '非危险品车': 0, '未知': 0},
                    '是否为渣土车': {'渣土车': 0, '非渣土车': 0, '未知': 0},
                    '渣土车满载': {'渣土车满载': 0, '渣土车未满载': 0, '未知': 0},
                    '渣土车改装': {'渣土车改装': 0, '渣土车未改装': 0, '未知': 0}
                }
            },
            'ele-car': {
                '白天': {
                    '车辆类型': {'自行车': 0, '摩托车/电瓶车（电动摩托车/电动自行车）': 0, '儿童脚踏车': 0,
                             '手推车': 0, '滑板车': 0, '三轮车（有顶篷）': 0, '三轮车（封闭驾驶舱）': 0,
                             '三轮车（无顶篷/无封闭）': 0, '未知': 0},
                    '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '花色': 0, '未知': 0},
                    '性别': '百度无此属性',
                    '年龄段': '百度无此属性',
                    '上身纹理': '百度无此属性',
                    '头部特征': {'眼镜': 0, '帽子': 0, '头盔': 0, '佩戴口罩': 0, '未知': 0},
                    '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0}
                },
                '夜间': {
                    '车辆类型': {'自行车': 0, '摩托车/电瓶车（电动摩托车/电动自行车）': 0, '儿童脚踏车': 0,
                             '手推车': 0, '滑板车': 0, '三轮车（有顶篷）': 0, '三轮车（封闭驾驶舱）': 0,
                             '三轮车（无顶篷/无封闭）': 0, '未知': 0},
                    '车身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '银色': 0, '花色': 0, '未知': 0},
                    '性别': '百度无此属性',
                    '年龄段': '百度无此属性',
                    '上身纹理': '百度无此属性',
                    '头部特征': {'眼镜': 0, '帽子': 0, '头盔': 0, '佩戴口罩': 0, '未知': 0},
                    '上身颜色': {'红色': 0, '橙色': 0, '黄色': 0, '绿色': 0, '蓝色': 0, '紫色': 0,
                             '棕色': 0, '粉色': 0, '白色': 0, '灰色': 0, '黑色': 0, '花色': 0, '未知': 0}
                }
            }
        }

        self.false_id = {
            'face': [],
            'human': [],
            'car': [],
            'ele-car': []
        }

    def contrast(self, result):
        data = db.execute_sql(
            f"""select id, attribute, {result}, type, day from algorithm_precision 
            where result1 is not Null and result2 is not null and day in ('白天', '夜间')""")

        for im_id, att, v, im_type, day in data:
            att = json.loads(att)
            v = json.loads(v)

            for key, value in att.items():
                if key == '时间段':
                    continue

                if value == '':
                    value = '未知'
                if not value:
                    value.append('未知')

                if im_type == 1:
                    # print(im_id)
                    if key == '帽子':
                        continue
                    elif att[key] == v[key]:
                        self.true['face'][day][key][value] += 1
                    else:
                        self.false['face'][day][key][value] += 1
                        self.false_id['face'].append(f"{key}{im_id}")
                elif im_type == 2:
                    # print(im_id, key, value)
                    if key == '随身物品':
                        for item in value:
                            if item in v[key]:
                                self.true['human'][day][key][item] += 1
                            else:
                                self.false['human'][day][key][item] += 1
                                self.false_id['human'].append(f"{key}{im_id}")

                    elif key == '行为':
                        if value in ('看手机', '未使用手机', '打手机'):
                            if v['是否用手机'] == value:
                                self.true['human'][day]['是否用手机'][value] += 1
                            else:
                                self.false['human'][day]['是否用手机'][value] += 1
                                self.false_id['human'].append(f"{'是否用手机'}{im_id}")

                        elif value in ('未吸烟', '吸烟'):
                            if value == v['是否吸烟']:
                                self.true['human'][day]['是否吸烟'][value] += 1
                            else:
                                self.false['human'][day]['是否吸烟'][value] += 1
                                self.false_id['human'].append(f"{'是否吸烟'}{im_id}")

                    elif att[key] == v[key]:

                        self.true['human'][day][key][value] += 1
                    else:
                        self.false['human'][day][key][value] += 1
                        self.false_id['human'].append(f"{key}{im_id}")
                elif im_type == 3:
                    # print(im_id, key, value)
                    if key in ('机动车类型', '副驾驶员是否打电话'):
                        continue
                    elif key == '车牌状态':
                        for item in value:
                            if item in v[key]:
                                self.true['car'][day][key][item] += 1
                            else:
                                self.false['car'][day][key][item] += 1
                                self.false_id['human'].append(f"{'车牌状态'}{im_id}")
                    elif key == '车牌号码':
                        if value == v[key]:
                            self.true['car'][day]['车牌号码'] += 1
                        else:
                            self.false['car'][day]['车牌号码'] += 1
                            self.false_id['human'].append(f"{'车牌号码'}{im_id}")
                    elif att[key] == v[key]:
                        self.true['car'][day][key][value] += 1
                    else:
                        self.false['car'][day][key][value] += 1
                        self.false_id['human'].append(f"{key}{im_id}")
                elif im_type == 4:
                    # print(im_id, key, value)
                    if key in ('性别', '年龄段', '上身纹理'):
                        continue
                    elif key == '头部特征':
                        for item in value:
                            if item in v[key]:
                                self.true['ele-car'][day][key][item] += 1
                            else:
                                self.false['ele-car'][day][key][item] += 1
                                self.false_id['ele-car'].append(f"{key}{im_id}")

                    elif att[key] == v[key]:

                        self.true['ele-car'][day][key][value] += 1
                    else:
                        self.false['ele-car'][day][key][value] += 1
                        self.false_id['ele-car'].append(f"{key}{im_id}")

        # 异常数据，分析结果时使用
        # print(self.false_id)
        # if result == 'result2':
        #     # print(self.false_id)
        #     for i in self.false_id['ele-car']:
        #         if '车辆类型' in i:
        #             print(i)

        return self.true, self.false, self.false_id


# 标记图片
class Target:

    def __init__(self, url):
        self.url = url

    def target(self):

        # 查询所有本次算法需要的数据
        data = db.execute_sql(f"""select id, attribute, file_path, type from algorithm_precision 
        where id in (14096)""")

        baidu = BaiduAi(config["server"]["DianJun"]["user"],
                        config["server"]["DianJun"]["password"],
                        config["server"]["DianJun"]["url"])

        for num in range(1):  # 控制循环5次，防止网络问题导致的失败
            # 判断是否有未处理过的图片，无直接结束循环
            if not data:
                break
            else:
                for im_id, att, image, im_type in data:

                    att = json.loads(att)
                    print(f'标记属性:{att["车辆类型"]}')

                    point = {}  # 记录坐标
                    try:
                        response = baidu.base_detect(
                            self.url, image, "filepath", enable_multiple=True)
                    except Exception as e:
                        # raise e
                        print(e, "服务异常，重新执行！")
                        continue
                    print(response)
                    try:
                        if response["code"] == 0:  # 判断是否成功调用接口
                            if 'data' in response:  # 部分接口未识别到对象时返回无data字段
                                if response["data"]["item_count"] > 0:  # 判断接口是否识别到对象
                                    value = ""  # 参数组装
                                    items = response["data"]["items"]

                                    for item in items:
                                        # print(item)
                                        if im_type == 4:
                                            if item['type'] == 'electric-car':
                                                print(item['desc'])
                                                # print(im_id, item['location'])
                                                point['e' + str(item['id'])] = self._get_point(item['location'])
                                        if im_type == 3:
                                            if item['type'] == 'car':
                                                point['c' + str(item['id'])] = self._get_point(json.loads(item['location']))
                                        if im_type == 2:
                                            if item['type'] == 'human':
                                                point['h' + str(item['id'])] = self._get_point(json.loads(item['location']))
                                        if im_type == 1:
                                            if item['type'] == 'face':
                                                point['f' + str(item['id'])] = self._get_point(json.loads(item['location']))
                                    if point:
                                        self._draw_rectangle(image, point)  # 对图像标记并将新文件位置保存至数据库

                    except Exception as e:
                        raise e
                        print(e, "服务异常，重新执行！")
                        continue

    # 获取对象坐标
    @staticmethod
    def _get_point(location):
        return (
            (int(location['left']), int(location['top'])),
            (
                int(location['left'] + location['width']),
                int(location['top'] + location['height'])
            )
        )

    # 对图片进行标记，并返回标记后图片的保存位置
    @staticmethod
    def _draw_rectangle(image, point):
        img = cv2.imread(image)
        # print(point)
        for key, value in point.items():

            if key[0] == 'b':
                color = (255, 255, 0)

            elif key[0] == 'h':
                color = (0, 255, 0)

            elif key[0] == 'f':
                color = (0, 0, 255)

            elif key[0] == 'c':
                color = (255, 0, 0)

            elif key[0] == 'e':
                color = (0, 255, 255)

            cv2.rectangle(img, value[0], value[1], color, 2, 4)
            cv2.putText(img, key, (value[0][0], value[0][1] + 30), cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=color,
                        thickness=2)

        new_img_file_path = os.path.split(image)[0] + f"/结果/"
        if not os.path.exists(new_img_file_path):
            os.makedirs(new_img_file_path)

        cv2.imwrite(f"{new_img_file_path}{os.path.split(image)[1]}", img)


# 打印结果
def print_result(v1_true, v1_false, v2_true, v2_false):
    # print(v1[0], v2[0], v1[1], v2[1])
    print('v1 face true')
    for k, v in v1_true['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 face false')
    for k, v in v1_false['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 face true')
    for k, v in v2_true['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 face false')
    for k, v in v2_false['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 human true')
    for k, v in v1_true['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 human false')
    for k, v in v1_false['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 human true')
    for k, v in v2_true['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 human false')
    for k, v in v2_false['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 car true')
    for k, v in v1_true['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 car false')
    for k, v in v1_false['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 car true')
    for k, v in v2_true['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 car false')
    for k, v in v2_false['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 ele true')
    for k, v in v1_true['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 ele false')
    for k, v in v1_false['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 ele true')
    for k, v in v2_true['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 ele false')
    print(v2_false)
    for k, v in v2_false['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()


# 取v1正确，v2异常的数据
def v_false(v1_false_id, v2_false_id):
    # print(v1_false_id)
    for i in v2_false_id['human']:

        if '年龄段' in i and (i not in v1_false_id['human']):
            print(i)


if __name__ == '__main__':

    # 调用接口并整理对应属性
    # WholeTarget('/v2/whole/target/detect').whole_target()

    # 更新时间段
    # update_day()

    # v1_true, v1_false, v1_false_id = Contrast().contrast('result1')
    # v2_true, v2_false, v2_false_id = Contrast().contrast('result2')

    # print_result(v1_true, v1_false, v2_true, v2_false)

    # 取v1正确，v2错误的数据
    # v_false(v1_false_id, v2_false_id)

    # 调用接口标记图片
    Target('/v1/whole/target/detect').target()
    print('v2')
    Target('/v2/whole/target/detect').target()
    #
    # data = db.execute_sql(f"""select id, attribute from algorithm_precision where type=3 and day in ('白天', '夜间')""")
    # for id, att in data:
    #     # print(att)
    #     att = json.loads(att)
    #     # print(att)
    #     if '车牌号码(非必填)' in att:
    #         att['车牌号码'] = att.pop('车牌号码(非必填)')
    #
    #         db.execute_sql(f"""update algorithm_precision
    #         set attribute='{json.dumps(att, ensure_ascii=False)}' where id={id}""")
    #     if '是否吸烟' in att:
    #         pass
    #         print('是否吸烟', att['是否吸烟'])

    db.close()


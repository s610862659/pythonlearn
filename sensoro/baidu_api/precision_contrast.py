# coding=utf-8
"""
1、算法对比测试使用
2、调用不同算法取对应数据
3、对数据进行对比
"""

from openai_sdk_base import BaiduAi
from sensoro.tools.DrawRectangle import draw_rectangle
import json
from sensoro.tools.ReadConfig import read_config
from sensoro.tools.DB import DB
import os
import datetime
import threading

config = read_config()
db = DB()


# 1、根据图片类型，获取对应属性，并调用不同对象方法，将属性与标记字段映射存储到数据库
class WholeTarget:
    def __init__(self, url, version):
        self.url = url
        self.result = {}    # 记录属性及坐标内容，保存至数据库
        self.version = version  # 版本

    def whole_target(self):
        baidu = BaiduAi(config["sdk"]["DianJun"]["user"],
                        config["sdk"]["DianJun"]["password"],
                        config["sdk"]["DianJun"]["url"])

        # image = '/Users/sunzhaohui/Desktop/SensoroTestData/算法对比测试集/非机动车/非机动车0.jpeg'
        data = db.execute_sql(f"""
        select id,attribute, file_path,type from algorithm_precision where delete_time is null and type in (1,2)""")
        # data = db.execute_sql(f"""select id,file_path,type from algorithm_precision where result1 is NULL""")

        for im_id, attribute, image, im_type in data:

            try:
                response = baidu.base_detect(
                    self.url, image, "filepath", enable_multiple=True)
                # print(json.dumps(response))
            except Exception as e:
                # raise e
                print(e, "服务异常！")
            # print(im_id)
            try:
                if 'data' in response:
                    # print(response)
                    item = self.calc_overlap_rate(response['data']['items'], attribute, im_type)
                    if not item:
                        continue

                    self.result['location'] = item['location']
                    if im_type == 1:
                        self.face(item, im_id)
                    elif im_type == 2:
                        self.human(item, im_id)
                    elif im_type == 3:
                        self.car(item, im_id)
                    else:
                        self.ele(item, im_id)
            except Exception as e:
                raise e
                print('返回无数据', im_id)
                continue

    def face(self, item, im_id):

        self.result['帽子'] = '未知'

        if item['gender']['name'] == 'male':
            self.result['性别'] = '男'
        elif item['gender']['name'] == 'female':
            self.result['性别'] = '女'
        else:
            self.result['性别'] = '未知'

        if item['glasses']['name'] == 'common':
            self.result['眼镜'] = '戴普通眼镜'
        elif item['glasses']['name'] == 'sun':
            self.result['眼镜'] = '戴墨镜'
        elif item['glasses']['name'] == 'none':
            self.result['眼镜'] = '未戴眼镜'
        else:
            self.result['眼镜'] = '未知'

        if item['age'] <= 6:
            self.result['年龄段'] = '小孩'
        elif 7 < item['age'] <= 40:
            self.result['年龄段'] = '青年'
        elif 40 < item['age'] <= 60:
            self.result['年龄段'] = '中年'
        elif item['age'] > 60:
            self.result['年龄段'] = '老年'
        else:
            self.result['年龄段'] = '未知'

        if item['mask']['name'] == '1':
            self.result['佩戴口罩'] = '佩戴口罩'
        elif item['mask']['name'] == '0':
            self.result['佩戴口罩'] = '未戴口罩'
        else:
            self.result['佩戴口罩'] = '未知'
        # print(att)
        db.execute_sql(
            f"""update algorithm_precision set {self.version}='{json.dumps(self.result, ensure_ascii=False)}' where id={im_id}""")

    def human(self, item, im_id):

        # 帽子
        if item['attribute']['headwear']['name'] == '无帽':
            self.result['帽子'] = '未戴帽子'
        elif item['attribute']['headwear']['name'] == '普通帽':
            self.result['帽子'] = '戴普通帽子'
        elif item['attribute']['headwear']['name'] == '安全帽':
            self.result['帽子'] = '戴安全帽子'
        else:
            self.result['帽子'] = '未知'

        # 性别
        if item['attribute']['gender']['name'] == '男性':
            self.result['性别'] = '男'
        elif item['attribute']['gender']['name'] == '女性':
            self.result['性别'] = '女'
        else:
            self.result['性别'] = '未知'

        # 眼镜
        if item['attribute']['glasses']['name'] == '戴眼镜':
            self.result['眼镜'] = '戴普通眼镜'
        elif item['attribute']['glasses']['name'] == '戴墨镜':
            self.result['眼镜'] = '戴墨镜'
        elif item['attribute']['glasses']['name'] == '无眼镜':
            self.result['眼镜'] = '未戴眼镜'
        else:
            self.result['眼镜'] = '未知'

        if item['attribute']['age']['name'] == '幼儿':
            self.result['年龄段'] = '小孩'
        elif item['attribute']['age']['name'] in ('青少年', '青年'):
            self.result['年龄段'] = '青年'
        elif item['attribute']['age']['name'] == '中年':
            self.result['年龄段'] = '中年'
        elif item['attribute']['age']['name'] == '老年':
            self.result['年龄段'] = '老年'
        else:
            self.result['年龄段'] = '未知'

        if item['attribute']['upper_wear_texture']['name'] in ('纯色', '图案', '条纹', '格子'):
            self.result['上身纹理'] = item['attribute']['upper_wear_texture']['name']
        elif item['attribute']['upper_wear_texture']['name'] == '碎花':
            self.result['上身纹理'] = '花纹'
        elif item['attribute']['upper_wear_texture']['name'] == '条纹或格子':
            self.result['上身纹理'] = '格子'
        else:
            self.result['上身纹理'] = '未知'

        # 上身颜色
        if item['attribute']['upper_color']['name'] in ('红', '橙', '黄', '绿', '蓝', '紫', '粉', '黑', '白', '灰', '棕'):
            self.result['上身颜色'] = f"{item['attribute']['upper_color']['name']}色"
        else:
            self.result['上身颜色'] = '未知'

        if item['attribute']['lower_wear']['name'] == '不确定':
            self.result['下身类别'] = '未知'
        else:
            self.result['下身类别'] = item['attribute']['lower_wear']['name']

        if item['attribute']['upper_color']['name'] in ('红', '橙', '黄', '绿', '蓝', '紫', '粉', '黑', '白', '灰', '棕'):
            self.result['下身颜色'] = f"{item['attribute']['lower_color']['name']}色"
        else:
            self.result['下身颜色'] = '未知'

        if item['attribute']['orientation']['name'] in ('正面', '背面', '左侧面', '右侧面'):
            self.result['人体朝向'] = item['attribute']['orientation']['name']
        else:
            self.result['人体朝向'] = '未知'

        if item['attribute']['face_mask']['name'] == '戴口罩':
            self.result['佩戴口罩'] = '佩戴口罩'
        elif item['attribute']['face_mask']['name'] == '无口罩':
            self.result['佩戴口罩'] = '未戴口罩'
        else:
            self.result['佩戴口罩'] = '未知'

        if item['attribute']['action']['name'] in ('站立', '蹲或坐', '走', '跑'):
            self.result['动作姿态'] = item['attribute']['action']['name']
        else:
            self.result['动作姿态'] = '未知'

        # 是否吸烟
        if item['attribute']['smoke']['name'] in ('吸烟', '未吸烟'):
            self.result['是否吸烟'] = item['attribute']['smoke']['name']
        else:
            self.result['是否吸烟'] = '未知'

        self.result['随身物品'] = []
        if item['attribute']['carrying_baby']['name'] == '抱小孩':
            self.result['随身物品'].append('抱小孩')
        if item['attribute']['bag']['name'] == '单肩包':
            self.result['随身物品'].append('单肩包或斜挎包')
        elif item['attribute']['bag']['name'] == '双肩包':
            self.result['随身物品'].append('双肩包')
        if item['attribute']['umbrella']['name'] == '打伞':
            self.result['随身物品'].append('打伞')
        if item['attribute']['carrying_item']['name'] == '有手提物':
            self.result['随身物品'].append('拎物品')
        if item['attribute']['luggage']['name'] == '有拉杆箱':
            self.result['随身物品'].append('行李箱')

        if item['attribute']['cellphone']['name'] in ('未使用手机', '看手机'):
            self.result['是否用手机'] = item['attribute']['cellphone']['name']
        elif item['attribute']['cellphone']['name'] == '打电话':
            self.result['是否用手机'] = '打手机'
        else:
            self.result['是否用手机'] = '未知'

        db.execute_sql(
            f"""update algorithm_precision set {self.version}='{json.dumps(self.result, ensure_ascii=False)}' where id={im_id}""")

    def car(self, item, im_id):
        # 车牌号码
        if 'plate' in item:
            self.result['车牌号码'] = item['plate']['plate_number']
        else:
            self.result['车牌号码'] = '未知'

        # 是否有车牌
        if 'has_plate' in item['attribute']:
            if item['attribute']['has_plate']['name'] == '有车牌':
                self.result['是否有车牌'] = '有车牌号码'
            elif item['attribute']['has_plate']['name'] == '无车牌':
                self.result['是否有车牌'] = '无车牌'
            else:
                self.result['是否有车牌'] = '未知'
        else:
            self.result['是否有车牌'] = '未知'

        # 车牌颜色
        if 'plate' in item:
            if item['plate']['plate_color'] == 'blue':
                self.result['车牌颜色'] = '蓝色'
            elif item['plate']['plate_color'] == 'yellow':
                self.result['车牌颜色'] = '黄色'
            elif item['plate']['plate_color'] == 'white':
                self.result['车牌颜色'] = '白色'
            else:
                self.result['车牌颜色'] = '未知'
        else:
            self.result['车牌颜色'] = '未知'

        # 车牌状态
        self.result['车牌状态'] = []
        if 'plate_cover' in item['attribute']:
            self.result['车牌状态'].append(item['attribute']['plate_cover']['name'])
            self.result['车牌状态'].append(item['attribute']['has_plate']['name'])
            self.result['车牌状态'].append(item['attribute']['plate_stained']['name'])

        # 机动车品牌
        if 'model' in item:
            self.result['机动车品牌'] = item['model']['brand']
        else:
            self.result['机动车品牌'] = '未知'

        # 机动车类型；百度无此字段，取特殊车辆统计
        self.result['机动车类型'] = '未知'

        # 车身颜色
        if 'vehicle_color' in item['attribute']:
            vehicle_color = item['attribute']['vehicle_color']['name'].replace('车身颜色', '')
            if vehicle_color in ('红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '棕色', '粉色', '白色', '黑色'):
                self.result['车身颜色'] = vehicle_color
            elif vehicle_color == '深空灰':
                self.result['车身颜色'] = '灰色'
            elif vehicle_color == '金银色':
                self.result['车身颜色'] = '银色'
            else:
                self.result['车身颜色'] = '未知'
        else:
            self.result['车身颜色'] = '未知'

        # 车辆朝向
        if 'motor_direction' in item['attribute']:
            if item['attribute']['motor_direction']['name'] in ('车辆朝向正向', '车辆朝向背向', '车辆朝向左向', '车辆朝向右向'):
                self.result['车辆朝向'] = item['attribute']['motor_direction']['name']
            else:
                self.result['车辆朝向'] = '未知'
        else:
            self.result['车辆朝向'] = '未知'

        # 车辆行驶方向；direction	车辆行驶方向	车辆正向行驶、车辆背向行驶、车辆左侧行驶、车辆右侧行驶
        if 'direction' in item['attribute']:
            if item['attribute']['direction']['name'] in ('车辆正向行驶', '车辆背向行驶', '车辆左侧行驶', '车辆右侧行驶'):
                self.result['车辆行驶方向'] = item['attribute']['direction']['name']
            else:
                self.result['车辆行驶方向'] = '未知'
        else:
            self.result['车辆行驶方向'] = '未知'

        # 车顶架状态；top_holder	是否有车顶架	无车顶架、有车顶架
        if 'top_holder' in item['attribute']:
            if item['attribute']['top_holder']['name'] in ('无车顶架', '有车顶架'):
                self.result['车顶架状态'] = item['attribute']['top_holder']['name']
            else:
                self.result['车顶架状态'] = '未知'
        else:
            self.result['车顶架状态'] = '未知'

        # 天窗状态；skylight
        if 'skylight' in item['attribute']:
            if item['attribute']['skylight']['name'] in ('有天窗', '无天窗'):
                self.result['天窗状态'] = item['attribute']['skylight']['name']
            else:
                self.result['天窗状态'] = '未知'
        else:
            self.result['天窗状态'] = '未知'

        # 车窗雨眉
        if 'window_rain_eyebrow' in item['attribute']:
            if item['attribute']['window_rain_eyebrow']['name'] in ('有车窗雨眉', '无车窗雨眉'):
                self.result['车窗雨眉'] = item['attribute']['window_rain_eyebrow']['name']
            else:
                self.result['车窗雨眉'] = '未知'
        else:
            self.result['车窗雨眉'] = '未知'

        # 车前摆放物；vehicle_front_item_placeitems	是否有车前摆放物	无车前摆放物、有车前摆放物
        if 'vehicle_front_item_placeitems' in item['attribute']:
            if item['attribute']['vehicle_front_item_placeitems']['name'] in ('无车前摆放物', '有车前摆放物'):
                self.result['车前摆放物'] = item['attribute']['vehicle_front_item_placeitems']['name']
            else:
                self.result['车前摆放物'] = '未知'
        else:
            self.result['车前摆放物'] = '未知'

        # 有无后视镜挂件;vehicle_front_item_pendant	是否有后视镜挂件	无后视镜挂件、有后视镜挂件
        if 'vehicle_front_item_pendant' in item['attribute']:
            if item['attribute']['vehicle_front_item_pendant']['name'] in ('无后视镜挂件', '有后视镜挂件'):
                self.result['有无后视镜挂件'] = item['attribute']['vehicle_front_item_pendant']['name']
            else:
                self.result['有无后视镜挂件'] = '未知'
        else:
            self.result['有无后视镜挂件'] = '未知'

        # 车身有无喷字;body_spray	是否车身喷字	车身无喷字、车身有喷字
        if 'body_spray' in item['attribute']:
            if item['attribute']['body_spray']['name'] in ('车身无喷字', '车身有喷字'):
                self.result['车身有无喷字'] = item['attribute']['body_spray']['name']
            else:
                self.result['车身有无喷字'] = '未知'
        else:
            self.result['车身有无喷字'] = '未知'

        # 有无备胎；spare_wheel
        if 'spare_wheel' in item['attribute']:
            if item['attribute']['spare_wheel']['name'] in ('有备胎', '无备胎'):
                self.result['有无备胎'] = item['attribute']['spare_wheel']['name']
            else:
                self.result['有无备胎'] = '未知'
        else:
            self.result['有无备胎'] = '未知'

        # 是否车前有纸巾盒；vehicle_front_item_tissuebox	是否车前有纸巾盒	车前无纸巾盒、车前有纸巾盒
        if 'vehicle_front_item_tissuebox' in item['attribute']:
            if item['attribute']['vehicle_front_item_tissuebox']['name'] in ('车前无纸巾盒', '车前有纸巾盒'):
                self.result['是否车前有纸巾盒'] = item['attribute']['vehicle_front_item_tissuebox']['name']
            else:
                self.result['是否车前有纸巾盒'] = '未知'
        else:
            self.result['是否车前有纸巾盒'] = '未知'

        # 是否有年检标;vehicle_inspection	是否有年检标	无年检标、有年检标
        if 'vehicle_inspection' in item['attribute']:
            if item['attribute']['vehicle_inspection']['name'] in ('无年检标', '有年检标'):
                self.result['是否有年检标'] = item['attribute']['vehicle_inspection']['name']
            else:
                self.result['是否有年检标'] = '未知'
        else:
            self.result['是否有年检标'] = '未知'

        # 车门状态
        if 'door_open' in item['attribute']:
            if item['attribute']['door_open']['name'] in ('车门关闭', '车门打开'):
                self.result['车门状态'] = item['attribute']['door_open']['name']
            else:
                self.result['车门状态'] = '未知'
        else:
            self.result['车门状态'] = '未知'

        # 驾驶员状态
        if 'has_pilot' in item['attribute']:
            if item['attribute']['has_pilot']['name'] in ('有驾驶人', '无驾驶人'):
                self.result['驾驶员状态'] = item['attribute']['has_pilot']['name']
            else:
                self.result['驾驶员状态'] = '未知'
        else:
            self.result['驾驶员状态'] = '未知'

        # 驾驶员是否系安全带;safety_belt_pilot	驾驶员安全带是否系带	驾驶员未系安全带、驾驶员系安全带
        if 'safety_belt_pilot' in item['attribute']:
            if item['attribute']['safety_belt_pilot']['name'] in ('驾驶员未系安全带', '驾驶员系安全带'):
                self.result['驾驶员是否系安全带'] = item['attribute']['safety_belt_pilot']['name']
            else:
                self.result['驾驶员是否系安全带'] = '未知'
        else:
            self.result['驾驶员是否系安全带'] = '未知'

        # 驾驶员遮阳板是否放下;sunvisor_pilot	驾驶员遮阳板是否放下	驾驶员遮阳板未放下、驾驶员遮阳板放下
        if 'sunvisor_pilot' in item['attribute']:
            if item['attribute']['sunvisor_pilot']['name'] in ('驾驶员遮阳板未放下', '驾驶员遮阳板放下'):
                self.result['驾驶员遮阳板是否放下'] = item['attribute']['sunvisor_pilot']['name']
            else:
                self.result['驾驶员遮阳板是否放下'] = '未知'
        else:
            self.result['驾驶员遮阳板是否放下'] = '未知'

        # 驾驶员是否打电话；calling	是否驾驶员打电话	驾驶员未打电话、驾驶员打电话
        if 'calling' in item['attribute']:
            if item['attribute']['calling']['name'] in ('驾驶员未打电话', '驾驶员打电话'):
                self.result['驾驶员是否打电话'] = item['attribute']['calling']['name']
            else:
                self.result['驾驶员是否打电话'] = '未知'
        else:
            self.result['驾驶员是否打电话'] = '未知'

        # 副驾驶是否有人;has_copilot	副驾驶位是否有人	副驾驶无人、副驾驶有人
        if 'has_copilot' in item['attribute']:
            if item['attribute']['has_copilot']['name'] in ('副驾驶无人', '副驾驶有人'):
                self.result['副驾驶是否有人'] = item['attribute']['has_copilot']['name']
            else:
                self.result['副驾驶是否有人'] = '未知'
        else:
            self.result['副驾驶是否有人'] = '未知'

        # 副驾驶是否系安全带;safety_belt_copilot	副驾驶安全带是否系带	副驾驶未系安全带、副驾驶系安全带
        if 'safety_belt_copilot' in item['attribute']:
            if item['attribute']['safety_belt_copilot']['name'] in ('副驾驶未系安全带', '副驾驶系安全带'):
                self.result['副驾驶是否系安全带'] = item['attribute']['safety_belt_copilot']['name']
            else:
                self.result['副驾驶是否系安全带'] = '未知'
        else:
            self.result['副驾驶是否系安全带'] = '未知'

        # 副驾驶员是否打电话,无此属性
        self.result['副驾驶员是否打电话'] = ''

        # 副驾驶员遮阳板状态;sunvisor_copilot	副驾驶遮阳板是否放下	副驾驶遮阳板未放下、副驾驶遮阳板放下
        if 'sunvisor_copilot' in item['attribute']:
            if item['attribute']['sunvisor_copilot']['name'] in ('副驾驶遮阳板未放下', '副驾驶遮阳板放下'):
                self.result['副驾驶员遮阳板状态'] = item['attribute']['sunvisor_copilot']['name']
            else:
                self.result['副驾驶员遮阳板状态'] = '未知'
        else:
            self.result['副驾驶员遮阳板状态'] = '未知'

        # 特殊车辆
        if 'dangerous_vehicle' in item['attribute']:
            if item['attribute']['dangerous_vehicle']['name'] == '危险品车':
                self.result['特殊车辆'] = '危化品车'
        elif 'special_vehicle' in item['attribute']:
            if item['attribute']['special_vehicle']['name'] in ('普通车', '施工工程车', '校车', '搅拌车', '救护车',
                                                                '工程抢险车', '警车', '消防车', '洒水车'):
                self.result['特殊车辆'] = item['attribute']['special_vehicle']['name']
            elif item['attribute']['special_vehicle']['name'] == '施工工程车':
                self.result['特殊车辆'] = '市政工程&环卫&园林车'
        elif 'slag_vehicle' in item['attribute']:
            if item['attribute']['slag_vehicle']['name'] == '渣土车':
                self.result['特殊车辆'] = '渣土车'
        else:
            self.result['特殊车辆'] = '未知'

        # 是否为危化品车;dangerous_vehicle	是否为危化品车  非危险品车、危险品车
        if 'dangerous_vehicle' in item['attribute']:
            if item['attribute']['dangerous_vehicle']['name'] in ('非危险品车', '危险品车'):
                self.result['是否为危化品车'] = item['attribute']['dangerous_vehicle']['name']
            else:
                self.result['是否为危化品车'] = '未知'
        else:
            self.result['是否为危化品车'] = '未知'

        # 是否为渣土车;slag_vehicle	是否为渣土车	非渣土车、渣土车
        if 'slag_vehicle' in item['attribute']:
            if item['attribute']['slag_vehicle']['name'] in ('非渣土车', '渣土车'):
                self.result['是否为渣土车'] = item['attribute']['slag_vehicle']['name']
            else:
                self.result['是否为渣土车'] = '未知'
        else:
            self.result['是否为渣土车'] = '未知'

        # 渣土车改装，slag_refit 渣土车未改装、渣土车改装
        if 'slag_refit' in item['attribute']:
            if item['attribute']['slag_refit']['name'] in ('渣土车未改装', '渣土车改装'):
                self.result['渣土车改装'] = item['attribute']['slag_refit']['name']
            else:
                self.result['渣土车改装'] = '未知'
        else:
            self.result['渣土车改装'] = '未知'

        # 渣土车满载；slag_full_loaded	渣土车满载	渣土车未满载、渣土车满载
        if 'slag_full_loaded' in item['attribute']:
            if item['attribute']['slag_full_loaded']['name'] in ('渣土车未满载', '渣土车满载'):
                self.result['渣土车满载'] = item['attribute']['slag_full_loaded']['name']
            else:
                self.result['渣土车满载'] = '未知'
        else:
            self.result['渣土车满载'] = '未知'

        db.execute_sql(
            f"""update algorithm_precision set {self.version}='{json.dumps(self.result, ensure_ascii=False)}' where id={im_id}""")

    def ele(self, item, im_id):
        # 性别，无此属性
        self.result['性别'] = '未知'

        # 年龄段，无此属性
        self.result['年龄段'] = '未知'

        # 上身纹理，无此属性
        self.result['上身纹理'] = '未知'

        # 上身颜色；pilot_upper_color	骑车人上衣颜色
        if 'pilot_upper_color' in item['attribute']:
            color = item['attribute']['pilot_upper_color']['name'].replace('骑车人上衣颜色', '')
            self.result['上身颜色'] = color
        else:
            self.result['上身颜色'] = '未知'

        # 头部特征
        self.result['头部特征'] = []
        if 'has_helment' in item['attribute']:
            if item['attribute']['has_helment']['name'] == '带头盔':
                self.result['头部特征'].append('头盔')

        # 车身颜色;与car属性一致
        if 'vehicle_color' in item['attribute']:
            vehicle_color = item['attribute']['vehicle_color']['name'].replace('车身颜色', '')
            if vehicle_color in ('红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '棕色', '粉色', '白色', '黑色'):
                self.result['车身颜色'] = vehicle_color
            elif vehicle_color in ('深空灰', '金银色'):
                self.result['车身颜色'] = '灰色'
            else:
                self.result['车身颜色'] = '未知'
        else:
            self.result['车身颜色'] = '未知'

        # 车辆类型;category - desc
        # print(item)
        if item['desc'] in ('摩托车', '电动摩托车', '电动自行车'):
            self.result['车辆类型'] = '摩托车/电瓶车（电动摩托车/电动自行车）'
        elif item['desc'] in ('儿童脚踏车', '手推车', '滑板车', '自行车', '三轮车'):
            self.result['车辆类型'] = item['desc']
        else:
            self.result['车辆类型'] = '未知'

        db.execute_sql(
            f"""update algorithm_precision set {self.version}='{json.dumps(self.result, ensure_ascii=False)}' where id={im_id}""")

    @staticmethod
    def calc_overlap_rate(items, att, im_type):    # 计算与标记坐标重叠率，取重叠最大的
        data = []   # 记录对象信息
        for item in items:
            if im_type == 1:
                if item['type'] == 'face':
                    data.append(item)
            elif im_type == 2:
                if item['type'] == 'human':
                    data.append(item)
            elif im_type == 3:
                if item['type'] == 'car':
                    data.append(item)
            else:
                if item['type'] == 'electric-car':
                    data.append(item)

        if len(data) == 1:
            return data[0]
        elif len(data) > 1:
            att = json.loads(att)
            location = att['location']
            cross_area = {}
            for table in range(len(data)):
                min_x = min(int(location[0][0]), data[table]['location']['left'])
                min_y = min(int(location[0][1]), data[table]['location']['top'])
                max_x = max(int(location[1][0]), data[table]['location']['left']+data[table]['location']['width'])
                max_y = max(int(location[1][1]), data[table]['location']['top']+data[table]['location']['height'])

                cross_x = location[1][0]-location[0][0] + data[table]['location']['width'] - (max_x-min_x)
                cross_y = location[1][1]-location[0][1] + data[table]['location']['height'] - (max_y-min_y)

                if cross_y < 0 or cross_y < 0:
                    continue
                else:
                    cross_area[table] = cross_x * cross_y
        else:
            return False

            max_key = 0
            max_value = 0
            for key, value in cross_area.items():
                if value > max_value:
                    max_value = value
                    max_key = key
            print(max_key, data)
            return data[max_key]


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

    def contrast(self, version, is_draw=0):  # is_draw判断是否标记图片，1标记，0不标记
        data = db.execute_sql(
            f"""select id, file_path, attribute, {version}, type, day from algorithm_precision 
            where id>14221""")

        for im_id, image, att, result, im_type, day in data:
            att = json.loads(att)['attribute']
            result = json.loads(result)

            for key, value in att.items():

                if is_draw == 1:
                    self.draw_picture(image, result['location'], version)

                if key in ('时间段', 'location'):
                    continue

                if value == '':
                    value = '未知'
                if not value:
                    value.append('未知')

                if im_type == 1:
                    # print(im_id)
                    if key == '帽子':
                        continue
                    elif att[key] == result[key]:
                        self.true['face'][day][key][value] += 1
                    else:
                        self.false['face'][day][key][value] += 1
                        self.false_id['face'].append(f"{key}{im_id}")
                elif im_type == 2:
                    # print(im_id, key, value)
                    if key == '随身物品':
                        for item in value:
                            if item in result[key]:
                                self.true['human'][day][key][item] += 1
                            else:
                                self.false['human'][day][key][item] += 1
                                self.false_id['human'].append(f"{key}{im_id}")

                    elif key == '行为':
                        if value in ('看手机', '未使用手机', '打手机'):
                            if result['是否用手机'] == value:
                                self.true['human'][day]['是否用手机'][value] += 1
                            else:
                                self.false['human'][day]['是否用手机'][value] += 1
                                self.false_id['human'].append(f"{'是否用手机'}{im_id}")

                        elif value in ('未吸烟', '吸烟'):
                            if value == result['是否吸烟']:
                                self.true['human'][day]['是否吸烟'][value] += 1
                            else:
                                self.false['human'][day]['是否吸烟'][value] += 1
                                self.false_id['human'].append(f"{'是否吸烟'}{im_id}")

                    elif att[key] == result[key]:

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
                            if item in result[key]:
                                self.true['car'][day][key][item] += 1
                            else:
                                self.false['car'][day][key][item] += 1
                                self.false_id['human'].append(f"{'车牌状态'}{im_id}")
                    elif key == '车牌号码':
                        if value == result[key]:
                            self.true['car'][day]['车牌号码'] += 1
                        else:
                            self.false['car'][day]['车牌号码'] += 1
                            self.false_id['human'].append(f"{'车牌号码'}{im_id}")
                    elif att[key] == result[key]:
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
                            if item in result[key]:
                                self.true['ele-car'][day][key][item] += 1
                            else:
                                self.false['ele-car'][day][key][item] += 1
                                self.false_id['ele-car'].append(f"{key}{im_id}")

                    elif att[key] == result[key]:

                        self.true['ele-car'][day][key][value] += 1
                    else:
                        self.false['ele-car'][day][key][value] += 1
                        self.false_id['ele-car'].append(f"{key}{im_id}")

        return self.true, self.false, self.false_id

    @staticmethod
    def draw_picture(image, location, version):
        location = ((location['left'], location['top']),
                    (location['left']+location['width'], location['top']+location['height']))
        draw_rectangle(image, location, version)


# 标记图片
class Target:

    def __init__(self, url):
        self.url = url

    def target(self):

        # 查询所有本次算法需要的数据
        data = db.execute_sql(f"""select id, attribute, file_path, type from algorithm_precision 
        where type=4""")

        baidu = BaiduAi(config["sdk"]["DianJun"]["user"],
                        config["sdk"]["DianJun"]["password"],
                        config["sdk"]["DianJun"]["url"])

        for num in range(1):  # 控制循环5次，防止网络问题导致的失败
            # 判断是否有未处理过的图片，无直接结束循环
            if not data:
                break
            else:
                for im_id, att, image, im_type in data:

                    # att = json.loads(att)
                    # print(f'标记属性:{att["车辆类型"]}')

                    point = {}  # 记录坐标
                    # image = '/Users/sunzhaohui/Desktop/SensoroTestData/算法对比测试集/非机动车/111.jpeg'
                    try:
                        response = baidu.base_detect(
                            self.url, image, "filepath", enable_multiple=True)
                    except Exception as e:
                        # raise e
                        print(e, "服务异常，重新执行！")
                        continue
                    # print(response)
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
                                        # print(point)
                                        draw_rectangle(image, point)  # 对图像标记并将新文件位置保存至数据库

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
    # WholeTarget('/v1/whole/target/detect', version='v1').whole_target()
    # WholeTarget('/v2/whole/target/detect', version='v2').whole_target()

    # v1_true, v1_false, v1_false_id = Contrast().contrast(version='v1', is_draw=1)
    # v2_true, v2_false, v2_false_id = Contrast().contrast(version='v2', is_draw=1)

    # print_result(v1_true, v1_false, v2_true, v2_false)

    # 取v1正确，v2错误的数据
    # v_false(v1_false_id, v2_false_id)

    data = db.execute_sql(f"""
        select id, file_path from algorithm_precision 
        where (v1 is null or v2 is null) and delete_time is null and type=1""")
    # print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )

    for im_id, file in data:
        # print(file)
        print(os.path.split(file)[1])

    db.close()


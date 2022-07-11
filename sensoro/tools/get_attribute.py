#!/usr/env/bin/python3
# -*- coding:utf-8
"""
1、调用全目标检测算子并返回人脸、人体、机动车、非机动车属性内容
2、一张图仅有一个对象时适用
"""


class GetAttribute:
    result = {'location': [], 'attribute': {}}  # 记录属性及坐标内容

    def get_attribute(self, obj_type, data) -> dict:
        """

        :param obj_type: 对象类型，human、face、car、ele-car
        :param data: 百度全目标算法返回结果
        :return: result['attribute']，返回处理后的属性及坐标内容
        """
        print(data)
        try:
            self.result['location'] = data['location']
            self.result['attribute']['时间段'] = '白天'

            if obj_type == 'face':
                self.face(data)
            elif obj_type == 'human':
                self.human(data)
            elif obj_type == 'car':
                self.car(data)
            elif obj_type == 'ele-car':
                self.ele(data)
        except Exception as e:
            raise e

        return self.result

    def face(self, item):
        self.result['attribute']['帽子'] = '未知'

        if item['gender']['name'] == 'male':
            self.result['attribute']['性别'] = '男'
        elif item['gender']['name'] == 'female':
            self.result['attribute']['性别'] = '女'
        else:
            self.result['attribute']['性别'] = '未知'

        if item['glasses']['name'] == 'common':
            self.result['attribute']['眼镜'] = '戴普通眼镜'
        elif item['glasses']['name'] == 'sun':
            self.result['attribute']['眼镜'] = '戴墨镜'
        elif item['glasses']['name'] == 'none':
            self.result['attribute']['眼镜'] = '未戴眼镜'
        else:
            self.result['attribute']['眼镜'] = '未知'

        if item['age'] <= 6:
            self.result['attribute']['年龄段'] = '小孩'
        elif 7 < item['age'] <= 40:
            self.result['attribute']['年龄段'] = '青年'
        elif 40 < item['age'] <= 60:
            self.result['attribute']['年龄段'] = '中年'
        elif item['age'] > 60:
            self.result['attribute']['年龄段'] = '老年'
        else:
            self.result['attribute']['年龄段'] = '未知'

        if item['mask']['name'] == '1':
            self.result['attribute']['佩戴口罩'] = '佩戴口罩'
        elif item['mask']['name'] == '0':
            self.result['attribute']['佩戴口罩'] = '未戴口罩'
        else:
            self.result['attribute']['佩戴口罩'] = '未知'

    def human(self, item):
        # 帽子
        if item['attribute']['headwear']['name'] == '无帽':
            self.result['attribute']['帽子'] = '未戴帽子'
        elif item['attribute']['headwear']['name'] == '普通帽':
            self.result['attribute']['帽子'] = '戴普通帽子'
        elif item['attribute']['headwear']['name'] == '安全帽':
            self.result['attribute']['帽子'] = '戴安全帽子'
        else:
            self.result['attribute']['帽子'] = '未知'

        # 性别
        if item['attribute']['gender']['name'] == '男性':
            self.result['attribute']['性别'] = '男'
        elif item['attribute']['gender']['name'] == '女性':
            self.result['attribute']['性别'] = '女'
        else:
            self.result['attribute']['性别'] = '未知'

        # 眼镜
        if item['attribute']['glasses']['name'] == '戴眼镜':
            self.result['attribute']['眼镜'] = '戴普通眼镜'
        elif item['attribute']['glasses']['name'] == '戴墨镜':
            self.result['attribute']['眼镜'] = '戴墨镜'
        elif item['attribute']['glasses']['name'] == '无眼镜':
            self.result['attribute']['眼镜'] = '未戴眼镜'
        else:
            self.result['attribute']['眼镜'] = '未知'

        if item['attribute']['age']['name'] == '幼儿':
            self.result['attribute']['年龄段'] = '小孩'
        elif item['attribute']['age']['name'] in ('青少年', '青年'):
            self.result['attribute']['年龄段'] = '青年'
        elif item['attribute']['age']['name'] == '中年':
            self.result['attribute']['年龄段'] = '中年'
        elif item['attribute']['age']['name'] == '老年':
            self.result['attribute']['年龄段'] = '老年'
        else:
            self.result['attribute']['年龄段'] = '未知'

        if item['attribute']['upper_wear_texture']['name'] in ('纯色', '图案', '条纹', '格子'):
            self.result['attribute']['上身纹理'] = item['attribute']['upper_wear_texture']['name']
        elif item['attribute']['upper_wear_texture']['name'] == '碎花':
            self.result['attribute']['上身纹理'] = '花纹'
        elif item['attribute']['upper_wear_texture']['name'] == '条纹或格子':
            self.result['attribute']['上身纹理'] = '格子'
        else:
            self.result['attribute']['上身纹理'] = '未知'

        # 上身颜色
        if item['attribute']['upper_color']['name'] in ('红', '橙', '黄', '绿', '蓝', '紫', '粉', '黑', '白', '灰', '棕'):
            self.result['attribute']['上身颜色'] = f"{item['attribute']['upper_color']['name']}色"
        else:
            self.result['attribute']['上身颜色'] = '未知'

        if item['attribute']['lower_wear']['name'] == '不确定':
            self.result['attribute']['下身类别'] = '未知'
        else:
            self.result['attribute']['下身类别'] = item['attribute']['lower_wear']['name']

        if item['attribute']['upper_color']['name'] in ('红', '橙', '黄', '绿', '蓝', '紫', '粉', '黑', '白', '灰', '棕'):
            self.result['attribute']['下身颜色'] = f"{item['attribute']['lower_color']['name']}色"
        else:
            self.result['attribute']['下身颜色'] = '未知'

        if item['attribute']['orientation']['name'] in ('正面', '背面', '左侧面', '右侧面'):
            self.result['attribute']['人体朝向'] = item['attribute']['orientation']['name']
        else:
            self.result['attribute']['人体朝向'] = '未知'

        if item['attribute']['face_mask']['name'] == '戴口罩':
            self.result['attribute']['佩戴口罩'] = '佩戴口罩'
        elif item['attribute']['face_mask']['name'] == '无口罩':
            self.result['attribute']['佩戴口罩'] = '未戴口罩'
        else:
            self.result['attribute']['佩戴口罩'] = '未知'

        if item['attribute']['action']['name'] in ('站立', '蹲或坐', '走', '跑'):
            self.result['attribute']['动作姿态'] = item['attribute']['action']['name']
        else:
            self.result['attribute']['动作姿态'] = '未知'

        # 是否吸烟
        if item['attribute']['smoke']['name'] in ('吸烟', '未吸烟'):
            self.result['attribute']['是否吸烟'] = item['attribute']['smoke']['name']
        else:
            self.result['attribute']['是否吸烟'] = '未知'

        self.result['attribute']['随身物品'] = []
        if item['attribute']['carrying_baby']['name'] == '抱小孩':
            self.result['attribute']['随身物品'].append('抱小孩')
        if item['attribute']['bag']['name'] == '单肩包':
            self.result['attribute']['随身物品'].append('单肩包或斜挎包')
        elif item['attribute']['bag']['name'] == '双肩包':
            self.result['attribute']['随身物品'].append('双肩包')
        if item['attribute']['umbrella']['name'] == '打伞':
            self.result['attribute']['随身物品'].append('打伞')
        if item['attribute']['carrying_item']['name'] == '有手提物':
            self.result['attribute']['随身物品'].append('拎物品')
        if item['attribute']['luggage']['name'] == '有拉杆箱':
            self.result['attribute']['随身物品'].append('行李箱')

        if item['attribute']['cellphone']['name'] in ('未使用手机', '看手机'):
            self.result['attribute']['是否用手机'] = item['attribute']['cellphone']['name']
        elif item['attribute']['cellphone']['name'] == '打电话':
            self.result['attribute']['是否用手机'] = '打手机'
        else:
            self.result['attribute']['是否用手机'] = '未知'
            
    def car(self, item):
        # 车牌号码
        if 'plate' in item:
            self.result['attribute']['车牌号码'] = item['plate']['plate_number']
        else:
            self.result['attribute']['车牌号码'] = '未知'

        # 是否有车牌
        if 'has_plate' in item['attribute']:
            if item['attribute']['has_plate']['name'] == '有车牌':
                self.result['attribute']['是否有车牌'] = '有车牌号码'
            elif item['attribute']['has_plate']['name'] == '无车牌':
                self.result['attribute']['是否有车牌'] = '无车牌'
            else:
                self.result['attribute']['是否有车牌'] = '未知'
        else:
            self.result['attribute']['是否有车牌'] = '未知'

        # 车牌颜色
        if 'plate' in item:
            if item['plate']['plate_color'] == 'blue':
                self.result['attribute']['车牌颜色'] = '蓝色'
            elif item['plate']['plate_color'] == 'yellow':
                self.result['attribute']['车牌颜色'] = '黄色'
            elif item['plate']['plate_color'] == 'white':
                self.result['attribute']['车牌颜色'] = '白色'
            else:
                self.result['attribute']['车牌颜色'] = '未知'
        else:
            self.result['attribute']['车牌颜色'] = '未知'

        # 车牌状态
        self.result['attribute']['车牌状态'] = []
        if 'plate_cover' in item['attribute']:
            self.result['attribute']['车牌状态'].append(item['attribute']['plate_cover']['name'])
            self.result['attribute']['车牌状态'].append(item['attribute']['has_plate']['name'])
            self.result['attribute']['车牌状态'].append(item['attribute']['plate_stained']['name'])

        # 机动车品牌
        if 'model' in item:
            self.result['attribute']['机动车品牌'] = item['model']['brand']
        else:
            self.result['attribute']['机动车品牌'] = '未知'

        # 机动车类型；百度无此字段，取特殊车辆统计
        self.result['attribute']['机动车类型'] = '未知'

        # 车身颜色
        if 'vehicle_color' in item['attribute']:
            vehicle_color = item['attribute']['vehicle_color']['name'].replace('车身颜色', '')
            if vehicle_color in ('红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '棕色', '粉色', '白色', '黑色'):
                self.result['attribute']['车身颜色'] = vehicle_color
            elif vehicle_color == '深空灰':
                self.result['attribute']['车身颜色'] = '灰色'
            elif vehicle_color == '金银色':
                self.result['attribute']['车身颜色'] = '银色'
            else:
                self.result['attribute']['车身颜色'] = '未知'
        else:
            self.result['attribute']['车身颜色'] = '未知'

        # 车辆朝向
        if 'motor_direction' in item['attribute']:
            if item['attribute']['motor_direction']['name'] in ('车辆朝向正向', '车辆朝向背向', '车辆朝向左向', '车辆朝向右向'):
                self.result['attribute']['车辆朝向'] = item['attribute']['motor_direction']['name']
            else:
                self.result['attribute']['车辆朝向'] = '未知'
        else:
            self.result['attribute']['车辆朝向'] = '未知'

        # 车辆行驶方向；direction	车辆行驶方向	车辆正向行驶、车辆背向行驶、车辆左侧行驶、车辆右侧行驶
        if 'direction' in item['attribute']:
            if item['attribute']['direction']['name'] in ('车辆正向行驶', '车辆背向行驶', '车辆左侧行驶', '车辆右侧行驶'):
                self.result['attribute']['车辆行驶方向'] = item['attribute']['direction']['name']
            else:
                self.result['attribute']['车辆行驶方向'] = '未知'
        else:
            self.result['attribute']['车辆行驶方向'] = '未知'

        # 车顶架状态；top_holder	是否有车顶架	无车顶架、有车顶架
        if 'top_holder' in item['attribute']:
            if item['attribute']['top_holder']['name'] in ('无车顶架', '有车顶架'):
                self.result['attribute']['车顶架状态'] = item['attribute']['top_holder']['name']
            else:
                self.result['attribute']['车顶架状态'] = '未知'
        else:
            self.result['attribute']['车顶架状态'] = '未知'

        # 天窗状态；skylight
        if 'skylight' in item['attribute']:
            if item['attribute']['skylight']['name'] in ('有天窗', '无天窗'):
                self.result['attribute']['天窗状态'] = item['attribute']['skylight']['name']
            else:
                self.result['attribute']['天窗状态'] = '未知'
        else:
            self.result['attribute']['天窗状态'] = '未知'

        # 车窗雨眉
        if 'window_rain_eyebrow' in item['attribute']:
            if item['attribute']['window_rain_eyebrow']['name'] in ('有车窗雨眉', '无车窗雨眉'):
                self.result['attribute']['车窗雨眉'] = item['attribute']['window_rain_eyebrow']['name']
            else:
                self.result['attribute']['车窗雨眉'] = '未知'
        else:
            self.result['attribute']['车窗雨眉'] = '未知'

        # 车前摆放物；vehicle_front_item_placeitems	是否有车前摆放物	无车前摆放物、有车前摆放物
        if 'vehicle_front_item_placeitems' in item['attribute']:
            if item['attribute']['vehicle_front_item_placeitems']['name'] in ('无车前摆放物', '有车前摆放物'):
                self.result['attribute']['车前摆放物'] = item['attribute']['vehicle_front_item_placeitems']['name']
            else:
                self.result['attribute']['车前摆放物'] = '未知'
        else:
            self.result['attribute']['车前摆放物'] = '未知'

        # 有无后视镜挂件;vehicle_front_item_pendant	是否有后视镜挂件	无后视镜挂件、有后视镜挂件
        if 'vehicle_front_item_pendant' in item['attribute']:
            if item['attribute']['vehicle_front_item_pendant']['name'] in ('无后视镜挂件', '有后视镜挂件'):
                self.result['attribute']['有无后视镜挂件'] = item['attribute']['vehicle_front_item_pendant']['name']
            else:
                self.result['attribute']['有无后视镜挂件'] = '未知'
        else:
            self.result['attribute']['有无后视镜挂件'] = '未知'

        # 车身有无喷字;body_spray	是否车身喷字	车身无喷字、车身有喷字
        if 'body_spray' in item['attribute']:
            if item['attribute']['body_spray']['name'] in ('车身无喷字', '车身有喷字'):
                self.result['attribute']['车身有无喷字'] = item['attribute']['body_spray']['name']
            else:
                self.result['attribute']['车身有无喷字'] = '未知'
        else:
            self.result['attribute']['车身有无喷字'] = '未知'

        # 有无备胎；spare_wheel
        if 'spare_wheel' in item['attribute']:
            if item['attribute']['spare_wheel']['name'] in ('有备胎', '无备胎'):
                self.result['attribute']['有无备胎'] = item['attribute']['spare_wheel']['name']
            else:
                self.result['attribute']['有无备胎'] = '未知'
        else:
            self.result['attribute']['有无备胎'] = '未知'

        # 是否车前有纸巾盒；vehicle_front_item_tissuebox	是否车前有纸巾盒	车前无纸巾盒、车前有纸巾盒
        if 'vehicle_front_item_tissuebox' in item['attribute']:
            if item['attribute']['vehicle_front_item_tissuebox']['name'] in ('车前无纸巾盒', '车前有纸巾盒'):
                self.result['attribute']['是否车前有纸巾盒'] = item['attribute']['vehicle_front_item_tissuebox']['name']
            else:
                self.result['attribute']['是否车前有纸巾盒'] = '未知'
        else:
            self.result['attribute']['是否车前有纸巾盒'] = '未知'

        # 是否有年检标;vehicle_inspection	是否有年检标	无年检标、有年检标
        if 'vehicle_inspection' in item['attribute']:
            if item['attribute']['vehicle_inspection']['name'] in ('无年检标', '有年检标'):
                self.result['attribute']['是否有年检标'] = item['attribute']['vehicle_inspection']['name']
            else:
                self.result['attribute']['是否有年检标'] = '未知'
        else:
            self.result['attribute']['是否有年检标'] = '未知'

        # 车门状态
        if 'door_open' in item['attribute']:
            if item['attribute']['door_open']['name'] in ('车门关闭', '车门打开'):
                self.result['attribute']['车门状态'] = item['attribute']['door_open']['name']
            else:
                self.result['attribute']['车门状态'] = '未知'
        else:
            self.result['attribute']['车门状态'] = '未知'

        # 驾驶员状态
        if 'has_pilot' in item['attribute']:
            if item['attribute']['has_pilot']['name'] in ('有驾驶人', '无驾驶人'):
                self.result['attribute']['驾驶员状态'] = item['attribute']['has_pilot']['name']
            else:
                self.result['attribute']['驾驶员状态'] = '未知'
        else:
            self.result['attribute']['驾驶员状态'] = '未知'

        # 驾驶员是否系安全带;safety_belt_pilot	驾驶员安全带是否系带	驾驶员未系安全带、驾驶员系安全带
        if 'safety_belt_pilot' in item['attribute']:
            if item['attribute']['safety_belt_pilot']['name'] in ('驾驶员未系安全带', '驾驶员系安全带'):
                self.result['attribute']['驾驶员是否系安全带'] = item['attribute']['safety_belt_pilot']['name']
            else:
                self.result['attribute']['驾驶员是否系安全带'] = '未知'
        else:
            self.result['attribute']['驾驶员是否系安全带'] = '未知'

        # 驾驶员遮阳板是否放下;sunvisor_pilot	驾驶员遮阳板是否放下	驾驶员遮阳板未放下、驾驶员遮阳板放下
        if 'sunvisor_pilot' in item['attribute']:
            if item['attribute']['sunvisor_pilot']['name'] in ('驾驶员遮阳板未放下', '驾驶员遮阳板放下'):
                self.result['attribute']['驾驶员遮阳板是否放下'] = item['attribute']['sunvisor_pilot']['name']
            else:
                self.result['attribute']['驾驶员遮阳板是否放下'] = '未知'
        else:
            self.result['attribute']['驾驶员遮阳板是否放下'] = '未知'

        # 驾驶员是否打电话；calling	是否驾驶员打电话	驾驶员未打电话、驾驶员打电话
        if 'calling' in item['attribute']:
            if item['attribute']['calling']['name'] in ('驾驶员未打电话', '驾驶员打电话'):
                self.result['attribute']['驾驶员是否打电话'] = item['attribute']['calling']['name']
            else:
                self.result['attribute']['驾驶员是否打电话'] = '未知'
        else:
            self.result['attribute']['驾驶员是否打电话'] = '未知'

        # 副驾驶是否有人;has_copilot	副驾驶位是否有人	副驾驶无人、副驾驶有人
        if 'has_copilot' in item['attribute']:
            if item['attribute']['has_copilot']['name'] in ('副驾驶无人', '副驾驶有人'):
                self.result['attribute']['副驾驶是否有人'] = item['attribute']['has_copilot']['name']
            else:
                self.result['attribute']['副驾驶是否有人'] = '未知'
        else:
            self.result['attribute']['副驾驶是否有人'] = '未知'

        # 副驾驶是否系安全带;safety_belt_copilot	副驾驶安全带是否系带	副驾驶未系安全带、副驾驶系安全带
        if 'safety_belt_copilot' in item['attribute']:
            if item['attribute']['safety_belt_copilot']['name'] in ('副驾驶未系安全带', '副驾驶系安全带'):
                self.result['attribute']['副驾驶是否系安全带'] = item['attribute']['safety_belt_copilot']['name']
            else:
                self.result['attribute']['副驾驶是否系安全带'] = '未知'
        else:
            self.result['attribute']['副驾驶是否系安全带'] = '未知'

        # 副驾驶员是否打电话,无此属性
        self.result['attribute']['副驾驶员是否打电话'] = ''

        # 副驾驶员遮阳板状态;sunvisor_copilot	副驾驶遮阳板是否放下	副驾驶遮阳板未放下、副驾驶遮阳板放下
        if 'sunvisor_copilot' in item['attribute']:
            if item['attribute']['sunvisor_copilot']['name'] in ('副驾驶遮阳板未放下', '副驾驶遮阳板放下'):
                self.result['attribute']['副驾驶员遮阳板状态'] = item['attribute']['sunvisor_copilot']['name']
            else:
                self.result['attribute']['副驾驶员遮阳板状态'] = '未知'
        else:
            self.result['attribute']['副驾驶员遮阳板状态'] = '未知'

        # 特殊车辆
        if 'dangerous_vehicle' in item['attribute']:
            if item['attribute']['dangerous_vehicle']['name'] == '危险品车':
                self.result['attribute']['特殊车辆'] = '危化品车'
        elif 'special_vehicle' in item['attribute']:
            if item['attribute']['special_vehicle']['name'] in ('普通车', '施工工程车', '校车', '搅拌车', '救护车',
                                                                '工程抢险车', '警车', '消防车', '洒水车'):
                self.result['attribute']['特殊车辆'] = item['attribute']['special_vehicle']['name']
            elif item['attribute']['special_vehicle']['name'] == '施工工程车':
                self.result['attribute']['特殊车辆'] = '市政工程&环卫&园林车'
        elif 'slag_vehicle' in item['attribute']:
            if item['attribute']['slag_vehicle']['name'] == '渣土车':
                self.result['attribute']['特殊车辆'] = '渣土车'
        else:
            self.result['attribute']['特殊车辆'] = '未知'
        if '特殊车辆' not in self.result['attribute'].keys():
            self.result['attribute']['特殊车辆'] = '未知'

        # 是否为危化品车;dangerous_vehicle	是否为危化品车  非危险品车、危险品车
        if 'dangerous_vehicle' in item['attribute']:
            if item['attribute']['dangerous_vehicle']['name'] in ('非危险品车', '危险品车'):
                self.result['attribute']['是否为危化品车'] = item['attribute']['dangerous_vehicle']['name']
            else:
                self.result['attribute']['是否为危化品车'] = '未知'
        else:
            self.result['attribute']['是否为危化品车'] = '未知'

        # 是否为渣土车;slag_vehicle	是否为渣土车	非渣土车、渣土车
        if 'slag_vehicle' in item['attribute']:
            if item['attribute']['slag_vehicle']['name'] in ('非渣土车', '渣土车'):
                self.result['attribute']['是否为渣土车'] = item['attribute']['slag_vehicle']['name']
            else:
                self.result['attribute']['是否为渣土车'] = '未知'
        else:
            self.result['attribute']['是否为渣土车'] = '未知'

        # 渣土车改装，slag_refit 渣土车未改装、渣土车改装
        if 'slag_refit' in item['attribute']:
            if item['attribute']['slag_refit']['name'] in ('渣土车未改装', '渣土车改装'):
                self.result['attribute']['渣土车改装'] = item['attribute']['slag_refit']['name']
            else:
                self.result['attribute']['渣土车改装'] = '未知'
        else:
            self.result['attribute']['渣土车改装'] = '未知'

        # 渣土车满载；slag_full_loaded	渣土车满载	渣土车未满载、渣土车满载
        if 'slag_full_loaded' in item['attribute']:
            if item['attribute']['slag_full_loaded']['name'] in ('渣土车未满载', '渣土车满载'):
                self.result['attribute']['渣土车满载'] = item['attribute']['slag_full_loaded']['name']
            else:
                self.result['attribute']['渣土车满载'] = '未知'
        else:
            self.result['attribute']['渣土车满载'] = '未知'

    def ele(self, item):
        # 性别，无此属性
        self.result['attribute']['性别'] = '未知'

        # 年龄段，无此属性
        self.result['attribute']['年龄段'] = '未知'

        # 上身纹理，无此属性
        self.result['attribute']['上身纹理'] = '未知'

        # 上身颜色；pilot_upper_color	骑车人上衣颜色
        if 'pilot_upper_color' in item['attribute']:
            color = item['attribute']['pilot_upper_color']['name'].replace('骑车人上衣颜色', '')
            self.result['attribute']['上身颜色'] = color
        else:
            self.result['attribute']['上身颜色'] = '未知'

        # 头部特征
        self.result['attribute']['头部特征'] = []
        if 'has_helment' in item['attribute']:
            if item['attribute']['has_helment']['name'] == '带头盔':
                self.result['attribute']['头部特征'].append('头盔')

        # 车身颜色;与car属性一致
        if 'vehicle_color' in item['attribute']:
            vehicle_color = item['attribute']['vehicle_color']['name'].replace('车身颜色', '')
            if vehicle_color in ('红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '棕色', '粉色', '白色', '黑色'):
                self.result['attribute']['车身颜色'] = vehicle_color
            elif vehicle_color in ('深空灰', '金银色'):
                self.result['attribute']['车身颜色'] = '灰色'
            else:
                self.result['attribute']['车身颜色'] = '未知'
        else:
            self.result['attribute']['车身颜色'] = '未知'

        # 车辆类型;category - desc
        # print(item)
        if item['desc'] in ('摩托车', '电动摩托车', '电动自行车'):
            self.result['attribute']['车辆类型'] = '摩托车/电瓶车（电动摩托车/电动自行车）'
        elif item['desc'] in ('儿童脚踏车', '手推车', '滑板车', '自行车', '三轮车'):
            self.result['attribute']['车辆类型'] = item['desc']
        else:
            self.result['attribute']['车辆类型'] = '未知'

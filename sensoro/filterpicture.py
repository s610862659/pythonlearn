import os
from shutil import copy
import time


# 复制文件修改时间会变化，导致很难判断重复数据
def move_file(path, file_path_list):
    for file_list in file_path_list:
        file_path = path + '/' + file_list

        # 新建4个文件夹
        new_path_RL = file_path+'/RL'
        os.mkdir(new_path_RL)

        new_path_RT = file_path + '/RT'
        os.mkdir(new_path_RT)

        new_path_MO = file_path + '/MO'
        os.mkdir(new_path_MO)

        new_path_NM = file_path + '/NM'
        os.mkdir(new_path_NM)

        # 用来相同时间时命名曲风
        # 0-RL：人脸, 1-RT：人体, 2-MO：机动车, 3-NM：非机动车，
        num = [0, 0, 0, 0]

        # 用来判断存在相同时间文件
        # 0-RL：人脸, 1-RT：人体, 2-MO：机动车, 3-NM：非机动车，
        time_num = [[], [], [], []]

        # 判断文件夹是否存在
        if os.path.exists(file_path):
            path_list = os.listdir(file_path)

            for each_file in path_list:
                # 获取文件修改时间，并截取时分秒为字符串，用来给文件命名
                updatem_time = ''.join(
                            ((time.ctime(os.path.getmtime(file_path+'/'+each_file))).split(' ')[3]).split(':'))
                if 'PROFILE' in each_file:
                    # NM：非机动车，MO：机动车，RT：人体，RL：人脸
                    # 取人脸大图
                    if 'RL' in each_file:

                        if updatem_time not in time_num[0]:
                            time_num[0].append(updatem_time)
                            copy(file_path + '/' + each_file, new_path_RL+'/'+updatem_time+'.jpg')
                        else:
                            copy(file_path + '/' + each_file, new_path_RL + '/' + updatem_time+str(num[0]) + '.jpg')
                            num[0] += 1

                    # 取人体大图
                    elif 'RT' in each_file:

                        if updatem_time not in time_num[1]:
                            time_num[1].append(updatem_time)
                            copy(file_path + '/' + each_file, new_path_RT + '/' + updatem_time + '.jpg')
                        else:
                            copy(file_path + '/' + each_file,
                                 new_path_RL + '/' + updatem_time + str(num[1]) + '.jpg')
                            num[1] += 1

                    # 取机动车大图
                    elif 'MO' in each_file:

                        if updatem_time not in time_num[2]:
                            time_num[2].append(updatem_time)
                            copy(file_path + '/' + each_file, new_path_MO + '/' + updatem_time + '.jpg')
                        else:
                            copy(file_path + '/' + each_file,
                                 new_path_RL + '/' + updatem_time + str(num[2]) + '.jpg')
                            num[2] += 1

                    # 非机动车大图
                    elif 'NM' in each_file:

                        if updatem_time not in time_num[3]:
                            time_num[3].append(updatem_time)
                            copy(file_path + '/' + each_file, new_path_NM + '/' + updatem_time + '.jpg')
                        else:
                            copy(file_path + '/' + each_file,
                                 new_path_RL + '/' + updatem_time + str(num[3]) + '.jpg')
                            num[3] += 1

        else:
            print('%s 文件不存在' % file_path)


if __name__ == '__main__':
    old_path = '/Users/sunzhaohui/Desktop'
    file_name_list = ['泰和世家篮球场', '3号楼东侧小广场', '2号楼旁停车棚往3号楼方向','2号楼旁停车棚往1号楼方向', '1号楼2单元左侧朝停车库方向', '大门口垃圾分类投放点']
    # file_name_list = ['2号楼旁停车棚往3号楼方向']
    # NM：非机动车，MO：机动车，RT：人体，RL：人脸
    move_file(old_path, file_name_list)
    # del_file(old_path, file_name_list)
    # rename_file(old_path, file_name_list)



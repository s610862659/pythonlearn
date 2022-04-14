# coding=utf-8
import os
import ffmpeg


def frame_video():
    filename = []
    while True:
        # '/Users/sunzhaohui/Desktop/升哲测试数据/视频抽帧/茶花基地牌坊'
        input_file = input("请输入视频文件目录：")

        if not os.path.exists(input_file):
            print("视频目录不存在！")
            continue

        save_file = input("请输入图片输出目录：")
        if not os.path.exists(save_file):
            os.makedirs(save_file)

        time_start = input("开始抽帧时间(mm:ss):")

        time_input = input("请输入间隔时间:")

        file_list = list(os.walk(input_file))[0][2]
        for file in file_list:
            if file.split('.')[1] == 'ts':
                frame = f"ffmpeg -ss {time_start} -i {input_file}/{file} -f image2 -vf " \
                        f"fps=fps=1/{time_input} {save_file}/{file.split('.')[0]}_%d.png"
                os.system(frame)
        result = input('视频处理完成！是否继续操作？(y/n)')
        if result == 'y':
            continue
        else:
            print('bye！')
            break


if __name__ == '__main__':
    frame_video()



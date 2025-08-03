# -*- coding: utf-8 -*-
# @Author  : Virace
# @Email   : Virace@aliyun.com
# @Site    : x-item.com
# @Software: Pycharm
# @Create  : 2025/4/26 3:12
# @Update  : 2025/4/26 3:13
# @Detail  : 

# 文件头标记
HEADER_SIGNATURE = b'PROP'

# 主要结构类型哈希
SKIN_AUDIO_PROPERTIES = 0x8F7B194F  # 皮肤音频属性
MUSIC = 0x9f9c4fd4  # 音乐结构标记
MUSIC_AUDIO_DATA_PROPERTIES = 0x6630947b  # 音乐音频数据属性
THEME_MUSIC = 0x53ad3c01  # 主题音乐标记(皮肤文件特有)

# 银行单元相关标记
BANK_UNITS_SIGNATURE = [0x92, 0x9F, 0xF2, 0xF8]  # 银行单元集合标记
BANK_UNIT_SIGNATURE = 0xA4416515  # 银行单元标记

# 字段标记
NAME_SIGNATURE = 0x8D39BDE6  # 名称标记
BANK_PATH_SIGNATURE = 0x2A21AD00  # 银行路径标记
EVENTS_SIGNATURE = 0x12D8E384  # 事件标记
VOICE_OVER_SIGNATURE = 0x3B13AA4B  # 语音覆盖标记
ASYNCHRONE_SIGNATURE = 0xA8A558FF
TAG_EVENT_LIST = 0xD65BAC4D  # 标签事件列表

# 音乐结构字段哈希
THEME_MUSIC_ID = 0xEDA78F54  # 主题音乐ID
THEME_MUSIC_TRANSITION_ID = 0x8CD28ECB  # 主题音乐过渡ID
LEGACY_THEME_MUSIC_ID = 0xECC0E697  # 传统主题音乐ID
LEGACY_THEME_MUSIC_TRANSITION_ID = 0x4FD5971C  # 传统主题音乐过渡ID
VICTORY_MUSIC_ID = 0xD25DA809  # 胜利音乐ID
DEFEAT_MUSIC_ID = 0x47F3FB40  # 失败音乐ID
VICTORY_BANNER_SOUND = 0x73F9C3E6  # 胜利横幅音效
DEFEAT_BANNER_SOUND = 0x27F7A183  # 失败横幅音效
AMBIENT_EVENT = 0x3FDA1A59  # 环境事件

# 类型常量
TYPE_STRING = 0x10
TYPE_BOOL = 0x01
TYPE_CONTAINER = 0x12

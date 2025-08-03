# 🐍 Although that way may not be obvious at first unless you're Dutch.
# 🐼 尽管这方法一开始并非如此直观，除非你是荷兰人
# @Author  : Virace
# @Email   : Virace@aliyun.com
# @Site    : x-item.com
# @Software: PyCharm
# @Create  : 2021/3/1 21:09
# @Update  : 2025/7/25 23:25
# @Detail  : Wwise bnk文件, Data块


from typing import List

from loguru import logger

from league_tools.core.section import SectionNoIdBNK, WemFile


class DATAFormatError(Exception):
    """DATA区块格式错误"""

    pass


class DATA(SectionNoIdBNK):
    """
    DATA区块包含未编码的.wem文件，文件之间紧密相连。
    不建议单独读取此区块，而是根据DIDX区块中提供的偏移量直接跳转到正确位置。

    44 41 54 41 -- DATA
    uint32: 区块长度
        FOR EACH (embedded .wem file) {
            byte[]: 以RIFF文件头(52 49 46 46)开始的.wem文件，长度在DIDX区块中给出
        } END FOR
    """

    def get_files(self, files: List[WemFile]) -> List[WemFile]:
        """
        根据提供的WemFile索引列表，从DATA区块中提取音频文件的二进制数据

        此方法会原地修改传入的WemFile对象，填充其data属性，同时返回修改后的列表

        :param files: 从DIDX区块获取的WemFile列表，每个对象包含ID、偏移量和长度信息
        :return: 填充了二进制数据的相同WemFile列表
        :raises DATAFormatError: 当读取数据过程中出现错误时
        """
        if not files:
            logger.warning("没有提供文件索引列表，无法从DATA区块获取数据")
            return files

        try:
            for i, item in enumerate(files):
                if item.offset >= self._data.end:
                    error_msg = f"文件 #{i} (ID={item.id})的偏移量({item.offset})超出DATA区块范围({self._data.end})"
                    logger.error(error_msg)
                    raise DATAFormatError(error_msg)

                if item.offset + item.length > self._data.end:
                    error_msg = f"文件 #{i} (ID={item.id})的数据范围({item.offset}~{item.offset + item.length})超出DATA区块范围({self._data.end})"
                    logger.error(error_msg)
                    raise DATAFormatError(error_msg)

                # 定位到文件起始位置并读取数据
                self._data.seek(item.offset, 0)
                item.data = self._data.bytes(item.length)

                # 验证RIFF头
                # if len(item.data) >= 4 and item.data[:4] != b'RIFF':
                #     logger.warning(f"文件 #{i} (ID={item.id}) 不是标准RIFF格式，缺少RIFF头")

                logger.trace(f"读取文件 #{i}: ID={item.id}, 大小={len(item.data)}字节")

            return files

        except Exception as e:
            if not isinstance(e, DATAFormatError):
                error_msg = f"从DATA区块提取文件数据时出错: {str(e)}"
                logger.error(error_msg)
                raise DATAFormatError(error_msg) from e
            raise

    def __repr__(self):
        """返回DATA对象的字符串表示"""
        return f"DATA: 区块大小={self._data.end}字节"

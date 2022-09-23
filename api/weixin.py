
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.weixin import Weixin
        from kyger.common import xml_data
        post_param = self.kg['post']

        xml_dict = xml_data(post_param)
        weixin = Weixin(self.db, self.kg, xml_dict)
        # 消息类型
        msg_type = xml_dict.get("MsgType", '')

        # 配置服务器
        res = weixin.check_signature()
        if isinstance(res, str):
            return res

        # 接收文本消息
        if msg_type == "text":
            return weixin.questions()
        # 接收图片消息
        elif msg_type == 'image':
            weixin.message_save(2)
            return weixin.send_text('您发送的照片我们已经收到，谢谢。')
        # 语音消息
        elif msg_type == 'voice':
            weixin.message_save(3)
            return weixin.send_text('语音消息已接收，谢谢。')
        # 视频消息
        elif msg_type == 'video':
            weixin.message_save(4)
            return weixin.send_text('视频文件已接收，谢谢。')
        # 接收事件推送
        elif msg_type == "event":
            event = xml_dict['Event']
            # 关注
            if event == "subscribe":
                from urllib.parse import quote, unquote
                # 确保api权限已经开通,否则无法拉取用户信息
                fans_info = weixin.get_fans_info(xml_dict['FromUserName'])

                fans = {
                    "groupid": fans_info.get("groupid", ""),
                    "openid": fans_info.get("openid", ""),
                    "nickname": quote(fans_info.get("nickname", "")),
                    "sex": numeric(fans_info.get("sex", 0)),
                    "city": fans_info.get("city", ""),
                    "country": fans_info.get("country", ""),
                    "province": fans_info.get("province", ""),
                    "language": fans_info.get("language", ""),
                    "headimgurl": fans_info.get("headimgurl", ""),
                    "qrscene": fans_info.get("qr_scene", ""),
                    "scenestr": fans_info.get("qr_scene_str", ""),
                    "subscribetime": fans_info.get("subscribe_time", "")
                }
                self.db.add('wx_fans', fans)

                default_group = self.db.list(table='wx_group', where='id=0', shift=1)
                self.db.edit('wx_group', {'count': default_group['count'] + 1}, where='id=0')
                weixin.message_save(0, '关注公众号', openid=fans_info.get("openid", ""))
                # 扫码关注事件
                if xml_dict.get('EventKey', '').startswith('qrscene_'):
                    pass
                return weixin.send_material(1)
            # 取消关注
            elif event == "unsubscribe":
                del_fans = self.db.list(
                    table='%swx_fans as a, %swx_group as b' % (self.db.cfg["prefix"],  self.db.cfg["prefix"]),
                    field='a.groupid, b.count',
                    where='a.groupid = b.id && openid="%s"' % xml_dict['FromUserName'],
                    shift=1
                )
                self.db.edit('wx_group', {'count': del_fans['count'] -1}, where="id=%s" % del_fans['groupid'])
                self.db.dele('message', where="openid='%s'" % xml_dict['FromUserName'])
                self.db.dele('wx_fans', where="openid='%s'" % xml_dict['FromUserName'])
                return ''
            # 已关注用户扫码事件
            elif event == 'SCAN':
                return ''

            # 上报地理位置事件
            elif event == 'LOCATION':
                return ''

            # 自定义菜单事件
            elif event == 'CLICK':
                key = xml_dict.get('EventKey', '')
                dict2json_file({"key":key})
                # 用户点击本地素材
                if key.startswith('LOCAL_MATERIAL_'):
                    # 本地素材id
                    material_id = numeric(key.split('_')[-1], 0)
                    res = self.db.list(table='material', where=material_id)
                    if not res: return ''
                    return weixin.send_material(material_id)
                # 微信素材
                if key.startswith('WX_MATERIAL_'):
                    # 微信素材id
                    wx_material_id = numeric(key.split('_')[-1], 0)
                    res = self.db.list(table='wx_material', where=wx_material_id)
                    # dict2json_file({"res": res, "wx_material_id":wx_material_id})
                    if not res: return ''
                    return weixin.send_wx_material(wx_material_id)

                return ''

        else:
            return ''




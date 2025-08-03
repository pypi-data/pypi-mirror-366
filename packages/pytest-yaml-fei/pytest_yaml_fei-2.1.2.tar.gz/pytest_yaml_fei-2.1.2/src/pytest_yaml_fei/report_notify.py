from dingtalkchatbot.chatbot import DingtalkChatbot
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from .log import log


class NotificationManager:
    """统一管理所有通知方式的类"""

    @staticmethod
    def send_dingtalk(access_token, text="", **kwargs):
        """
        发送钉钉通知
        机器人初始化
            :param access_token: 钉钉群自定义机器人access_token
                :param secret: 机器人安全设置页面勾选"加签"时需要传入的密钥
            :param pc_slide: 消息链接打开方式，默认False为浏览器打开，设置为True时为PC端侧边栏打开
            :param fail_notice: 消息发送失败提醒，默认为False不提醒，开发者可以根据返回的消息发送结果自行判断和处理

        钉钉机器人通知报告
        markdown类型
            :param title: 首屏会话透出的展示内容
            :param text: markdown格式的消息内容
            :param is_at_all: @所有人时：true，否则为：false（可选）
            :param at_mobiles: 被@人的手机号
            :param at_dingtalk_ids: 被@用户的UserId（企业内部机器人可用，可选）
            :param is_auto_at: 是否自动在text内容末尾添加@手机号，默认自动添加，也可设置为False，然后自行在text内容中自定义@手机号的位置，才有@效果，支持同时@多个手机号（可选）
            :return: 返回消息发送结果
        """
        try:
            webhook = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}'
            ding = DingtalkChatbot(
                webhook=webhook,
                secret=kwargs.get('secret'),
                pc_slide=kwargs.get('pc_slide', False),
                fail_notice=kwargs.get('fail_notice', False)
            )
            ding.send_markdown(
                title=kwargs.get('title', '测试报告'),
                text=text,
                is_at_all=kwargs.get('is_at_all', False),
                at_mobiles=kwargs.get('at_mobiles', []),
                at_dingtalk_ids=kwargs.get('at_dingtalk_ids', []),
                is_auto_at=kwargs.get('is_auto_at', True)
            )
        except Exception as e:
            log.error(f"钉钉通知初始化失败: {str(e)}")
            return None

    @staticmethod
    def send_feishu(token, text="", **kwargs):
        """
        发送飞书通知
        :param token: 飞书机器人Webhook地址
        :param text: 通知内容
        :param kwargs: 其他参数，包括:
            - is_success: 测试结果，默认为True
            - title: 通知标题，默认为'测试报告'
        :return: 发送结果，成功返回True，失败返回False
        """
        webhook = f"https://open.feishu.cn/open-apis/bot/v2/hook/{token}"
        headers = {"Content-Type": "application/json"}
        color = "green" if kwargs.get('is_success', True) else "red"
        data = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "elements": [{"tag": "markdown", "content": text}],
                "header": {
                    "title": {"content": kwargs.get('title', '测试报告'), "tag": "plain_text"},
                    "template": color
                }
            }
        }
        try:
            response = requests.post(webhook, headers=headers, data=json.dumps(data))
            return response.json()
        except Exception as e:
            log.error(f"飞书通知发送失败: {str(e)}")
            return None

    @staticmethod
    def send_wecom(token, text="", **kwargs):
        """
        发送企业微信通知
        :param token: 企业微信机器人Webhook地址
        :param text: 通知内容
        :param kwargs: 其他参数，包括:
            - mentioned_list: 被@人的手机号列表
            - mentioned_mobile_list: 被@人的手机号列表
            - is_success: 测试结果，默认为True
            - title: 通知标题，默认为'测试报告'
        :return: 发送结果，成功返回True，失败返回False
        """
        webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={token}"
        headers = {"Content-Type": "application/json"}
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": text,
                "mentioned_list": kwargs.get('mentioned_list', []),
                "mentioned_mobile_list": kwargs.get('mentioned_mobile_list', [])
            }
        }
        try:
            response = requests.post(webhook, headers=headers, data=json.dumps(data))
            return response.json()
        except Exception as e:
            log.error(f"企业微信通知发送失败: {str(e)}")
            return None

    @staticmethod
    def send_email(content, **kwargs):
        """发送邮件通知
        :param content: 邮件内容
        :param kwargs: 其他参数，包括:
            - user: SMTP登录用户名
            - password: SMTP登录密码
            - ssl: 是否使用SSL，默认为True
            - host: SMTP服务器地址，如'smtp.qq.com:465'
            - port: SMTP服务器端口
            - sender: 发件人邮箱,获取取user
            - to/receivers: 收件人邮箱列表
            - subject: 邮件主题
        """
        sender, receivers = kwargs.get('sender') or kwargs.get('user'), kwargs.get('receivers') or kwargs.get('to')
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header(sender)
        message['To'] = Header(','.join(receivers), 'utf-8')
        message['Subject'] = Header(kwargs.get('subject', '接口自动化测试报告'), 'utf-8')

        try:
            use_ssl = kwargs.get('ssl', True)
            smtp = smtplib.SMTP_SSL(kwargs.get('host')) if use_ssl else smtplib.SMTP(kwargs.get('host'))
            smtp.login(kwargs.get('user'), kwargs.get('password'))
            smtp.sendmail(sender, receivers, message.as_string())
            smtp.quit()
            return True
        except Exception as e:
            log.error(f"邮件发送失败: {str(e)}")
            return False


# 保留原有函数式调用方式，内部调用NotificationManager
def ding_ding_notify(*args, **kwargs):
    """钉钉通知(兼容旧调用方式)"""
    return NotificationManager.send_dingtalk(*args, **kwargs)


def fei_shu_notify(*args, **kwargs):
    """飞书通知(兼容旧调用方式)"""
    return NotificationManager.send_feishu(*args, **kwargs)


def we_com_notify(*args, **kwargs):
    """企业微信通知(兼容旧调用方式)"""
    return NotificationManager.send_wecom(*args, **kwargs)


def email_notify(*args, **kwargs):
    """邮件通知"""
    return NotificationManager.send_email(*args, **kwargs)

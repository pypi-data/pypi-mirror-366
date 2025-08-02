# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-11 21:56:56
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Baidu API methods.
"""


from typing import Any, TypedDict, NotRequired, Literal, Hashable, overload
from collections.abc import Iterable, Generator
from enum import StrEnum
from datetime import datetime, timedelta
from requests import Response
from uuid import uuid1
from json import loads as json_loads
from reykit.rbase import throw, warn, catch_exc
from reykit.rnet import request as reykit_request
from reykit.ros import File, get_md5
from reykit.rrand import randn, randi
from reykit.rtime import now, wait

from ..rbase import API


__all__ = (
    'APIBaidu',
    'APIBaiduFanyiLangEnum',
    'APIBaiduFanyiLangAutoEnum',
    'APIBaiduFanyi',
    'APIBaiduQianfan',
    'APIBaiduQianfanChat',
    'APIBaiduQianfanImage',
    'APIBaiduQianfanVoice'
)


FanyiResponseResult = TypedDict('FanyiResponseResult', {'src': str, 'dst': str})
FanyiResponse = TypedDict('FanyiResponse', {'from': str, 'to': str, 'trans_result': list[FanyiResponseResult]})

# Key 'role' value 'system' only in first.
# Key 'role' value 'user' and 'assistant' can mix.
# Key 'name' is distinguish users.
ModelName = str
ModelNames = list[ModelName]
_ChatRecord = TypedDict('ChatRecords', {'role': Literal['system', 'user', 'assistant'], 'content': str, 'name': NotRequired[str]})
ChatRecords = list[_ChatRecord]
ChatRecordsIndex = Hashable
ChatRecordsData = dict[ChatRecordsIndex, ChatRecords]
ChatResponseWebItem = TypedDict('ChatResponseWebItem', {'index': int, 'url': str, 'title': str})
ChatResponseWeb = list[ChatResponseWebItem]

CallRecord = TypedDict('CallRecord', {'time': datetime, 'data': Any})
ChatRecord = TypedDict('ChatRecord', {'time': datetime, 'send': str, 'receive': str})
HistoryMessage = TypedDict('HistoryMessage', {'role': str, 'content': str})


class APIBaidu(API):
    """
    Baidu API type.
    """


class APIBaiduFanyiLangEnum(APIBaidu, StrEnum):
    """
    Baidu Fanyi APT language enumeration type.
    """

    ZH = 'zh'
    EN = 'en'
    YUE = 'yue'
    KOR = 'kor'
    TH = 'th'
    PT = 'pt'
    EL = 'el'
    BUL = 'bul'
    FIN = 'fin'
    SLO = 'slo'
    CHT = 'cht'
    WYW = 'wyw'
    FRA = 'fra'
    ARA = 'ara'
    DE = 'de'
    NL = 'nl'
    EST = 'est'
    CS = 'cs'
    SWE = 'swe'
    VIE = 'vie'
    JP = 'jp'
    SPA = 'spa'
    RU = 'ru'
    IT = 'it'
    PL = 'pl'
    DAN = 'dan'
    ROM = 'rom'
    HU ='hu'


class APIBaiduFanyiLangAutoEnum(APIBaidu, StrEnum):
    """
    Baidu Fanyi APT language auto type enumeration.
    """

    AUTO = 'auto'


class APIBaiduFanyi(APIBaidu):
    """
    Baidu Fanyi API type.
    API description: https://fanyi-api.baidu.com/product/113.
    """

    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    LangEnum = APIBaiduFanyiLangEnum
    LangAutoEnum = APIBaiduFanyiLangAutoEnum


    def __init__(
        self,
        appid: str,
        appkey: str,
        is_auth: bool = True
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        appid : APP ID.
        appkey : APP key.
        is_auth : Is authorized.
        """

        # Build.
        self.appid = appid
        self.appkey = appkey
        self.is_auth = is_auth


    def sign(self, text: str, num: int) -> str:
        """
        Get signature.

        Parameters
        ----------
        text : Text.
        num : Number.

        Returns
        -------
        Signature.
        """

        # Get parameter.
        num_str = str(num)

        # Sign.
        data = ''.join(
            (
                self.appid,
                text,
                num_str,
                self.appkey
            )
        )
        md5 = get_md5(data)

        return md5


    def request(
        self,
        text: str,
        from_lang: APIBaiduFanyiLangEnum | APIBaiduFanyiLangAutoEnum,
        to_lang: APIBaiduFanyiLangEnum
    ) -> FanyiResponse:
        """
        Request translate API.

        Parameters
        ----------
        text : Text.
        from_lang : Source language.
        to_lang : Target language.

        Returns
        -------
        Response dictionary.
        """

        # Get parameter.
        rand_num = randn(32768, 65536)
        sign = self.sign(text, rand_num)
        params = {
            'q': text,
            'from': from_lang.value,
            'to': to_lang.value,
            'appid': self.appid,
            'salt': rand_num,
            'sign': sign
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Request.
        response = reykit_request(
            self.url,
            params,
            headers=headers,
            check=True
        )

        # Check.
        content_type = response.headers['Content-Type']
        if content_type.startswith('application/json'):
            response_json: dict = response.json()
            if 'error_code' in response_json:
                throw(AssertionError, response_json)
        else:
            throw(AssertionError, content_type)

        return response_json


    def translate(
        self,
        text: str,
        from_lang: APIBaiduFanyiLangEnum | APIBaiduFanyiLangAutoEnum = APIBaiduFanyiLangAutoEnum.AUTO,
        to_lang: APIBaiduFanyiLangEnum | None = None
    ) -> str:
        """
        Translate.

        Parameters
        ----------
        text : Text.
            - `self.is_auth is True`: Maximum length is 6000.
            - `self.is_auth is False`: Maximum length is 3000.
        from_lang : Source language.
        to_lang : Target language.
            - `None`: When text first character is letter, then is chinese, otherwise is english.

        Returns
        -------
        Translated text.
        """

        # Check.
        max_len = (3000, 6000)[self.is_auth]
        text_len = len(text)
        if len(text) > max_len:
            throw(AssertionError, max_len, text_len)

        # Handle parameter.
        text = text.strip()
        if to_lang is None:
            prefix = tuple('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            if text[0].startswith(prefix):
                to_lang = APIBaiduFanyiLangEnum.ZH
            else:
                to_lang = APIBaiduFanyiLangEnum.EN

        # Request.
        response_dict = self.request(text, from_lang, to_lang)

        # Extract.
        trans_text = '\n'.join(
            [
                trans_text_line_dict['dst']
                for trans_text_line_dict in response_dict['trans_result']
            ]
        )

        return trans_text


    __call__ = translate


class APIBaiduQianfan(APIBaidu):
    """
    Baidu Qianfan API type.
    """


    def __init__(
        self,
        key: str,
        secret: str,
        token_valid_seconds: float = 43200
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        key : API key.
        secret : API secret.
        token_valid_seconds : Authorization token vaild seconds.
        """

        # Set attribute.
        self.key = key
        self.secret = secret
        self.token_valid_seconds = token_valid_seconds
        self.cuid = uuid1()
        self.call_records: list[CallRecord] = []
        self.start_time = now()


    def get_token(self) -> str:
        """
        Get token.

        Returns
        -------
        Token.
        """

        # Get parameter.
        url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.key,
            'client_secret': self.secret
        }

        # Request.
        response = self.request(
            url,
            params,
            method='post'
        )

        # Extract.
        response_json = response.json()
        token = response_json['access_token']

        return token


    @property
    def token(self) -> str:
        """
        Get authorization token.
        """

        # Get parameter.
        if hasattr(self, 'token_time'):
            token_time: datetime = getattr(self, 'token_time')
        else:
            token_time = None
        if (
            token_time is None
            or (now() - token_time).seconds > self.token_valid_seconds
        ):
            self.token_time = now()
            self._token = self.get_token()

        return self._token


    def request(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Response:
        """
        Request.

        Parameters
        ----------
        args : Position arguments of function.
        kwargs : Keyword arguments of function.

        Returns
        -------
        `Response` instance.
        """

        # Request.
        response = reykit_request(*args, **kwargs)

        # Check.
        content_type = response.headers['Content-Type']
        if content_type.startswith('application/json'):
            response_json: dict = response.json()
            if 'error_code' in response_json:
                raise AssertionError('Baidu API request failed', response_json)

        return response


    def record_call(
        self,
        **data: Any
    ) -> None:
        """
        Record call.

        Parameters
        ----------
        data : Record data.
        """

        # Get parameter.
        record = {
            'time': now(),
            'data': data
        }

        # Record.
        self.call_records.append(record)


    @property
    def interval(self) -> float:
        """
        Return the interval seconds from last call.
        When no record, then return the interval seconds from start.

        Returns
        -------
        Interval seconds.
        """

        # Get parameter.
        if self.call_records == []:
            last_time = self.start_time
        else:
            last_time: datetime = self.call_records[-1]['time']

        # Count.
        now_time = now()
        interval_time = now_time - last_time
        interval_seconds = interval_time.total_seconds()

        return interval_seconds


class _APIBaiduQianfan(APIBaidu):
    """
    Baidu Qianfan API type.
    """

    # API URL.
    url: str


    def __init__(
        self,
        key: str,
        model: ModelName
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        key : API key.
        model : Model name, can get model name list from `self.models`.
        """

        # Build.
        self.key = key
        self.model = model
        self.auth = 'Bearer ' + key


    def request(self, json: dict) -> dict | Iterable[str]:
        """
        Request API.

        Parameters
        ----------
        json : Request body.

        Returns
        -------
        Response json or iterable.
            - `Contain key 'stream' value True`: Return `Iterable[bytes]`.
        """

        # Get parameter.
        json['model'] = self.model
        rand: int | None = getattr(self, 'rand', None)
        if rand is not None:
            json['temperature'] = rand
        stream: bool = json.get('stream', False)
        headers = {'Authorization': self.auth, 'Content-Type': 'application/json'}

        # Request.
        response = reykit_request(
            self.url,
            json=json,
            headers=headers,
            stream=stream,
            check=True
        )

        # Stream.
        if stream:
            iterable: Iterable[str] = response.iter_lines(decode_unicode=True)
            return iterable

        # Check.
        content_type = response.headers['Content-Type']
        if content_type.startswith('application/json'):
            response_json: dict = response.json()
            if 'code' in response_json:
                throw(AssertionError, response_json)
        else:
            throw(AssertionError, content_type)

        return response_json


    @property
    def models(self) -> ModelNames:
        """
        Get model name list.

        Returns
        -------
        Model name list.
        """

        # Get parameter.
        url = 'https://qianfan.baidubce.com/v2/models'
        headers = {'Authorization': self.auth, 'Content-Type': 'application/json'}

        # Request.
        response = reykit_request(url, headers=headers, check=True)

        # Check.
        content_type = response.headers['Content-Type']
        if content_type.startswith('application/json'):
            response_json: dict = response.json()
            if 'code' in response_json:
                throw(AssertionError, response_json)
        else:
            throw(AssertionError, content_type)

        # Extract.
        result = [
            row['id']
            for row in response_json['data']
        ]

        return result


class _APIBaiduQianfanChat(_APIBaiduQianfan):
    """
    Baidu Qianfan chat API type.
    """

    url = 'https://qianfan.baidubce.com/v2/chat/completions'


    def __init__(
        self,
        key: str,
        role: str | None = None,
        name: str | None = None,
        model: ModelName = 'ernie-4.5-turbo-32k',
        rand: float = 1
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        key : API key.
        role : AI role description.
        name : AI role name.
        model : Model name, can get model name list from `self.models`.
        rand : Randomness, value range is `[0,2]`.
        """

        # Build.
        super().__init__(key, model)
        self.role = role
        self.name = name
        self.rand = rand
        self.data: ChatRecordsData = {}


    @overload
    def chat(
        self,
        text: str,
        name: str | None = None,
        index: ChatRecordsIndex | None = None
    ) -> str: ...

    @overload
    def chat(
        self,
        text: str,
        name: str | None = None,
        index: ChatRecordsIndex | None = None,
        *,
        web: Literal[True]
    ) -> tuple[str, ChatResponseWeb]: ...

    @overload
    def chat(
        self,
        text: str,
        name: str | None = None,
        index: ChatRecordsIndex | None = None,
        *,
        stream: Literal[True]
    ) -> Iterable[str]: ...

    @overload
    def chat(
        self,
        text: str,
        name: str | None = None,
        index: ChatRecordsIndex | None = None,
        *,
        web: Literal[True],
        stream: Literal[True]
    ) -> tuple[Iterable[str], ChatResponseWeb]: ...

    def chat(
        self,
        text: str,
        name: str | None = None,
        index: ChatRecordsIndex | None = None,
        web: bool = False,
        stream: bool = False
    ) -> str | tuple[str, ChatResponseWeb] | Iterable[str] | tuple[Iterable[str], ChatResponseWeb]:
        """
        Chat with AI.

        Parameters
        ----------
        text : User chat text.
        name : User name.
        index : Chat records index.
            `None`: Not use record.
        web : Whether use web search.
        think : Whether use deep think.
        stream : Whether use stream response.
            - `Literal[True]`: Will not update records, need manual update.

        Returns
        -------
        Response content.
        """

        # Get parameter.
        chat_records_update = []

        ## Record.
        if index is not None:
            chat_records: ChatRecords = self.data.setdefault(index, [])
        else:
            chat_records: ChatRecords = []

        ## New.
        chat_record_role = None
        if (
            chat_records == []
            and self.role is not None
        ):
            chat_record_role = {'role': 'system', 'content': self.role}
            if self.name is not None:
                chat_record_role['name'] = self.name
            chat_records_update.append(chat_record_role)

        ## Now.
        chat_record_now = {'role': 'user', 'content': text}
        if name is not None:
            chat_record_now['name'] = name
        chat_records_update.append(chat_record_now)

        chat_record_role = [chat_record_role]
        json = {'messages': [*chat_records, *chat_records_update]}
        if web:
            json['web_search'] = {
                'enable': True,
                'enable_citation': True,
                'enable_trace': True
            }
        if stream:
            json['stream'] = True

        # Request.
        response = self.request(json)

        # Return.

        ## Stream.
        if stream:
            response_iter: Iterable[str] = response
            response_line_first: str = next(response_iter)
            response_line_first = response_line_first[6:]
            response_json_first: dict = json_loads(response_line_first)
            response_web: ChatResponseWeb = response_json_first.get('search_results', [])
            response_content_first: str = response_json_first['choices'][0]['delta']['content']


            ### Defin.
            def _generator() -> Generator[str, Any, None]:
                """
                Generator function.

                Returns
                -------
                Generator
                """

                # First.
                yield response_content_first

                # Next.
                for response_line in response_iter:
                    if response_line == '':
                        continue
                    elif response_line == 'data: [DONE]':
                        break
                    response_line = response_line[6:]
                    response_json: dict = json_loads(response_line)
                    response_content: str = response_json['choices'][0]['delta']['content']
                    yield response_content


            ### Web.
            generator = _generator()
            if web:
                return generator, response_web

            return generator

        ## Not Stream.
        else:
            response_json: dict = response
            response_content: str = response_json['choices'][0]['message']['content']

            ### Record.
            if index is not None:
                chat_records_reply = {'role': 'assistant', 'content': response_content}
                if self.name is not None:
                    chat_records_reply['name'] = self.name
                chat_records_update.append(chat_records_reply)
                chat_records.extend(chat_records_update)

            ### Web.
            if web:
                response_web: ChatResponseWeb = response_json.get('search_results', [])
                return response_content, response_web

            return response_content


class APIBaiduQianfanChat(APIBaiduQianfan):
    """
    Baidu Qianfan API chat type.
    """

    # Character.
    characters = (
        '善良', '淳厚', '淳朴', '豁达', '开朗', '体贴', '活跃', '慈祥', '仁慈', '温和',
        '温存', '和蔼', '和气', '直爽', '耿直', '憨直', '敦厚', '正直', '爽直', '率直',
        '刚直', '正派', '刚正', '纯正', '自信', '信心',
        '老实', '谦恭', '谦虚', '谦逊', '自谦', '谦和', '坚强', '顽强', '建议', '刚毅',
        '刚强', '倔强', '强悍', '刚毅', '坚定', '坚韧', '坚决', '坚忍', '勇敢',
        '勇猛', '勤劳', '勤恳', '勤奋', '勤勉', '勤快', '勤俭', '辛勤', '刻苦', '节约',
        '狂妄', '骄横', '骄纵', '窘态', '窘迫', '困窘', '难堪', '害羞', '羞涩', '赧然',
        '无语', '羞赧'
    )


    def __init__(
        self,
        key: str,
        secret: str,
        character: str | None = None
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        key : API key.
        secret : API secret.
        Character : Character of language model.
        """

        # Set attribute.
        super().__init__(key, secret)
        self.chat_records: dict[str, ChatRecord] = {}
        self.character=character


    def chat(
        self,
        text: str,
        character: str | Literal[False] | None = None,
        history_key: str | None = None,
        history_recent_seconds: float = 1800,
        history_max_word: int = 400
    ) -> str:
        """
        Chat with language model.

        Parameters
        ----------
        text : Text.
        Character : Character of language model.
            - `None`, Use `self.character`: attribute.
            - `str`: Use this value.
            - `Literal[False]`: Do not set.
        Character : Character of language model.
        history_key : Chat history records key.
        history_recent_seconds : Limit recent seconds of chat history.
        history_max_word : Limit maximum word of chat history.

        Returns
        -------
        Reply text.
        """

        # Get parameter.
        url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro'
        params = {'access_token': self.token}
        headers = {'Content-Type': 'application/json'}
        if history_key is None:
            messages = []
        else:
            messages = self.history_messages(
                history_key,
                history_recent_seconds,
                history_max_word
            )
        message = {'role': 'user', 'content': text}
        messages.append(message)
        json = {'messages': messages}
        match character:
            case None:
                character = self.character
            case False:
                character = None
        if character is not None:
            json['system'] = character

        # Request.
        try:
            response = self.request(
                url,
                params=params,
                json=json,
                headers=headers
            )

        ## Parameter 'system' error.
        except:
            *_, exc_instance, _ = catch_exc()
            error_code = exc_instance.args[1]['error_code']
            if error_code == 336104:
                result = self.chat(
                    text,
                    False,
                    history_key,
                    history_recent_seconds,
                    history_max_word
                )
                return result
            else:
                raise

        # Extract.
        response_json: dict = response.json()
        result: str = response_json['result']

        # Record.
        self.record_call(
            messages=messages,
            character=character
        )
        if history_key is not None:
            self.record_chat(
                text,
                result,
                history_key
            )

        return result


    def record_chat(
        self,
        send: str,
        receive: str,
        key: str
    ) -> None:
        """
        Record chat.

        Parameters
        ----------
        send : Send text.
        receive : Receive text.
        key : Chat history records key.
        """

        # Generate.
        record = {
            'time': now(),
            'send': send,
            'receive': receive
        }

        # Record.
        reocrds = self.chat_records.get(key)
        if reocrds is None:
            self.chat_records[key] = [record]
        else:
            reocrds.append(record)


    def history_messages(
        self,
        key: str,
        recent_seconds: float,
        max_word: int
    ) -> list[HistoryMessage]:
        """
        Return history messages.

        Parameters
        ----------
        key : Chat history records key.
        recent_seconds : Limit recent seconds of chat history.
        max_word : Limit maximum word of chat history.

        Returns
        -------
        History messages.
        """

        # Get parameter.
        records = self.chat_records.get(key, [])
        now_time = now()

        # Generate.
        messages = []
        word_count = 0
        for record in records:

            ## Limit time.
            interval_time: timedelta = now_time - record['time']
            interval_seconds = interval_time.total_seconds()
            if interval_seconds > recent_seconds:
                break

            ## Limit word.
            word_len = len(record['send']) + len(record['receive'])
            character_len = len(self.character)
            word_count += word_len
            if word_count + character_len > max_word:
                break

            ## Append.
            message = [
                {'role': 'user', 'content': record['send']},
                {'role': 'assistant', 'content': record['receive']}
            ]
            messages.extend(message)

        return messages


    def interval_chat(
        self,
        key: str
    ) -> float:
        """
        Return the interval seconds from last chat.
        When no record, then return the interval seconds from start.

        Parameters
        ----------
        key : Chat history records key.

        Returns
        -------
        Interval seconds.
        """

        # Get parameter.
        records = self.chat_records.get(key)
        if records is None:
            last_time = self.start_time
        else:
            last_time: datetime = records[-1]['time']
        if self.call_records == []:
            last_time = self.start_time
        else:
            last_time: datetime = self.call_records[-1]['time']

        # Count.
        now_time = now()
        interval_time = now_time - last_time
        interval_seconds = interval_time.total_seconds()

        return interval_seconds


    def modify(
        self,
        text: str
    ) -> str:
        """
        Modify text.
        """

        # Get parameter.
        character = randi(self.characters)

        # Modify.
        text = '用%s的语气，润色以下这句话\n%s' % (character, text)
        text_modify = self.chat(text)

        return text_modify


    __call__ = chat


class APIBaiduQianfanImage(APIBaiduQianfan):
    """
    Baidu Qianfan API image type.
    """


    def __to_url_create_task(
        self,
        text: str
    ) -> str:
        """
        Create task of generate image URL from text.

        Parameters
        ----------
        text : Text, length cannot exceed 60.

        Returns
        -------
        Task ID.
        """

        # Get parameter.
        url = 'https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2'
        params = {'access_token': self.token}
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        json = {
            'prompt': text,
            'width': 1024,
            'height': 1024
        }

        # Request.
        response = self.request(
            url,
            params=params,
            json=json,
            headers=headers
        )

        # Record.
        self.record_call(text=text)

        # Extract.
        response_json: dict = response.json()
        task_id: str = response_json['data']['task_id']

        return task_id


    def __to_url_query_task(
        self,
        task_id: str
    ) -> dict:
        """
        Query task of generate image URL from text.

        Parameters
        ----------
        task_id : Task ID.

        Returns
        -------
        Task information.
        """

        # Get parameter.
        url = 'https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2'
        params = {'access_token': self.token}
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        json = {'task_id': task_id}

        # Request.
        response = self.request(
            url,
            params=params,
            json=json,
            headers=headers
        )

        # Extract.
        response_json: dict = response.json()
        task_info: dict = response_json['data']

        return task_info


    def to_url(
        self,
        text: str,
        path: str | None = None
    ) -> str:
        """
        Generate image URL from text.

        Parameters
        ----------
        text : Text, length cannot exceed 60.
        path : File save path.
            - `None`: Not save.

        Returns
        -------
        Image URL.
        """

        # Create.
        task_id = self.__to_url_create_task(text)

        # Wait.
        store = {}


        ## Define.
        def is_task_success() -> bool:
            """
            Whether if is task successed.

            Returns
            -------
            Judge result.
            """

            # Query.
            task_info = self.__to_url_query_task(task_id)

            # Judge.
            match task_info['task_status']:
                case 'RUNNING':
                    return False
                case 'SUCCESS':
                    store['url'] = task_info['sub_task_result_list'][0]['final_image_list'][0]['img_url']
                    return True
                case _:
                    raise AssertionError('Baidu API text to image task failed')


        ## Start.
        wait(
            is_task_success,
            _interval=0.5,
            _timeout=600
        )

        ## Extract.
        url = store['url']

        # Save.
        if path is not None:
            response = self.request(url)
            rfile = File(path)
            rfile.write(response.content)

        return url


    __call__ = to_url


class APIBaiduQianfanVoice(APIBaiduQianfan):
    """
    Baidu Qianfan API voice type.
    """


    def to_file(
        self,
        text: str,
        path: str | None = None
    ) -> bytes:
        """
        Generate voice file from text.

        Parameters
        ----------
        text : Text, length cannot exceed 60.
        path : File save path.
            - `None`: Not save.

        Returns
        -------
        Voice bytes data.
        """

        # Check.
        if len(text) > 60:
            text = text[:60]
            warn('parameter "text" length cannot exceed 60')

        # Get parameter.
        url = 'https://tsn.baidu.com/text2audio'
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'tok': self.token,
            'tex': text,
            'cuid': self.cuid,
            'ctp': 1,
            'lan': 'zh',
            'spd': 5,
            'pit': 5,
            'vol': 5,
            'per': 4,
            'aue': 3
        }

        # Request.
        response = self.request(
            url,
            data=data,
            headers=headers
        )

        # Record.
        self.record_call(
            text=text,
            path=path
        )

        # Extract.
        file_bytes = response.content

        # Save.
        if path is not None:
            rfile = File(path)
            rfile.write(file_bytes)

        return file_bytes


    def __to_url_create_task(
        self,
        text: str
    ) -> str:
        """
        Create task of generate voice URL from text.

        Parameters
        ----------
        text : Text, length cannot exceed 60.

        Returns
        -------
        Task ID.
        """

        # Get parameter.
        url = 'https://aip.baidubce.com/rpc/2.0/tts/v1/create'
        params = {'access_token': self.token}
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        json = {
            'text': text,
            'format': 'mp3-16k',
            'voice': 4,
            'lang': 'zh',
            'speed': 5,
            'pitch': 5,
            'volume': 5,
            'enable_subtitle': 0
        }

        # Request.
        response = self.request(
            url,
            params=params,
            json=json,
            headers=headers
        )

        # Record.
        self.record_call(text=text)

        # Extract.
        response_json: dict = response.json()
        task_id: str = response_json['task_id']

        return task_id


    def __to_url_query_task(
        self,
        task_id: str
    ) -> dict:
        """
        Query task of generate voice URL from text.

        Parameters
        ----------
        task_id : Task ID.

        Returns
        -------
        Task information.
        """

        # Get parameter.
        url = 'https://aip.baidubce.com/rpc/2.0/tts/v1/query'
        params = {'access_token': self.token}
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        json = {'task_ids': [task_id]}

        # Request.
        response = self.request(
            url,
            params=params,
            json=json,
            headers=headers
        )

        # Extract.
        response_json: dict = response.json()
        task_info: dict = response_json['tasks_info'][0]

        return task_info


    def to_url(
        self,
        text: str,
        path: str | None = None
    ) -> str:
        """
        Generate voice URL from text.

        Parameters
        ----------
        text : Text, length cannot exceed 60.
        path : File save path.
            - `None`: Not save.

        Returns
        -------
        Voice URL.
        """

        # Create.
        task_id = self.__to_url_create_task(text)

        # Wait.
        store = {}


        ## Define.
        def is_task_success() -> bool:
            """
            Whether if is task successed.

            Returns
            -------
            Judge result.
            """

            # Query.
            task_info = self.__to_url_query_task(task_id)

            # Judge.
            match task_info['task_status']:
                case 'Running':
                    return False
                case 'Success':
                    store['url'] = task_info['task_result']['speech_url']
                    return True
                case _:
                    raise AssertionError('Baidu API text to voice task failed', task_info)


        ## Start.
        wait(
            is_task_success,
            _interval=0.5,
            _timeout=600
        )

        ## Extract.
        url = store['url']

        # Save.
        if path is not None:
            response = self.request(url)
            rfile = File(path)
            rfile.write(response.content)

        return url


    __call__ = to_url

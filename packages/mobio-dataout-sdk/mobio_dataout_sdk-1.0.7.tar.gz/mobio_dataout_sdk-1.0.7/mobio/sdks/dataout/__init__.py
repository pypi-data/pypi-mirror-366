import os, requests, json
from mobio.libs.Singleton import Singleton
from mobio.libs.kafka_lib.helpers.kafka_producer_manager import KafkaProducerManager
from mobio.libs.caching import LRUCacheDict

kafka_manager = KafkaProducerManager()


class DataOut:

    def send(self, body, merchant_id, data_type, key_message=None):
        try:
            key_message = key_message if key_message and isinstance(key_message, str) else ""
            list_app = AppConfig().get_list_connector_register(merchant_id, data_type)
            if list_app and len(list_app) > 0:
                allow_push = True
                if data_type == "profile_dynamic_event":
                    allow_push = self.check_dynamic_event_allow_push(body, list_app)
                if allow_push:
                    body_mess = {
                        ParamTopicSaveEvent.DATA_EVENT: body,
                        ParamTopicSaveEvent.MERCHANT_ID: merchant_id,
                        ParamTopicSaveEvent.DATA_TYPE: data_type,
                    }
                    kafka_manager.flush_message(topic="save-event-need-send", key=key_message, value=body_mess)
                # print("dataout_send success merchant_id: {}, data_type: {}".format(merchant_id, data_type))
                return allow_push
            else:
                # print("dataout_send fail merchant_id: {}, data_type: {}".format(merchant_id, data_type))
                return False
        except Exception as er:
            err_msg = "dataout_send, ERROR: {}".format(er)
            print(err_msg)
            return False

    @staticmethod
    def check_dynamic_event_allow_push(body, list_app):
        push_dynamic = False
        for i in list_app:
            if i.get("event_register") and isinstance(i.get("event_register"), list):
                if body.get("event_key") in i.get("event_register"):
                    push_dynamic = True
                    break
            else:
                push_dynamic = True
                break
        return push_dynamic


class RedisConfig:
    REDIS_URI = "{}?health_check_interval=30".format(os.environ.get("REDIS_BASE_URI", os.environ.get("REDIS_URI")))
    REDIS_TYPE = int(os.environ.get("REDIS_BASE_TYPE", os.environ.get("REDIS_TYPE", "1")))
    PREFIX = "data_out"

    class RedisType:
        REPLICA = 1
        CLUSTER = 2

    def get_redis_connection(self):
        if self.REDIS_TYPE == self.RedisType.CLUSTER:
            from redis.cluster import RedisCluster as Redis
            return Redis.from_url(self.REDIS_URI)
        else:
            import redis
            return redis.from_url(self.REDIS_URI)


@Singleton
class RedisClient(object):
    def __init__(self):
        self.redis_connect = RedisConfig().get_redis_connection()

    def get_connect(self):
        return self.redis_connect

    def get_value(self, key_cache):
        redis_conn = self.get_connect()
        return redis_conn.get(key_cache)

    def set_value_expire(self, key_cache, value_cache, time_seconds=3600):
        redis_conn = self.get_connect()
        redis_conn.setex(key_cache, time_seconds, value_cache)

    def delete_key(self, key_cache):
        redis_conn = self.get_connect()
        redis_conn.delete(key_cache)

    def set_value(self, key_cache, value_cache):
        redis_conn = self.get_connect()
        redis_conn.set(key_cache, value_cache)

    def get_keys(self, regex_pattern):
        redis_conn = self.get_connect()
        return redis_conn.scan_iter(regex_pattern)

    def delete_cache_data_by_pattern(self, pattern):
        redis_conn = self.get_connect()
        for key in redis_conn.scan_iter(pattern):
            redis_conn.delete(key)


class ParamTopicSaveEvent:
    DATA_EVENT = "data_event"
    MERCHANT_ID = "merchant_id"
    DATA_TYPE = "data_type"


def get_merchant_config_host(merchant_id, key_host):
    key_cache = "data_out#get_merchant_config_host#" + merchant_id + "#" + key_host
    redis_value = RedisClient().get_value(key_cache=key_cache)
    if not redis_value:
        adm_url = str("{host}/adm/api/v2.1/merchants/{merchant_id}/config/detail").format(
            host=os.environ.get("ADMIN_HOST", "https://api-test1.mobio.vn/"),
            merchant_id=merchant_id,
        )
        request_header = {"X-Module-Request": "DATA_OUT", "X-Mobio-SDK": "DATA_OUT"}
        param = {"fields": ",".join(["internal_host", "module_host", "public_host", "config_host"])}
        response = requests.get(
            adm_url,
            params=param,
            headers=request_header,
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
        data = result.get("data", {}) if result and result.get("data", {}) else {}
        value_cache = data.get(key_host, "")
        RedisClient().set_value_expire(key_cache=key_cache, value_cache=value_cache)
        return value_cache
    else:
        return str(redis_value.decode("utf-8"))


def get_list_app_merchant_register(merchant_id, data_type):
    key_cache = "data_out#connector_register_event#{merchant_id}#{event_key}".format(
        merchant_id=merchant_id, event_key=data_type)
    redis_value = RedisClient().get_value(key_cache=key_cache)
    if not redis_value:
        host_data_out = get_merchant_config_host(merchant_id, "marketplace-app-api-internal-service-host")
        api_url = str("{host}/market-place/internal/api/v1.0/data-flow/connectors/get-by-event-key").format(
            host=host_data_out,
        )
        request_header = {
            "X-Module-Request": "DATA_OUT", "X-Mobio-SDK": "DATA_OUT",
            "Authorization": 'Basic {}'.format(os.environ.get('YEK_REWOP', "f38b67fa-22f3-4680-9d01-c36b23bd0cad")),
            "X-Merchant-ID": merchant_id,
        }
        response = requests.get(
            api_url,
            params={"event_key": data_type},
            headers=request_header,
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
        list_connector = []
        data = result.get("data", []) if result and result.get("data", []) else []
        if data and isinstance(data, list):
            for i in data:
                event_register = []
                if i.get("config") and isinstance(i.get("config"), dict) and i.get(
                        "config").get("list_specific_event"):
                    event_register = i.get("config").get("list_specific_event")
                list_connector.append({
                    "connector_id": i.get("connector_id"),
                    "app_id": i.get("app_id"),
                    "event_register": event_register,
                })
        RedisClient().set_value_expire(key_cache=key_cache, value_cache=json.dumps(list_connector, ensure_ascii=False))
        return data
    else:
        # print("get_list_app_merchant_register cache exists")
        return json.loads(str(redis_value.decode("utf-8")))


@Singleton
class AppConfig:
    def __init__(self):
        self.connector_register = LRUCacheDict(expiration=900)

    def get_list_connector_register(self, merchant_id, data_type):
        list_app_valid = None
        try:
            key_cache = merchant_id + data_type
            try:
                list_app_valid = self.connector_register.getitem(key_cache)
            except:
                list_app_valid = None
            if list_app_valid is None:
                list_app_valid = get_list_app_merchant_register(merchant_id, data_type)
                self.connector_register.set_item(key_cache, list_app_valid)
        except Exception as ex:
            print("get_list_connector_register: {}".format(ex))
        return list_app_valid


if __name__ == "__main__":
    body, merchant_id, data_type = {"name": "test"}, "1b99bdcf-d582-4f49-9715-1b61dfff3924", "profile"
    result = DataOut().send(body, merchant_id, data_type)
    print(result)

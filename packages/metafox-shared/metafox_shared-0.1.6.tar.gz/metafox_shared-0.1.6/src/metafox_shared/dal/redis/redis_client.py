#-------------------------------------------------------------------------------
# Copyright 2024 Vodéna
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# SPDX-License-Identifier: Apache-2.0
#-------------------------------------------------------------------------------

from redis import Redis

from metafox_shared.config import Config
from metafox_shared.exceptions.db import *
from metafox_shared.constants.api_constants import *
from metafox_shared.dal.idatastore import IDataStore

class RedisClient(IDataStore):
    """
    RedisClient is a class that provides an interface to interact with a Redis datastore.
    
    Methods:
        __init__() -> None:
            Initializes the Redis client and establishes a connection to the Redis server.
        set(key: str, value: str, collection_name: str) -> None:
            Sets a key-value pair in the Redis datastore. Raises an exception if the key already exists.
        get(key: str, collection_name: str) -> str:
            Retrieves the value associated with the given key from the Redis datastore. Raises an exception if the key does not exist.
        update(key: str, value: str, collection_name: str) -> None:
            Updates the value of an existing key in the Redis datastore. If the key does not exist, it sets the key-value pair.
        delete(key: str, collection_name: str) -> None:
            Deletes the key-value pair from the Redis datastore. Raises an exception if the key does not exist.
        get_automl_job_ids(collection_name: str) -> list:
            Retrieves a list of keys that match the CELERY_KEY_PREFIX from the Redis datastore.
        get_keys_by_pattern(pattern: str, collection_name: str) -> list:
            Retrieves a list of keys that match the given pattern from the Redis datastore.
        close() -> None:
            Closes the connection to the Redis server and prints a message indicating that the Redis client has been destroyed.
    """
    def __init__(self) -> None:
        try:
            self.redis = Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                password=Config.REDIS_PASSWORD,
                decode_responses=True
            )
            
            print("Redis connection established.")
        except Exception as e:
            raise DatabaseConnectionError(message=f"Failed to connect to Redis: {str(e)}")
        
    def set(self, key: str, value: str, collection_name: str) -> None:
        if self.redis.exists(key):
            raise DuplicateKeyError(key, "Key already exists in the collection.")
        
        try:
            self.redis.set(key, value)
        except Exception as e:
            raise DatabaseQueryError(query=f"set({{key}})", message=str(e))
        
    def get(self, key: str, collection_name: str) -> str:
        if self.redis.exists(key):
            return self.redis.get(key)

        raise KeyNotFoundError(key, "Key does not exist in the collection.")

    def update(self, key: str, value: str, collection_name: str) -> None:
        if self.redis.exists(key):
            try:
                self.redis.delete(key)
            except Exception as e:
                raise DatabaseQueryError(query=f"delete({{key}})", message=str(e))
            self.redis.set(key, value)
        else:
            self.redis.set(key, value)
    
    def delete(self, key: str, collection_name: str) -> None:
        if self.redis.exists(key):
            try:
                self.redis.delete(key)
            except Exception as e:
                raise DatabaseQueryError(query=f"delete({{key}})", message=str(e))
            return

        raise KeyNotFoundError(key, "Key does not exist in the collection.")

    def get_automl_job_ids(self, collection_name: str) -> list:
        cursor = '0'
        matching_keys = []
        
        while cursor != 0:
            cursor, keys = self.redis.scan(cursor = cursor)
            
            for key in keys:
                if key.startswith(CELERY_KEY_PREFIX):
                    matching_keys.append(key.replace(CELERY_KEY_PREFIX, ""))
                    
        return matching_keys
        
    def get_keys_by_pattern(self, pattern: str, collection_name: str) -> list:
        cursor = '0'
        redis_keys = []

        while cursor != 0:
            cursor, keys = self.redis.scan(cursor=cursor, match=pattern)
            redis_keys.extend(keys)

        return redis_keys

    def close(self) -> None:
        print("Redis client destroyed.")
        self.redis.close()
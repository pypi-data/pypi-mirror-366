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

class DatabaseException(Exception):
    """Base exception for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseException):
    """Exception raised for errors in connecting to the database."""
    def __init__(self, message="Failed to connect to the database."):
        super().__init__(message)

class DatabaseQueryError(DatabaseException):
    """Exception raised for errors in executing a database query."""
    def __init__(self, query, message="Error executing query."):
        self.query = query
        full_message = f"{message} Query: {query}"
        super().__init__(full_message)
        
class DuplicateKeyError(DatabaseException):
    """Exception raised when trying to insert a duplicate key."""
    def __init__(self, key, message="Duplicate key error."):
        self.key = key
        full_message = f"{message} Key: {key}"
        super().__init__(full_message)
        
class KeyNotFoundError(DatabaseException):
    """Exception raised when a key is not found in the database."""
    def __init__(self, key, message="Key not found."):
        self.key = key
        full_message = f"{message} Key: {key}"
        super().__init__(full_message)
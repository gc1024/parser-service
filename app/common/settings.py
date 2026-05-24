#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import os
import json
import secrets
import logging
from datetime import date

from app.common.constants import RAG_FLOW_SERVICE_NAME
from app.common.file_utils import get_project_base_directory
from app.common.config_utils import get_base_config, decrypt_database_config
from app.common.misc_utils import pip_install_torch
from app.common.constants import SVR_QUEUE_NAME, Storage

import app.rag.utils
import app.rag.utils.es_conn
import app.rag.utils.infinity_conn
import app.rag.utils.ob_conn
import app.rag.utils.opensearch_conn
from app.rag.utils.azure_sas_conn import RAGFlowAzureSasBlob
from app.rag.utils.azure_spn_conn import RAGFlowAzureSpnBlob
from app.rag.utils.gcs_conn import RAGFlowGCS
from app.rag.utils.minio_conn import RAGFlowMinio
from app.rag.utils.opendal_conn import OpenDALStorage
from app.rag.utils.redis_conn import REDIS_CONN
from app.rag.utils.s3_conn import RAGFlowS3
from app.rag.utils.oss_conn import RAGFlowOSS

from app.rag.nlp import search

# Memory module removed - use stub connections
class MemoryStubConnection:
    """Stub for memory module connections"""
    pass

memory_es_conn_stub = type('obj', (object,), {'ESConnection': lambda: MemoryStubConnection()})
memory_infinity_conn_stub = type('obj', (object,), {'InfinityConnection': lambda: MemoryStubConnection()})
memory_ob_conn_stub = type('obj', (object,), {'OBConnection': lambda: MemoryStubConnection()})

TIMEZONE = os.getenv("TZ", "Asia/Shanghai")

LLM = None
LLM_FACTORY = None
LLM_BASE_URL = None
CHAT_MDL = ""
EMBEDDING_MDL = ""
RERANK_MDL = ""
ASR_MDL = ""
IMAGE2TEXT_MDL = ""


CHAT_CFG = ""
SYSTEM_SETTINGS = ""
PROMPT_CACHE = {}

# Retrieve storage configuration
# Get RAGFLOW conf
SVR_QUEUE_NAME = get_base_config("task_executor", {}).get("message_queue_type", "redis")

HOST_IP = os.getenv("HOST_IP", "0.0.0.0")
HOST_PORT = int(os.getenv("HOST_PORT", "9380"))

CONTAINER_NAME = os.getenv("CONTAINER_NAME", "ragflow")
MAX_PACKAGE_NUM = int(os.getenv("MAX_PACKAGE_NUM", "100000"))

DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mysql")
DATABASE_NAME = os.getenv("DATABASE_NAME", "rag_flow")
DATABASE = {}

DEPLOY_TYPE = os.getenv("DEPLOY_TYPE")

STORAGE_IMPL_TYPE = os.getenv("STORAGE_IMPL_TYPE")

# Switch storage type
def get_storage_type():
    global STORAGE_IMPL_TYPE
    STORAGE_IMPL_TYPE = os.getenv("STORAGE_IMPL_TYPE")
    config = get_base_config("obj", {}).get("storage_type", Storage.MINIO)
    if STORAGE_IMPL_TYPE is None:
        STORAGE_IMPL_TYPE = config
    return STORAGE_IMPL_TYPE

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))

def init_settings():
    global CHAT_CFG, SYSTEM_SETTINGS, LLM, LLM_FACTORY, LLM_BASE_URL, CHAT_MDL, EMBEDDING_MDL, RERANK_MDL, ASR_MDL, IMAGE2TEXT_MDL
    import time
    start_t = time.time()
    try:
        CHAT_CFG = get_base_config("user_default_llm", {})
        SYSTEM_SETTINGS = get_base_config("system_settings", {})
        LLM_FACTORY = os.getenv("LLM_FACTORY", None)
        LLM_BASE_URL = os.getenv("LLM_BASE_URL", None)
        CHAT_MDL = os.getenv("CHAT_MDL", "")
        EMBEDDING_MDL = os.getenv("EMBEDDING_MDL", "")
        RERANK_MDL = os.getenv("RERANK_MDL", "")
        ASR_MDL = os.getenv("ASR_MDL", "")
        IMAGE2TEXT_MDL = os.getenv("IMAGE2TEXT_MDL", "")

        GITHUB_OAUTH = get_base_config("oauth", {}).get("github")
        FEISHU_OAUTH = get_base_config("oauth", {}).get("feishu")
        OAUTH_CONFIG = get_base_config("oauth", {})

        global DOC_ENGINE, DOC_ENGINE_INFINITY, DOC_ENGINE_OCEANBASE, docStoreConn, ES, OB, OS, INFINITY
        DOC_ENGINE = os.environ.get("DOC_ENGINE", "elasticsearch").strip()
        DOC_ENGINE_INFINITY = (DOC_ENGINE.lower() == "infinity")
        DOC_ENGINE_OCEANBASE = (DOC_ENGINE.lower() == "oceanbase")
        lower_case_doc_engine = DOC_ENGINE.lower()
        if lower_case_doc_engine == "elasticsearch":
            ES = get_base_config("es", {})
            docStoreConn = app.rag.utils.es_conn.ESConnection()
        elif lower_case_doc_engine == "infinity":
            INFINITY = get_base_config("infinity", {
                "uri": "infinity:23817",
                "postgres_port": 5432,
                "db_name": "default_db"
            })
            docStoreConn = app.rag.utils.infinity_conn.InfinityConnection()
        elif lower_case_doc_engine == "opensearch":
            OS = get_base_config("os", {})
            docStoreConn = app.rag.utils.opensearch_conn.OSConnection()
        elif lower_case_doc_engine == "oceanbase":
            OB = get_base_config("oceanbase", {})
            docStoreConn = app.rag.utils.ob_conn.OBConnection()
        elif lower_case_doc_engine == "seekdb":
            OB = get_base_config("seekdb", {})
            docStoreConn = app.rag.utils.ob_conn.OBConnection()
        else:
            raise Exception(f"Not supported doc engine: {DOC_ENGINE}")

        global msgStoreConn
        # use the same engine for message store
        if DOC_ENGINE == "elasticsearch":
            ES = get_base_config("es", {})
            msgStoreConn = memory_es_conn_stub.ESConnection()
        elif DOC_ENGINE == "infinity":
            INFINITY = get_base_config("infinity", {
                "uri": "infinity:23817",
                "postgres_port": 5432,
                "db_name": "default_db"
            })
            msgStoreConn = memory_infinity_conn_stub.InfinityConnection()
        elif lower_case_doc_engine in ["oceanbase", "seekdb"]:
            msgStoreConn = memory_ob_conn_stub.OBConnection()

        global AZURE, S3, MINIO, OSS, GCS
        if STORAGE_IMPL_TYPE in ['AZURE_SPN', 'AZURE_SAS']:
            AZURE = get_base_config("azure", {})
        elif STORAGE_IMPL_TYPE == 'AWS_S3':
            S3 = get_base_config("s3", {})
        elif STORAGE_IMPL_TYPE == 'MINIO':
            MINIO = get_base_config("minio", {})
        elif STORAGE_IMPL_TYPE == 'OSS':
            OSS = get_base_config("oss", {})
        elif STORAGE_IMPL_TYPE == 'GCS':
            GCS = get_base_config("gcs", {})
        elif STORAGE_IMPL_TYPE == 'OPENDAL':
            OPENDAL = get_base_config("opendal", {})

        logging.info(f"init_settings completed in {time.time() - start_t:.2f}s")
    except Exception as e:
        logging.exception("init_settings failed")
        raise

def get_secret_key():
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        SECRET_KEY_PATH = os.path.join(get_project_base_directory(), "conf", "private.pem")
        if os.path.exists(SECRET_KEY_PATH):
            with open(SECRET_KEY_PATH, "rb") as f:
                secret_key = f.read()
        else:
            secret_key = secrets.token_hex(32)
        os.environ["SECRET_KEY"] = secret_key
    return secret_key

def print_rag_settings():
    logging.info(f"DOC_ENGINE: {os.environ.get('DOC_ENGINE', 'elasticsearch')}")
    logging.info(f"STORAGE_IMPL_TYPE: {STORAGE_IMPL_TYPE}")

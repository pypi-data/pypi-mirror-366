from typing import TYPE_CHECKING, Optional, Sequence, Union

from skt.vault_utils import get_secrets

if TYPE_CHECKING:
    import pandas as pd
    from hmsclient import hmsclient
    from pyarrow import fs
    from pyspark import SparkConf, SparkContext
    from pyspark.sql import SparkSession


def get_hms():
    from hmsclient import hmsclient

    s = get_secrets(path="ye/hivemetastore")
    host = s["ip"]
    port = s["port"]
    client = hmsclient.HMSClient(host=host, port=port)
    client.open()
    return client


def get_hive_conn():
    from pyhive import hive

    hiveserver2 = get_secrets(path="ye/hiveserver2")
    host = hiveserver2["ip"]
    port = hiveserver2["port"]
    user = hiveserver2["user"]
    conn = hive.connect(host, port=port, username=user)
    return conn


def get_hdfs_conn():
    import os
    import pyarrow

    os.environ["ARROW_LIBHDFS_DIR"] = "/usr/hdp/3.0.1.0-187/usr/lib"
    conn = pyarrow.hdfs.connect(user="airflow")
    return conn


def get_sqlalchemy_engine():
    from sqlalchemy import create_engine

    hiveserver2 = get_secrets(path="ye/hiveserver2")
    host = hiveserver2["ip"]
    port = hiveserver2["port"]
    user = hiveserver2["user"]
    return create_engine(f"hive://{user}@{host}:{port}/tmp")


def get_pkl_from_hdfs(pkl_path):
    import pickle

    conn = get_hdfs_conn()
    byte_object = conn.cat(f"{pkl_path}")
    pkl_object = pickle.loads(byte_object)
    return pkl_object


def is_in_notebook():
    try:
        from IPython import get_ipython

        if get_ipython().__class__.__name__ == "ZMQInteractiveShell":
            return True
        else:
            return False
    except (NameError, ModuleNotFoundError):
        return False


def _spark_context_to_repr_html(sc: "SparkContext") -> str:
    import os

    if os.environ.get("JUPYTERHUB_USER"):
        ui_web_url = sc.uiWebUrl

    else:
        history_server_url = os.environ.get("SPARK_HISTORY_SERVER_URL", "http://spark.yks.sktai.io")
        ui_web_url = f"{history_server_url}/history/{sc.applicationId}"

    return f"""
        <div>
            <p><b>SparkContext</b></p>

            <p><a href="{ui_web_url}">Spark UI</a></p>

            <dl>
              <dt>Version</dt>
                <dd><code>v{sc.version}</code></dd>
              <dt>Master</dt>
                <dd><code>{sc.master}</code></dd>
              <dt>AppName</dt>
                <dd><code>{sc.appName}</code></dd>
            </dl>
        </div>
        """


def get_spark(
    scale: int = 0,
    queue: Optional[str] = None,
    jars: Optional[Union[Sequence[str], str]] = None,
    conf: Optional["SparkConf"] = None,
) -> "SparkSession":
    import json
    import os
    import uuid
    import warnings

    from pyspark.conf import SparkConf
    from pyspark.sql import SparkSession

    if queue:
        warnings.warn("Queue is unsupported not implemented yet")

    default = {
        "spark.app.name": f"skt-{os.environ.get('USER', 'default')}-{str(uuid.uuid4())}",
        "spark.driver.cores": "1",
        "spark.executor.cores": "1",
    }

    if jars:
        if isinstance(jars, str):
            default["spark.jars"] = jars
        else:
            default["spark.jars"] = ",".join(jars)

    if not scale:
        default["spark.driver.memory"] = "8g"
        default["spark.driver.maxResultSize"] = "6g"
        default["spark.executor.memory"] = "8g"
        default["spark.executor.instances"] = "8"
    elif 1 <= scale <= 4:
        default["spark.driver.memory"] = f"{scale * 8}g"
        default["spark.driver.maxResultSize"] = f"{scale * 4}g"
        default["spark.executor.memory"] = f"{scale * 3}g"
        default["spark.executor.instances"] = str(scale * 8)
    elif scale < 9:
        default["spark.driver.memory"] = "8g"
        default["spark.driver.maxResultSize"] = "8g"
        default["spark.executor.memory"] = f"{min(2**scale, 200)}g"
        default["spark.executor.instances"] = "32"
    else:
        raise ValueError("Invalid scale")

    if not conf:
        conf = SparkConf()

    for key, value in default.items():
        if not conf.get(key):
            conf.set(key, value)

    task_group = [
        {
            "name": "executor",
            "minMember": int(conf.get("spark.executor.instances")),
            "minResource": {
                "cpu": conf.get("spark.executor.cores"),
                "memory": f'{int(conf.get("spark.executor.memory").replace("g","")) * 1.1}Gi',  # JVM Overhead
            },
            "nodeSelector": {
                "role/spark": None,
                "zone": "cpu.pool",
            },
            "tolerations": [],
            "affinity": {},
            "topologySpreadConstraints": [],
        }
    ]

    conf = (
        conf.set("spark.kubernetes.executor.annotation.yunikorn.apache.org/task-group-name", "executor")
        .set("spark.kubernetes.executor.annotation.yunikorn.apache.org/task-groups", json.dumps(task_group))
        .set(
            "spark.kubernetes.executor.annotation.yunikorn.apache.org/schedulingPolicyParameters",
            "placeholderTimeoutInSeconds=60 gangSchedulingStyle=Hard",
        )
    )

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    if is_in_notebook():
        from IPython.display import HTML, display

        display(HTML(_spark_context_to_repr_html(spark.sparkContext)))

    return spark


def hive_execute(query):
    conn = get_hive_conn()
    c = conn.cursor()
    c.execute(query)
    c.close()
    conn.close()


def hive_get_result(query):
    conn = get_hive_conn()
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    c.close()
    conn.close()
    return result


def hive_to_pandas(query, scale=0):
    if scale == 1:
        import pandas

        conn = get_hive_conn()
        df = pandas.read_sql(query, conn)
        df.info()
        conn.close()
        return df

    import uuid

    tmp_id = str(uuid.uuid4()).replace("-", "_")
    ctas = f"CREATE TABLE dumbo.{tmp_id} stored as parquet as {query}"
    conn = get_hive_conn()
    c = conn.cursor()
    c.execute("set parquet.column.index.access=false")
    c.execute(ctas)
    df = parquet_to_pandas(f"/warehouse/tablespace/managed/hive/dumbo.db/{tmp_id}")
    c.execute(f"DROP TABLE dumbo.{tmp_id}")
    c.close()
    conn.close()
    return df


def parquet_to_pandas(hdfs_path):
    import os
    from pyarrow import fs
    from pyarrow import parquet
    from skt.ye import get_hdfs_conn

    # Load hadoop environment
    get_hdfs_conn().close()

    os.environ["ARROW_LIBHDFS_DIR"] = "/usr/hdp/3.0.1.0-187/usr/lib"
    hdfs = fs.HadoopFileSystem("ye.sktai.io", 8020, user="airflow")
    if hdfs_path.startswith("hdfs://yellowelephant/"):
        hdfs_path = hdfs_path[21:]
    df = parquet.read_table(hdfs_path, filesystem=hdfs).to_pandas()
    df.info()
    return df


def pandas_to_parquet(pandas_df, hdfs_path, spark):
    df = spark.createDataFrame(pandas_df)
    df.write.mode("overwrite").parquet(hdfs_path)


def slack_send(
    text="This is default text",
    username="SKT",
    channel="#leavemealone",
    icon_emoji=":large_blue_circle:",
    blocks=None,
    dataframe=False,
    adot=False,
):
    import requests
    from skt.vault_utils import get_secrets

    if dataframe:
        from tabulate import tabulate

        text = "```" + tabulate(text, tablefmt="simple", headers="keys") + "```"

    token = (
        get_secrets("airflow_k8s/adot_slack/slack_alarmbot_token")["token"]
        if adot
        else get_secrets("slack")["bot_token"]["airflow"]
    )
    proxy = get_secrets("proxy")["proxy"]
    proxies = {
        "http": proxy,
        "https": proxy,
    }
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "Authorization": f"Bearer {token}",
    }
    json_body = {
        "username": username,
        "channel": channel,
        "text": text,
        "blocks": blocks,
        "icon_emoji": icon_emoji,
    }
    r = requests.post(
        "https://www.slack.com/api/chat.postMessage",
        proxies=proxies,
        headers=headers,
        json=json_body,
    )
    r.raise_for_status()
    if not r.json()["ok"]:
        raise Exception(r.json())


def send_email(subject, text, send_from, send_to, attachment=None):
    """
    :param str attachment: Attachment to send as .txt file with email
    """
    import smtplib
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import formatdate
    from skt.vault_utils import get_secrets

    c = get_secrets(path="mail")
    host, port = c["smtp_host"], c["smtp_port"]
    msg = MIMEMultipart()
    msg["From"] = send_from
    msg["To"] = send_to
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject
    msg.attach(MIMEText(text))

    if attachment:
        part = MIMEApplication(attachment, NAME=subject)
        part.add_header("Content-Disposition", f"attachment; filename={subject}.txt")
        msg.attach(part)

    with smtplib.SMTP(host, port) as smtp:
        return smtp.sendmail(send_from, send_to.split(","), msg.as_string())


def get_github_util():
    from skt.github_utils import GithubUtil

    github_token = get_secrets("github/sktaiflow")["token"]
    proxy = get_secrets("proxy")["proxy"]
    proxies = {
        "http": proxy,
        "https": proxy,
    }
    g = GithubUtil(github_token, proxies)
    return g


def _write_to_parquet_via_spark(pandas_df, hdfs_path):
    spark = get_spark()
    spark_df = spark.createDataFrame(pandas_df)
    spark_df.write.mode("overwrite").parquet(hdfs_path)


def _write_to_parquet(pandas_df, hdfs_path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    # Read Parquet INT64 timestamp issue:
    # https://issues.apache.org/jira/browse/HIVE-21215
    if "datetime64[ns]" in pandas_df.dtypes.tolist():
        _write_to_parquet_via_spark(pandas_df, hdfs_path)
        return

    pa_table = pa.Table.from_pandas(pandas_df)
    hdfs_conn = get_hdfs_conn()
    try:
        pq.write_to_dataset(pa_table, root_path=hdfs_path, filesystem=hdfs_conn)
    finally:
        hdfs_conn.close()


def _write_df(pandas_df, schema_name, table_name, hdfs_path, engine, cursor, tmp_table_name):
    import sqlalchemy.exc

    cursor.execute(f"drop table if exists {schema_name}.{tmp_table_name}")
    try:
        pandas_df.to_sql(tmp_table_name, engine, schema=schema_name, if_exists="replace", index=False)
    except sqlalchemy.exc.ProgrammingError:
        # Hive bulk insert issue:
        # https://github.com/dropbox/PyHive/issues/343
        pass

    cursor.execute(f"drop table if exists {schema_name}.{table_name}")
    if hdfs_path is None:
        cursor.execute(
            f"""create table {schema_name}.{table_name}
                           like {schema_name}.{tmp_table_name}
                           stored as parquet"""
        )
        cursor.execute(f"show create table {schema_name}.{table_name}")
        result = cursor.fetchall()
        managed_hdfs_path = list(filter(lambda row: row[0].strip().find("hdfs://") == 1, result))[0][0].strip()[1:-1]
        _write_to_parquet(pandas_df, managed_hdfs_path)
    else:
        cursor.execute(
            f"""create external table {schema_name}.{table_name}
                           like {schema_name}.{tmp_table_name}
                           stored as parquet
                           location '{hdfs_path}'"""
        )


def write_df_to_hive(pandas_df, schema_name, table_name, hdfs_path=None):
    """
    Exports a Panadas dataframe into a table in Hive.

    Example:
    write_df_to_hive(pandas_df1, "my_schema", "my_table1")
    write_df_to_hive(pandas_df2, "my_schema", "my_table2")
    write_df_to_hive(pandas_df1, "my_schema", "my_table3",
            hdfs_path="hdfs://.../my_schema.db/my_table1")

    Parameters
    ----------
    pandas_df : an ojbect of Pandas Dataframe
    schema_name : str
        A target schema name of Hive
    table_name : str
        A target table name of Hive
    hdfs_path : str, default None
        A path of Hadoop file system as an optional parameter.
        It will be used to create an external table. If hdfs_path
        is not None, data in the dataframe will not be converted.
        A metadata in the dataframe is just used to create a Hive
        table.
    """
    engine = get_sqlalchemy_engine()
    conn = get_hive_conn()
    cursor = conn.cursor()

    import hashlib

    tmp_table_name = hashlib.sha1(str(f"{schema_name}.{table_name}").encode("utf-8")).hexdigest()

    try:
        _write_df(pandas_df, schema_name, table_name, hdfs_path, engine, cursor, tmp_table_name)
    finally:
        cursor.execute(f"drop table if exists {schema_name}.{tmp_table_name}")
        cursor.close()
        conn.close()

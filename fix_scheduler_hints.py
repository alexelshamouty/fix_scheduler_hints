import itertools
import json
import subprocess
import sys

import pymysql

# In our infrastructure we are using vault. probably should make this a bit more generic but yeah...
credentials = json.loads(
    subprocess.check_output(["vault", "read", "-format", "json", "secret/mysql/nova"])
)


def empty_scheduler_hints(row):
    information = json.loads(row[1])
    if not information["nova_object.data"]["instance_group"]:
        return False
    if not information["nova_object.data"]["scheduler_hints"]:
        return True
    return False


def fix(conn, row):
    information = json.loads(row[1])
    instance_uuid = row[0]
    with conn.cursor() as cur:
        cur.execute(
            "select uuid from instance_groups inner join instance_group_member on instance_groups.id=instance_group_member.group_id where instance_group_member.instance_uuid= %s;",
            instance_uuid,
        )
        server_group = list(cur.fetchone())
        if server_group:
            print("Fixing the grup")
            server_group = {"group": [server_group[0]]}
            information["nova_object.data"]["scheduler_hints"] = server_group
            print(information)
            cur.execute(
                "update request_specs set spec = %s where instance_uuid = %s;",
                (json.dumps(information), instance_uuid),
            )
            cur.commit()
            return server_group
    return None


def fix_instance(instance):
    with pymysql.connect(
        host=MYSQL_HOST,
        user=credentials["data"]["user"],
        password=credentials["data"]["password"],
        db="novaapi",
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select instance_uuid,spec from request_specs where instance_uuid= %s",
                instance,
            )
            print(cur._last_executed)
            for row in cur.fetchall():
                if empty_scheduler_hints(row):
                    print(f"Instance {row[0]} will be fixed")
                    # fix(conn,row)


if __name__ == "__main__":
    MYSQL_HOST = sys.argv[1]
    fix_instance(sys.argv[2])

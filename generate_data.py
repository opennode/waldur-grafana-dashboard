import datetime
import random

from dateutil.relativedelta import relativedelta

from influxdb import InfluxDBClient


def get_points():
    now = datetime.datetime.now()
    points = []
    for i in range(200):
        timestamp = now - relativedelta(days=i)
        states = {
            'erred': random.randint(1, 5),
            'online': random.randint(1, 20),
            'offline': random.randint(1, 20),
            'provisioning': random.randint(1, 10),
        }

        for state, count in states.items():
            points.append({
                'measurement': 'openstack_instance_runtime_state',
                'time': timestamp,
                'tags': {
                    'state': state,
                },
                'fields': {
                    'count': count,
                }
            })

        vcpu_usage = random.randint(1, 200)
        vcpu_limit = vcpu_usage + random.randint(1, 200)

        ram_usage = vcpu_usage * 1024 * random.randint(1, 3)
        ram_limit = ram_usage + random.randint(1, 200*1024)

        volumes_usage = vcpu_usage + random.randint(1, 200)
        volumes_limit = volumes_usage + random.randint(1, 200)

        snapshots_usage = vcpu_usage + random.randint(1, 200)
        snapshots_limit = snapshots_usage + random.randint(1, 200)

        storage_usage = volumes_usage + snapshots_usage
        storage_limit = volumes_limit + snapshots_limit

        volumes_size_usage = volumes_usage * random.randint(1, 5) * 1024
        volumes_size_limit = volumes_size_usage + random.randint(100, 500) * 1024

        snapshots_size_usage = snapshots_usage * random.randint(1, 5) * 1024
        snapshots_size_limit = snapshots_size_usage + random.randint(100, 500) * 1024

        quotas_map = {
            'vcpu_usage': vcpu_usage,
            'vcpu_limit': vcpu_limit,

            'ram_usage': ram_usage,
            'ram_limit': ram_limit,

            'volumes_usage': volumes_usage,
            'volumes_limit': volumes_limit,

            'snapshots_usage': snapshots_usage,
            'snapshots_limit': snapshots_limit,

            'storage_usage': storage_usage,
            'storage_limit': storage_limit,

            'volumes_size_usage': volumes_size_usage,
            'volumes_size_limit': volumes_size_limit,

            'snapshots_size_usage': snapshots_size_usage,
            'snapshots_size_limit': snapshots_size_limit,
        }

        quota_names = sorted(set(name.replace('_usage', '').replace('_limit', '')
                                 for name in quotas_map.keys()))

        for name in quota_names:
            points.append({
                'measurement': 'openstack_%s' % name,
                'time': timestamp,
                'fields': {
                    'limit': quotas_map['%s_limit' % name],
                    'usage': quotas_map['%s_usage' % name],
                }
            })

    return points


def main():
    client = InfluxDBClient(database='playground')
    points = get_points()
    client.write_points(points)


if __name__ == '__main__':
    main()

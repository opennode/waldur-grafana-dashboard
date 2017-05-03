import datetime
import random

from dateutil.relativedelta import relativedelta

from influxdb import InfluxDBClient


providers = ('east-farm', 'west-farm', 'north-farm', 'south-farm')
resource_types = ('vm', 'vpc', 'volume', 'snapshot')


def get_timestamps(count):
    points = []
    now = datetime.datetime.now()
    for i in range(count):
        points.append(now - relativedelta(days=i))
    return points


def get_instances_by_state():
    points = []
    for timestamp in get_timestamps(200):
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
    return points


def get_openstack_quotas():
    points = []
    for timestamp in get_timestamps(200):
        vcpu_usage = random.randint(1, 200)
        vcpu_limit = vcpu_usage + random.randint(1, 200)

        ram_usage = vcpu_usage * 1024 * random.randint(1, 3)
        ram_limit = ram_usage + random.randint(1, 200 * 1024)

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


def get_total_cost():
    points = []

    for timestamp in get_timestamps(200):
        for provider in providers:
            points.append({
                'measurement': 'total_cost',
                'time': timestamp,
                'tags': {
                    'provider': provider,
                },
                'fields': {
                    'value': random.randint(500, 1000)
                }
            })
    return points


def get_events():
    points = []
    i = 0
    for timestamp in get_timestamps(200):
        if random.randint(1, 12) < 4:
            i += 1
            provider = random.choice(providers)
            resource_type = random.choice(resource_types)
            points.append({
                'measurement': 'events',
                'time': timestamp,
                'tags': {
                    'title': 'Resource #%d created' % i,
                    'tags': ','.join([provider, resource_type])
                },
                'fields': {
                    'value': 0
                }
            })
    return points


def get_points():
    points = []
    points.extend(get_instances_by_state())
    points.extend(get_openstack_quotas())
    points.extend(get_total_cost())
    points.extend(get_events())
    print points
    return points


def main():
    client = InfluxDBClient(database='playground')
    points = get_points()
    client.write_points(points)


if __name__ == '__main__':
    main()

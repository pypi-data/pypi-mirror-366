import hashlib
import re
import uuid

from django.apps import apps
from django.db import connection
from django.db.models import QuerySet, Manager
from django.core.exceptions import FieldError

from dcim.models import Device
from ipam.models import IPAddress
from netpicker.client import get_netpicker_devices
from netpicker import models


re_select = re.compile(r'\[([_]*?[:\w]+)\s*([~^$*]??=)\s*([^]\s]+)\s*([is])??]\s*')

re_step = re.compile(r'(?P<attr>[a-z_]\w*?)\s*'
                     r'(?P<selector>(?:\[[_]*?[:\w]+\s*[$^*~]??=\s*[^]\s]+\s*[is]??]\s*)*?)'
                     r'(?:\[(?P<reversed>-)??(?P<index>\d+)])??')

selector_pattern = {
    '=': ['exact', 'iexact'],
    '^=': ['startswith', 'istartswith'],
    '$=': ['endswith', 'istartswith'],
    '*=': ['contains', 'icontains'],
}

ipe = 'invalid path element '


def traverse(obj, path):
    steps = [s.strip() for s in path.split('.')]
    if not (len(steps) > 1 and (steps.pop(0) == '')):
        raise ValueError('invalid path')
    result = obj
    attr = None
    for step in steps:
        if (m := re_step.fullmatch(step)) is None:
            raise ValueError(f"{ipe}`{step}`")
        gd = m.groupdict()
        _, attr = attr, gd['attr']
        if not isinstance(result, (Manager, QuerySet)):
            try:
                result = getattr(result, attr)
            except AttributeError as exc:
                raise ValueError(f"{ipe}`{step}` ({exc.args[0]})")
        elif result:
            # move onto next object type
            target_model = getattr(result[0], attr).model
            relations = target_model._meta.related_objects
            backref = next((rel for rel in relations
                            if rel.field.attname == attr and isinstance(result[0], rel.related_model)), None)
            if backref:
                linkage = backref.accessor_name
            else:
                fwd_items = target_model._meta._forward_fields_map.items()
                linkage = next((k for k, v in fwd_items
                                if v.related_model and isinstance(result[0], v.related_model)), None)
            result = target_model.objects.filter(**{f"{linkage}__in": result})
        index = gd['index']
        # if (index is not None) != isinstance(result, Manager):
        #     raise ValueError(f"{ipe}`{step}`")

        if isinstance(result, (Manager, QuerySet)):
            selector = gd['selector']
            for field, op, value, casing in re.findall(re_select, selector):
                field = field.replace(':', '__')
                django_op = selector_pattern.get(op)[int(bool(casing))]
                django_val = value.strip('"')
                django_field = f"{field}__{django_op}"
                try:
                    result = result.filter(**{django_field: django_val})
                except FieldError as exc:
                    raise ValueError(f"{ipe}`{step}` ({exc.args[0]})")
            if index:
                if index.isdigit():
                    ndx = int(index)
                    result = result.all()
                    if gd['reversed']:
                        result = result.reverse()
                        ndx -= 1
                    result = result[ndx]
                else:
                    raise ValueError(f"{ipe}`{step}`")
    return result


def generate_random_string():
    # Generate a UUID and convert it to a string
    unique_id = str(uuid.uuid4())

    # Get the UTF-8 encoded bytes of the UUID string
    encoded_id = unique_id.encode('utf-8')

    # Create a SHA256 hash of the encoded UUID
    sha256_hash = hashlib.sha256(encoded_id)

    # Convert the SHA256 hash to a hexadecimal string
    hashed_string = sha256_hash.hexdigest()

    return hashed_string


def get_logo(**kwargs):
    from . import netpicker_app
    return netpicker_app.logo(**kwargs)


def ip_str(ipaddress: IPAddress) -> str:
    return str(ipaddress.address.ip)


def get_device_ip(device: Device) -> str:
    ipaddress = device.primary_ip or device.primary_ip4 or device.primary_ip6
    return ip_str(ipaddress) if ipaddress else None


def get_settings(request):
    if (settings := getattr(request, 'settings', get_settings)) is get_settings:
        if settings := models.Setting.objects.first():
            if settings.api_key == models.Setting.unset_api_key:
                settings = None
        request.settings = settings
    return settings


#########


def get_runnable_devices_query(target_platforms: list[str] | None = None):
    try:
        apps.get_app_config('slurpit')
    except LookupError:
        pass

    where = {}
    if target_platforms:
        table = {ord('?'): '(.)', ord('*'): '(.*?)'}
        regex = '|'.join((p.translate(table) for p in target_platforms))
        where = dict(netpickers__platform__regex=f"^(?:{regex})$")
    q_runnables = Device.objects.filter(**where)
    return models.ProxyQuerySet(model=Device, data=list(q_runnables))

    # if slurp'it is installed it provides more convenient way of looking up the devices


def reload_devices():
    ND = models.NetpickerDevice
    # 1. clear list
    ND.objects.all().delete()
    # 2. insert all Netpicker has to offer
    data = get_netpicker_devices()
    g_np_dev = (ND(ipaddress=ip, platform=platform, tenant=tenant) for ip, platform, tenant in data)
    ND.objects.bulk_create(g_np_dev)
    # 3. delete goers
    MD = models.MappedDevice
    qs_goers = MD.objects.raw("""
        select d.id from netpicker_mappeddevice as nd left outer join netpicker_netpickerdevice d
        on nd.tenant = d.tenant and nd.ipaddress = d.ipaddress and nd.platform = d.platform
        where d.ipaddress is null
    """)
    MD.objects.filter(id__in=qs_goers).delete()
    # 4. insert comers
    qs_comers = ND.objects.raw("""
        select d.id, d.ipaddress, d.platform, d.tenant
        from netpicker_netpickerdevice d left outer join netpicker_mappeddevice nd
        on nd.tenant = d.tenant and nd.ipaddress = d.ipaddress and nd.platform = d.platform
        where nd.ipaddress is null
    """)

    # TODO: optimize for inserting netbox device with bulk_create
    g_comers = (MD(ipaddress=d.ipaddress, platform=d.platform, tenant=d.tenant) for d in qs_comers)
    MD.objects.bulk_create(g_comers)

    qs_matchers = """
        update netpicker_mappeddevice
        set netbox_id = t.netbox_id
        from (
          select d.id as mapped_id, dcim_device.id netbox_id
          from netpicker_mappeddevice d left outer join (
            dcim_device join ipam_ipaddress
                on ipam_ipaddress.id = dcim_device.primary_ip4_id or ipam_ipaddress.id = dcim_device.primary_ip6_id)
            on d.ipaddress = host(ipam_ipaddress.address)
          where d.netbox_id is null and dcim_device.id is not null
        ) t
        where id = t.mapped_id
    """

    with connection.cursor() as cursor:
        cursor.execute(qs_matchers)

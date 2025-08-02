from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin, TenantColumn
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from .models import PhoneNumber, PhoneNumberRange, Sim, SimAdmin


AVAILABLE_LABEL = mark_safe('<span class="badge text-bg-success">Available</span>')


class PhoneNumberRangeTable(TenancyColumnsMixin, NetBoxTable):

    id = tables.LinkColumn()

    status = columns.ChoiceFieldColumn(verbose_name=_("Status"), default=AVAILABLE_LABEL)

    country_code = columns.ChoiceFieldColumn(verbose_name=_("Country Code"), default=AVAILABLE_LABEL)

    tags = columns.TagColumn(url_name="ipam:ipaddress_list")

    voice_cicruit = tables.Column(verbose_name=_("Cicruit"), linkify=True)

    class Meta(NetBoxTable.Meta):
        model = PhoneNumberRange
        fields = (
            "pk",
            "id",
            "status",
            "size",
            "country_code",
            "start_number",
            "tenant",
            "voice_cicruit",
            "description",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = (
            "pk",
            "id",
            "start_number",
            "size",
            "country_code",
            "status",
            "tenant",
            "voice_cicruit",
            "description",
        )
        row_attrs = {
            "class": lambda record: "success" if not isinstance(record, PhoneNumberRange) else "",
        }


class PhoneNumberTable(TenancyColumnsMixin, NetBoxTable):
    number = tables.LinkColumn()

    status = columns.ChoiceFieldColumn(verbose_name=_("Status"), default=AVAILABLE_LABEL)

    country_code = columns.ChoiceFieldColumn(verbose_name=_("Country Code"), default=AVAILABLE_LABEL)

    tags = columns.TagColumn(url_name="ipam:ipaddress_list")

    class Meta(NetBoxTable.Meta):
        model = PhoneNumber
        fields = (
            "pk",
            "id",
            "number",
            "status",
            "country_code",
            "tenant",
            "voice_cicruit",
            "sim",
            "description",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = (
            "pk",
            "number",
            "country_code",
            "status",
            "voice_cicruit",
            "sim",
            "tenant",
            "description",
        )
        row_attrs = {
            "class": lambda record: "success" if not isinstance(record, PhoneNumber) else "",
        }


class SimTable(TenancyColumnsMixin, NetBoxTable):
    sim_id = tables.LinkColumn()

    provider = tables.Column(verbose_name=_("Provider"), linkify=True)
    provider_account = tables.Column(linkify=True, verbose_name=_("Account"))

    tags = columns.TagColumn(url_name="ipam:ipaddress_list")

    class Meta(NetBoxTable.Meta):
        model = Sim

        fields = (
            "pk",
            "sim_id",
            "iccid",
            "msisdn",
            "tenant",
            "numeric_value",
            "tags",
            "description",
            "created",
            "last_updated",
            "provider",
            "provider_account",
        )
        default_columns = (
            "pk",
            "sim_id",
            "provider",
            "provider_account",
            "iccid",
            "msisdn",
            "tenant",
            "numeric_value",
            "tags",
            "description",
        )
        row_attrs = {
            "class": lambda record: "success" if not isinstance(record, Sim) else "",
        }


class SimAdminTable(NetBoxTable):
    id = tables.LinkColumn()

    sim = tables.Column(verbose_name=_("SIM"), linkify=True)

    tags = columns.TagColumn(url_name="ipam:ipaddress_list")

    class Meta(NetBoxTable.Meta):
        model = SimAdmin

        fields = (
            "pk",
            "id",
            "sim",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = ("pk", "id", "sim")
        row_attrs = {
            "class": lambda record: "success" if not isinstance(record, Sim) else "",
        }

"""Dataclasses used to hold parsed output from "juju status --format=json"."""

from __future__ import annotations

import dataclasses
from typing import Any

from jubilant import Status as JubilantStatus
from jubilant import _pretty

# For all classes that are identical in Juju 3.x, reuse the classes from Jubilant.
# For classes that differ in Juju 2.9, use the exported definition rather than
# inheriting from the Jubilant one.
from jubilant.statustypes import (
    CombinedStorage,
    ControllerStatus,
    EntityStatus,
    FilesystemAttachment,
    FilesystemAttachments,
    FilesystemInfo,
    LxdProfileContents,
    NetworkInterface,
    OfferStatus,
    RemoteAppStatus,
    RemoteEndpoint,
    StatusInfo,
    StorageAttachments,
    StorageInfo,
    UnitStorageAttachment,
    VolumeAttachment,
    VolumeAttachments,
    VolumeInfo,
)

__all__ = [
    'AppStatus',
    'BranchStatus',
    'CombinedStorage',
    'ControllerStatus',
    'EntityStatus',
    'FilesystemAttachment',
    'FilesystemAttachments',
    'FilesystemInfo',
    'LxdProfileContents',
    'MachineStatus',
    'MeterStatus',
    'ModelStatus',
    'NetworkInterface',
    'OfferStatus',
    'RemoteAppStatus',
    'RemoteEndpoint',
    'Status',
    'StatusInfo',
    'StorageAttachments',
    'StorageInfo',
    'UnitStatus',
    'UnitStorageAttachment',
    'VolumeAttachment',
    'VolumeAttachments',
    'VolumeInfo',
]


@dataclasses.dataclass(frozen=True)
class MeterStatus:
    color: str = ''
    message: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> MeterStatus:
        return cls(
            color=d.get('color') or '',
            message=d.get('message') or '',
        )


@dataclasses.dataclass(frozen=True)
class UnitStatus:
    workload_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    juju_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    meter_status: MeterStatus = dataclasses.field(default_factory=MeterStatus)
    leader: bool = False
    upgrading_from: str = ''
    machine: str = ''
    open_ports: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    public_address: str = ''
    address: str = ''
    provider_id: str = ''
    subordinates: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    branch: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitStatus:
        if 'status-error' in d:
            return cls(
                workload_status=StatusInfo(current='failed', message=d['status-error']),
                juju_status=StatusInfo(current='failed', message=d['status-error']),
            )
        return cls(
            workload_status=(
                StatusInfo._from_dict(d['workload-status'])
                if 'workload-status' in d
                else StatusInfo()
            ),
            juju_status=(
                StatusInfo._from_dict(d['juju-status']) if 'juju-status' in d else StatusInfo()
            ),
            meter_status=(
                MeterStatus._from_dict(d['meter-status']) if 'meter-status' in d else MeterStatus()
            ),
            leader=d.get('leader') or False,
            upgrading_from=d.get('upgrading-from') or '',
            machine=d.get('machine') or '',
            open_ports=d.get('open-ports') or [],
            public_address=d.get('public-address') or '',
            address=d.get('address') or '',
            provider_id=d.get('provider-id') or '',
            subordinates=(
                {k: UnitStatus._from_dict(v) for k, v in d['subordinates'].items()}
                if 'subordinates' in d
                else {}
            ),
            branch=d.get('branch') or '',
        )

    @property
    def is_active(self) -> bool:
        """Report whether the workload status for this unit status is "active"."""
        return self.workload_status.current == 'active'

    @property
    def is_blocked(self) -> bool:
        """Report whether the workload status for this unit status is "blocked"."""
        return self.workload_status.current == 'blocked'

    @property
    def is_error(self) -> bool:
        """Report whether the workload status for this unit status is "error"."""
        return self.workload_status.current == 'error'

    @property
    def is_maintenance(self) -> bool:
        """Report whether the workload status for this unit status is "maintenance"."""
        return self.workload_status.current == 'maintenance'

    @property
    def is_waiting(self) -> bool:
        """Report whether the workload status for this unit status is "waiting"."""
        return self.workload_status.current == 'waiting'


@dataclasses.dataclass(frozen=True)
class AppStatus:
    charm: str
    series: str
    os: str
    charm_origin: str
    charm_name: str
    charm_rev: int
    exposed: bool

    charm_channel: str = ''
    charm_version: str = ''
    charm_profile: str = ''
    can_upgrade_to: str = ''
    scale: int = 0
    provider_id: str = ''
    address: str = ''
    life: str = ''
    app_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    relations: dict[str, list[str]] = dataclasses.field(default_factory=dict)  # type: ignore
    subordinate_to: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    units: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    version: str = ''
    endpoint_bindings: dict[str, str] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AppStatus:
        if 'status-error' in d:
            return cls(
                charm='<failed>',
                series='<failed>',
                os='<failed>',
                charm_origin='<failed>',
                charm_name='<failed>',
                charm_rev=-1,
                exposed=False,
                app_status=StatusInfo(current='failed', message=d['status-error']),
            )
        return cls(
            charm=d['charm'],
            series=d['series'],
            os=d['os'],
            charm_origin=d['charm-origin'],
            charm_name=d['charm-name'],
            charm_rev=d['charm-rev'],
            exposed=d['exposed'],
            charm_channel=d.get('charm-channel') or '',
            charm_version=d.get('charm-version') or '',
            charm_profile=d.get('charm-profile') or '',
            can_upgrade_to=d.get('can-upgrade-to') or '',
            scale=d.get('scale') or 0,
            provider_id=d.get('provider-id') or '',
            address=d.get('address') or '',
            life=d.get('life') or '',
            app_status=(
                StatusInfo._from_dict(d['application-status'])
                if 'application-status' in d
                else StatusInfo()
            ),
            relations=d.get('relations') or {},
            subordinate_to=d.get('subordinate-to') or [],
            units=(
                {k: UnitStatus._from_dict(v) for k, v in d['units'].items()}
                if 'units' in d
                else {}
            ),
            version=d.get('version') or '',
            endpoint_bindings=d.get('endpoint-bindings') or {},
        )

    @property
    def is_active(self) -> bool:
        """Report whether the application status for this app is "active"."""
        return self.app_status.current == 'active'

    @property
    def is_blocked(self) -> bool:
        """Report whether the application status for this app is "blocked"."""
        return self.app_status.current == 'blocked'

    @property
    def is_error(self) -> bool:
        """Report whether the application status for this app is "error"."""
        return self.app_status.current == 'error'

    @property
    def is_maintenance(self) -> bool:
        """Report whether the application status for this app is "maintenance"."""
        return self.app_status.current == 'maintenance'

    @property
    def is_waiting(self) -> bool:
        """Report whether the application status for this app is "waiting"."""
        return self.app_status.current == 'waiting'


@dataclasses.dataclass(frozen=True)
class BranchStatus:
    ref: str = ''
    created: str = ''
    created_by: str = ''
    active: bool = False

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> BranchStatus:
        return cls(
            ref=d.get('ref') or '',
            created=d.get('created') or '',
            created_by=d.get('created-by') or '',
            active=d.get('active') or False,
        )


@dataclasses.dataclass(frozen=True)
class MachineStatus:
    series: str

    juju_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    hostname: str = ''
    dns_name: str = ''
    ip_addresses: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    instance_id: str = ''
    display_name: str = ''
    machine_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    modification_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    network_interfaces: dict[str, NetworkInterface] = dataclasses.field(default_factory=dict)  # type: ignore
    containers: dict[str, MachineStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    constraints: str = ''
    hardware: str = ''
    controller_member_status: str = ''
    ha_primary: bool = False
    lxd_profiles: dict[str, LxdProfileContents] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> MachineStatus:
        if 'status-error' in d:
            return cls(
                series='<failed>',
                juju_status=StatusInfo(current='failed', message=d['status-error']),
                machine_status=StatusInfo(current='failed', message=d['status-error']),
            )
        return cls(
            series=d['series'],
            juju_status=(
                StatusInfo._from_dict(d['juju-status']) if 'juju-status' in d else StatusInfo()
            ),
            hostname=d.get('hostname') or '',
            dns_name=d.get('dns-name') or '',
            ip_addresses=d.get('ip-addresses') or [],
            instance_id=d.get('instance-id') or '',
            display_name=d.get('display-name') or '',
            machine_status=(
                StatusInfo._from_dict(d['machine-status'])
                if 'machine-status' in d
                else StatusInfo()
            ),
            modification_status=(
                StatusInfo._from_dict(d['modification-status'])
                if 'modification-status' in d
                else StatusInfo()
            ),
            network_interfaces=(
                {k: NetworkInterface._from_dict(v) for k, v in d['network-interfaces'].items()}
                if 'network-interfaces' in d
                else {}
            ),
            containers=(
                {k: MachineStatus._from_dict(v) for k, v in d['containers'].items()}
                if 'containers' in d
                else {}
            ),
            constraints=d.get('constraints') or '',
            hardware=d.get('hardware') or '',
            controller_member_status=d.get('controller-member-status') or '',
            ha_primary=d.get('ha-primary') or False,
            lxd_profiles=(
                {k: LxdProfileContents._from_dict(v) for k, v in d['lxd-profiles'].items()}
                if 'lxd-profiles' in d
                else {}
            ),
        )


@dataclasses.dataclass(frozen=True)
class ModelStatus:
    name: str
    type: str
    controller: str
    cloud: str
    version: str

    region: str = ''
    upgrade_available: str = ''
    model_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    meter_status: MeterStatus = dataclasses.field(default_factory=MeterStatus)
    sla: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ModelStatus:
        return cls(
            name=d['name'],
            type=d['type'],
            controller=d['controller'],
            cloud=d['cloud'],
            version=d['version'],
            region=d.get('region') or '',
            upgrade_available=d.get('upgrade-available') or '',
            model_status=(
                StatusInfo._from_dict(d['model-status']) if 'model-status' in d else StatusInfo()
            ),
            meter_status=(
                MeterStatus._from_dict(d['meter-status']) if 'meter-status' in d else MeterStatus()
            ),
            sla=d.get('sla') or '',
        )


@dataclasses.dataclass(frozen=True)
class Status:
    """Parsed version of the status object returned by "juju status --format=json"."""

    model: ModelStatus
    machines: dict[str, MachineStatus]
    apps: dict[str, AppStatus]

    app_endpoints: dict[str, RemoteAppStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    offers: dict[str, OfferStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    storage: CombinedStorage = dataclasses.field(default_factory=CombinedStorage)
    controller: ControllerStatus = dataclasses.field(default_factory=ControllerStatus)
    branches: dict[str, BranchStatus] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Status:
        return cls(
            model=ModelStatus._from_dict(d['model']),
            machines={k: MachineStatus._from_dict(v) for k, v in d['machines'].items()},
            apps={k: AppStatus._from_dict(v) for k, v in d['applications'].items()},
            app_endpoints=(
                {k: RemoteAppStatus._from_dict(v) for k, v in d['application-endpoints'].items()}
                if 'application-endpoints' in d
                else {}
            ),
            offers=(
                {k: OfferStatus._from_dict(v) for k, v in d['offers'].items()}
                if 'offers' in d
                else {}
            ),
            storage=(
                CombinedStorage._from_dict(d['storage']) if 'storage' in d else CombinedStorage()
            ),
            controller=(
                ControllerStatus._from_dict(d['controller'])
                if 'controller' in d
                else ControllerStatus()
            ),
            branches=(
                {k: BranchStatus._from_dict(v) for k, v in d['branches'].items()}
                if 'branches' in d
                else {}
            ),
        )

    def __repr__(self) -> str:
        """Return a pretty-printed version of the status."""
        return _pretty.dump(self)

    def __str__(self) -> str:
        """Return a pretty-printed version of the status."""
        return repr(self)

    def __eq__(self, other: object) -> bool:
        """Report whether two status objects are equivalent.

        This excludes the :attr:`controller` attribute, because that only has a timestamp that
        constantly updates.
        """
        if not isinstance(other, (Status, JubilantStatus)):
            return False
        for field in dataclasses.fields(self):
            if field.name == 'controller':
                continue
            if getattr(self, field.name) != getattr(other, field.name):
                return False
        return True

    def get_units(self, app: str) -> dict[str, UnitStatus]:
        """Get all units of the given *app*, including units of subordinate apps.

        For subordinate apps, this finds and returns the subordinate units using the app's
        ``subordinate_to`` list. For principal (non-subordinate) apps, this is equivalent to
        ``status.apps[app].units``.

        Returns:
            Dict of units where the key is the unit name and the value is the :class:`UnitStatus`.
            If *app* is not found, return an empty dict.
        """
        app_info = self.apps.get(app)
        if app_info is None:
            return {}
        if not app_info.subordinate_to:
            return app_info.units

        units: dict[str, UnitStatus] = {}
        app_prefix = app + '/'
        for principal in app_info.subordinate_to:
            for unit_info in self.apps[principal].units.values():
                for sub_name, sub in unit_info.subordinates.items():
                    if sub_name.startswith(app_prefix):
                        units[sub_name] = sub  # noqa: PERF403
        return units

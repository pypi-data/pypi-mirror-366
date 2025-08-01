# RERO-Invenio-Files
# Copyright (C) 2024 RERO.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Files support for the RERO invenio instances."""

from rero_invenio_files.records.services import FileServiceConfig, RecordServiceConfig

from .permissions import MockPermissionPolicy


class MockRecordServiceConfig(RecordServiceConfig):
    """Mock record service configuration."""

    permission_policy_cls = MockPermissionPolicy


class MockFileServiceConfig(FileServiceConfig):
    """Records files service configuration."""

    permission_policy_cls = MockPermissionPolicy

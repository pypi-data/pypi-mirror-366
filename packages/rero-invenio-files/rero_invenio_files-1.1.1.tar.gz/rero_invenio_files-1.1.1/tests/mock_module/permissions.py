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

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess


class MockPermissionPolicy(RecordPermissionPolicy):
    """."""

    can_search = [AnyUser(), SystemProcess()]
    can_read = [AnyUser(), SystemProcess()]
    can_create = [AnyUser(), SystemProcess()]
    can_update = [AnyUser(), SystemProcess()]
    can_delete = [AnyUser(), SystemProcess()]

    can_get_content_files = [AnyUser(), SystemProcess()]
    can_set_content_files = [AnyUser(), SystemProcess()]

    can_read_files = [AnyUser(), SystemProcess()]
    can_create_files = [AnyUser(), SystemProcess()]
    can_commit_files = [AnyUser(), SystemProcess()]
    can_update_files = [AnyUser(), SystemProcess()]
    can_delete_files = [AnyUser(), SystemProcess()]

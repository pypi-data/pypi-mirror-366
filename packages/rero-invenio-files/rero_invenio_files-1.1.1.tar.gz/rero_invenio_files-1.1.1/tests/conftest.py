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

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_app.factory import create_app as _create_app
from mock_module.services import MockFileServiceConfig, MockRecordServiceConfig

from rero_invenio_files.pdf import PDFGenerator


@pytest.fixture(scope="module")
def simple_data():
    """Return a simple document data for pdf generation."""
    yield {
        "header": "Document pid: 1234",
        "title": "Simple Title",
        "authors": ["Author1, Author2"],
        "summary": """The year 1866 was marked by a bizarre development, an unexplained and downright inexplicable phenomenon that surely no one has forgotten. Without getting into those rumors that upset civilians in the seaports and deranged the public mind even far inland, it must be said that professional seamen were especially alarmed. Traders, shipowners, captains of vessels, skippers, and master mariners from Europe and America, naval officers from every country, and at their heels the various national governments on these two continents, were all extremely disturbed by the business.""",
    }


@pytest.fixture(scope="module")
def pdf_file(simple_data):
    """Return a simple pdf file."""
    pdf = PDFGenerator(simple_data)
    pdf.render()
    return pdf.output()


@pytest.fixture(scope="module")
def headers():
    """Return default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
    }


@pytest.fixture(scope="function")
def input_data():
    """Input data (as coming from the view layer)."""
    return {
        "metadata": {"title": "Test"},
    }


@pytest.yield_fixture(scope="module")
def file_location(database):
    """Create a simple default location for a test.

    Scope: function

    Use this fixture if your test requires a `files location <https://invenio-
    files-rest.readthedocs.io/en/latest/api.html#invenio_files_rest.models.
    Location>`_. The location will be a default location with the name
    ``pytest-location``.
    """
    import shutil
    import tempfile

    from invenio_files_rest.models import Location

    uri = tempfile.mkdtemp()
    location_obj = Location(name="pytest-location", uri=uri, default=True)

    database.session.add(location_obj)
    database.session.commit()

    yield location_obj

    shutil.rmtree(uri)


@pytest.fixture(scope="module")
def app_config(app_config):
    """Application config override."""
    # TODO: Override any necessary config values for tests
    app_config["THEME_FRONTPAGE"] = False
    app_config["RERO_FILES_DEFAULT_VALUE"] = "test-foobar"
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }

    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"
    app_config["RECORDS_REFRESOLVER_CLS"] = "invenio_records.resolver.InvenioRefResolver"
    app_config["RECORDS_REFRESOLVER_STORE"] = "invenio_jsonschemas.proxies.current_refresolver_store"
    app_config["RERO_FILES_RECORD_SERVICE_CONFIG"] = MockRecordServiceConfig
    app_config["RERO_FILES_RECORD_FILE_SERVICE_CONFIG"] = MockFileServiceConfig

    app_config["PREVIEWER_RECORD_FILE_FACOTRY"] = "rero_invenio_files.records.previewer.record_file_factory"

    app_config["RECORDS_UI_ENDPOINTS"] = {
        "recid_preview": {
            "pid_type": "recid",
            "route": "/records/<pid_value>/preview/<path:filename>",
            "view_imp": "rero_invenio_files.records.previewer.preview",
            "record_class": "rero_invenio_files.records.api:RecordWithFile",
        }
    }
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return _create_app

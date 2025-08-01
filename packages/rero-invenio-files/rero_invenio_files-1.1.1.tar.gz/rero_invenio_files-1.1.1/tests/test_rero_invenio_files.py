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

"""Module tests."""

from io import BytesIO
from unittest import mock

from flask import Flask

from rero_invenio_files import REROInvenioFiles


def test_version():
    """Test version import."""
    from rero_invenio_files import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = REROInvenioFiles(app)
    assert "rero-invenio-files" in app.extensions

    app = Flask("testapp")
    ext = REROInvenioFiles()
    assert "rero-invenio-files" not in app.extensions
    ext.init_app(app)
    assert "rero-invenio-files" in app.extensions


def test_files_api_flow(app, client, headers, file_location, pdf_file):
    """Test record creation."""
    # Initialize a draft
    data = {
        "collections": ["col1", "col2"],
        # links=[{"$ref": "https://localhost:5000/api/records/1"}],
        # owner={"$ref": "https://localhost:5000/api/users/1"},
    }
    res = client.post("/api/records", headers=headers, json={"metadata": data})
    assert res.status_code == 201
    id_ = res.json["id"]
    assert res.json["links"]["self"].endswith(f"/api/records/{id_}")
    data["collections"] = ["new col"]
    res = client.put(f"/api/records/{id_}", headers=headers, json={"metadata": data})
    assert res.status_code == 200
    assert res.json["metadata"]["collections"] == ["new col"]

    # Initialize files upload
    res = client.post(
        f"/api/records/{id_}/files",
        headers=headers,
        json=[{"key": "test.pdf", "metadata": {"label": "label1"}}],
    )
    assert res.status_code == 201
    res_file = res.json["entries"][0]
    assert res_file["key"] == "test.pdf"
    assert res_file["status"] == "pending"
    assert res_file["metadata"] == {"label": "label1"}
    assert res_file["links"]["self"].endswith(f"/api/records/{id_}/files/test.pdf")
    assert res_file["links"]["content"].endswith(f"/api/records/{id_}/files/test.pdf/content")
    assert res_file["links"]["commit"].endswith(f"/api/records/{id_}/files/test.pdf/commit")

    # Get the file metadata

    res = client.get(f"/api/records/{id_}/files/test.pdf", headers=headers)
    assert res.status_code == 200
    assert res.json["key"] == "test.pdf"
    assert res.json["status"] == "pending"
    assert res.json["metadata"] == {"label": "label1"}

    # Upload a file
    res = client.put(
        f"/api/records/{id_}/files/test.pdf/content",
        headers={
            "content-type": "application/octet-stream",
            "accept": "application/json",
        },
        data=BytesIO(pdf_file),
    )
    assert res.status_code == 200
    assert res.json["status"] == "pending"

    # Commit the uploaded file
    res = client.post(f"/api/records/{id_}/files/test.pdf/commit", headers=headers)
    assert res.status_code == 200
    assert res.json["status"] == "completed"

    # Get the file metadata
    res = client.get(f"/api/records/{id_}/files/test.pdf", headers=headers)
    assert res.status_code == 200
    assert res.json["key"] == "test.pdf"
    assert res.json["status"] == "completed"
    assert res.json["metadata"] == {"label": "label1"}
    # file_size = str(res.json["size"])
    assert set(res.json["links"].keys()) == {
        "self",
        "content",
        "commit",
        "preview",
        "thumbnail",
    }

    assert isinstance(res.json["size"], int), "File size not integer"

    # Read a file's content
    res = client.get(f"/api/records/{id_}/files/test.pdf/content", headers=headers)
    assert res.status_code == 200
    assert res.data == pdf_file

    res = client.get(f"/api/records/{id_}/files/test-pdf.jpg/content", headers=headers)
    assert res.status_code == 200

    # Test preview
    # Note: url_for works only on the top of the test
    with mock.patch("invenio_theme.views.render_template"):
        res = client.get("/records/foo/preview/test.pdf", headers=headers)
        assert res.status_code == 404
        res = client.get(f"/records/{id_}/preview/test1.pdf", headers=headers)
        assert res.status_code == 404
    with mock.patch("invenio_previewer.extensions.pdfjs.render_template"):
        res = client.get(f"/records/{id_}/preview/test.pdf", headers=headers)
        assert res.status_code == 200

    res = client.get(f"/api/records/{id_}/files/test-pdf.txt/content", headers=headers)
    assert res.status_code == 200
    assert "Title" in res.text

    # Update file metadata
    res = client.put(
        f"/api/records/{id_}/files/test.pdf",
        headers=headers,
        json={"metadata": {"title": "New title"}},
    )
    assert res.status_code == 200
    assert res.json["key"] == "test.pdf"
    assert res.json["status"] == "completed"
    assert res.json["metadata"] == {"title": "New title"}

    # Get all files
    res = client.get(f"/api/records/{id_}/files", headers=headers)
    assert res.status_code == 200
    assert len(res.json["entries"]) == 3
    main_file = next(
        file for file in res.json["entries"] if file.get("metadata", {}).get("type") not in ["thumbnail", "fulltext"]
    )
    assert main_file["key"] == "test.pdf"
    assert main_file["status"] == "completed"
    assert main_file["metadata"] == {"title": "New title"}

    # Delete a file
    res = client.delete(f"/api/records/{id_}/files/test.pdf", headers=headers)
    assert res.status_code == 204

    # Get all files
    res = client.get(f"/api/records/{id_}/files", headers=headers)
    assert res.status_code == 200
    assert len(res.json["entries"]) == 0

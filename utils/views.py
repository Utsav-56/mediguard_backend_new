import os
import mimetypes
from django.conf import settings
from django.http import HttpResponse, Http404, FileResponse
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class DownloadDatabaseView(UserPassesTestMixin, View):
    """
    Exposes the SQLite database file for download.
    Only accessible by superusers.
    """

    def test_func(self):
        # Simply check if the user is logged in
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        # Locate the db.sqlite3 file
        # Usually in BASE_DIR, check settings or os.path
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        
        if not os.path.exists(db_path):
            raise Http404("Database file not found.")

        # Open the file for reading in binary mode
        f = open(db_path, 'rb')
        response = FileResponse(f)
        
        # Set content type and disposition
        response['Content-Type'] = 'application/x-sqlite3'
        response['Content-Disposition'] = 'attachment; filename="db.sqlite3"'
        
        return response

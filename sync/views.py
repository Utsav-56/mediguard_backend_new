from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import SYNC_MAP

class SyncMapView(APIView):
    """
    Returns a 'Sync Map' of all syncable entities for the current user.
    Format: { "entity_name": { "uuid": "updated_at_timestamp", ... }, ... }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sync_map_response = list(SYNC_MAP.keys()) # To keep track of entities
        
        # We'll use a more descriptive structure as requested in guidelines
        # but keep it general enough to cover all entities in SYNC_MAP
        response_data = {}

        for key, (model_class, _) in SYNC_MAP.items():
            # Get only IDs and updated timestamps for performance
            items = model_class.objects.filter(user=user).values('id', 'updated_at')
            
            # Map UUID to its ISO timestamp
            response_data[key] = {
                str(item['id']): item['updated_at'].isoformat().replace("+00:00", "Z")
                for item in items
            }

        return Response(response_data)

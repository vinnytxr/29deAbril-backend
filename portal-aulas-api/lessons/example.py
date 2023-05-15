from django.http import FileResponse, Http404
from django.conf import settings
import os

def serve_video(request, path):
    """
    Returns a specific range of bytes from the video file.
    """
    try:
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        f = open(full_path, "rb")
    except FileNotFoundError:
        raise Http404("Video not found")
    else:
        # Get the byte range specified in the Range header, if present
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        size = os.path.getsize(full_path)
        start, end = 0, size - 1
        if range_match:
            start = int(range_match.group(1))
            if range_match.group(2):
                end = int(range_match.group(2))
        length = end - start + 1

        # Set the Content-Type header and return the requested range
        response = FileResponse(f, content_type='video/mp4', status=206)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
        response['Content-Range'] = f'bytes {start}-{end}/{size}'
        response['Content-Disposition'] = 'inline'
        response['Cache-Control'] = 'no-cache'
        response['Pragma'] = 'no-cache'

        if range_header:
            response['Content-Range'] = 'bytes %d-%d/%d' % (start, end, size)
        else:
            response['Content-Length'] = str(size)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Disposition'] = 'inline'
        return response

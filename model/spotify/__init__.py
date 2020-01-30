def exists(obj, spotify_id):
    return obj.nodes.get_or_none(spotify_id=spotify_id)
def exists(obj, id):
    return obj.nodes.get_or_none(spotify_id=id)
import json, os

def exists(obj, spotify_id):
    return obj.nodes.get_or_none(spotify_id=spotify_id)

def connection_url():
    neo4j_vars = json.load(open(os.path.join('config', 'neo4j.json'), 'r'))
    user = neo4j_vars['user']
    pw = neo4j_vars['pass']
    dns = neo4j_vars['dns']
    port = neo4j_vars['bolt_port']
    return f"bolt://{user}:{pw}@{dns}:{port}"
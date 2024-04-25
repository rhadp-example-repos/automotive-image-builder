def basenames:
    .path | split("/") | last;

def parseURL:
    capture("^((?<scheme>[^:/?#]+):)?(//(?<authority>(?<domain>[^/?#:]*)(:(?<port>[0-9]*))?))?(?<path>[^?#]*)(\\?(?<query>([^#]*)))?(#(?<fragment>(.*)))?");

def splitRPM:
    capture("(?<name>(.*))\\.(?<arch>[a-zA-Z0-9_]+).rpm");

def manifestUrls:
    .sources["org.osbuild.curl"].items | to_entries[] | .value | parseURL;

def urlsToRpms:
    basenames | splitRPM;

def mergeArches:
    reduce .[] as $item ({}; .[$item.arch][$item.name] = true) | with_entries(.value = (.value | keys));

manifestUrls | select(.domain == "mirror.stream.centos.org") | urlsToRpms | .name

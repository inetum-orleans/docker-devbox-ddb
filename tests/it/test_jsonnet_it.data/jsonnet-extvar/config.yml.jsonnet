local pp = std.extVar("docker.port_prefix");
local network = std.extVar("docker.compose.network_name");
local domain_ext = std.extVar("core.domain.ext");
local domain_sub = std.extVar("core.domain.sub");
local tags = std.extVar("tags");
local param1 = std.extVar("param1");

{
    pp: pp,
    network: network,
    domain: domain_ext + "." + domain_sub,
    tags: tags,
    param1: param1
}
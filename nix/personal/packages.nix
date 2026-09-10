{ pkgs, ... }:
{
  environment.systemPackages = [
    pkgs.cloudflared
    pkgs.codex-acp
  ];
}

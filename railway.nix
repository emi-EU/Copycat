{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [ pkgs.ffmpeg pkgs.python3 pkgs.python3Packages.flask ];
}

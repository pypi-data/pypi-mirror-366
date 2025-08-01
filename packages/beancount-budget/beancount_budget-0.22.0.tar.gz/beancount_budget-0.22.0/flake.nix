{
  description = "CLI envelope budget powered by Beancount";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    beanflake = {
      url = "sourcehut:~goorzhel/beancount-flake";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    flake-utils,
    nixpkgs,
    beanflake,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [beanflake.overlays.default];
      };
    in {
      devShells.default = beanflake.lib.${system}.mkShell {
        src = ./.;
        inherit pkgs;
        extraPkgs = with pkgs; [fzf];
        pyPkgs = p:
          with p; [
            beancount
            click
            python-dateutil
            pytest
            pytest-beartype
            pytest-cov
            pytest-datafiles
            types-python-dateutil

            build
            packaging
            packaging-legacy
            twine
          ];
        extraGitHooks = {beancount-black.enable = false;};
      };
    });
}

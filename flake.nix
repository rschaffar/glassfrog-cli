{
  description = "GlassFrog CLI - read-only access to the GlassFrog API";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
          python = pkgs.python313;
        in
        {
          default = self.packages.${system}.glassfrog-cli;

          glassfrog-cli = python.pkgs.buildPythonApplication {
            pname = "glassfrog-cli";
            version = "0.1.0";
            pyproject = true;

            src = ./.;

            build-system = [ python.pkgs.setuptools ];

            dependencies = with python.pkgs; [
              click
              httpx
              rich
              pydantic
              tomli
            ];

            nativeCheckInputs = with python.pkgs; [
              pytest
              respx
            ];

            checkPhase = ''
              runHook preCheck
              pytest tests/
              runHook postCheck
            '';

            meta = {
              description = "CLI tool for read-only access to the GlassFrog API";
              mainProgram = "gf";
            };
          };
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
          python = pkgs.python313;
        in
        {
          default = pkgs.mkShell {
            packages = [
              (python.withPackages (ps: [
                ps.click
                ps.httpx
                ps.rich
                ps.pydantic
                ps.tomli
                ps.pytest
                ps.respx
                ps.ruff
              ]))
              pkgs.ruff
            ];

            shellHook = ''
              export PYTHONPATH="$PWD/src:$PYTHONPATH"
            '';
          };
        }
      );
    };
}

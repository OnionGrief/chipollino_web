let
  common = import ./common.nix { };
  pkgs = common.pkgs;
in
pkgs.mkShell {
  packages = common.runtimePackages ++ (with pkgs; [
    cmake
    gnumake
    gcc
    git
    unzip
    wget
    curl
  ]);

  shellHook = ''
    export PATH="${common.refal5}/bin:$PATH"
    export DJANGO_DEBUG="1"

    if [ ! -f config/config.yaml ]; then
      mkdir -p config
      cp --no-preserve=mode ${common.configSrc}/config.yaml config/config.yaml
      echo "Copied config.yaml from Automatic-Chipollino-Update to config/config.yaml"
    fi

    if [ ! -d Chipollino ]; then
      cp -r ${common.chipollino} Chipollino
      chmod -R u+w Chipollino
      echo "Copied Chipollino to ./Chipollino"
    fi

    export CHIPOLLINO_BINARY="$PWD/Chipollino/build/apps/InterpreterApp/InterpreterApp"
    export CHIPOLLINO_GENERATOR_BINARY="$PWD/Chipollino/build/apps/InputGeneratorApp/InputGeneratorApp"
  '';
}

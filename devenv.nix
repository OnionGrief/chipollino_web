{ pkgs, lib, config, inputs, ... }:

let
  refal5 = pkgs.stdenv.mkDerivation {
    pname = "refal5";
    version = "081222";

    src = inputs.refal5-src;

    nativeBuildInputs = [ pkgs.unzip ];

    buildPhase = ''
      make -f makefile.lin C_FLAGS="-c -DFOR_OS_LINUX -Wall -funsigned-char -std=gnu89"
    '';

    enableParallelBuilding = false;

    installPhase = ''
      mkdir -p $out/bin
      cp refc refgo reftr $out/bin/
    '';
  };

  chipollino = pkgs.stdenv.mkDerivation {
    pname = "chipollino";
    version = "0.1.0";
    src = inputs.chipollino;

    nativeBuildInputs = [
      pkgs.cmake
      pkgs.gnumake
      refal5
    ];

    postPatch = ''
      sed -i \
        -e '/add_subdirectory(apps\/UnitTestsApp)/d' \
        -e '/add_subdirectory(apps\/IntegrationTestsApp)/d' \
        -e '/add_subdirectory(apps\/MetamorphicTestsApp)/d' \
        CMakeLists.txt
    '';

    configurePhase = ''
      cmake -S . -B build \
        -DFETCHCONTENT_SOURCE_DIR_LEXY=${inputs.lexy}
    '';

    buildPhase = ''
      cmake --build build

      pushd refal
      chmod +x compile.sh
      PATH="${refal5}/bin:$PATH" ./compile.sh
      popd
    '';

    installPhase = ''
      mkdir -p $out
      cp -r . $out/
    '';
  };

  pythonEnv = pkgs.python312.withPackages (
    ps: with ps; [
      django
      graphviz
      latex2mathml
      gunicorn
      dot2tex
      pydot
      pyyaml
    ]
  );

  tex = pkgs.texlive.combine {
    inherit (pkgs.texlive)
      scheme-medium
      collection-latexextra
      collection-fontsextra
      collection-mathscience
      collection-langcyrillic
      dvisvgm
      ;
  };

  appSource = pkgs.runCommand "chipollino-web-app" { } ''
    mkdir -p $out/app $out/db
    cp -r ${./accounts} $out/app/accounts
    cp -r ${./chipollino_web} $out/app/chipollino_web
    cp -r ${./converter} $out/app/converter
    cp -r ${./static} $out/app/static
    cp -r ${./templates} $out/app/templates
    cp ${./manage.py} $out/app/manage.py
    cp -r ${chipollino} $out/app/Chipollino
    cp -r ${inputs.chipollino-config} $out/app/config
    chmod -R u+w $out/app $out/db
  '';

  appEntrypoint = pkgs.writeShellScript "chipollino-web-entrypoint" ''
    set -e
    export PATH="${pythonEnv}/bin:${refal5}/bin:/bin"
    export DJANGO_DEBUG="0"
    cd /app
    python manage.py migrate
    python manage.py collectstatic --noinput
    exec gunicorn --bind 0.0.0.0 --timeout 120 chipollino_web.wsgi
  '';

  caddyConfig = pkgs.writeTextDir "etc/caddy/Caddyfile" ''
    :8000 {
      root * /var/www/html
      file_server /static/* browse

      @notStatic {
        not path /static/*
      }

      reverse_proxy @notStatic http://app:8000
    }
  '';

  caddyRoot = pkgs.runCommand "chipollino-web-caddy-root" { } ''
    mkdir -p $out/bin $out/etc/caddy $out/var/www/html/static
    ln -s ${pkgs.caddy}/bin/caddy $out/bin/caddy
    cp ${caddyConfig}/etc/caddy/Caddyfile $out/etc/caddy/Caddyfile
    cp -r ${./static}/. $out/var/www/html/static/
  '';
in
{
  packages = [
    pythonEnv
    pkgs.graphviz
    tex
    refal5
    chipollino

    # dev tools
    pkgs.cmake
    pkgs.gnumake
    pkgs.gcc
    pkgs.git
    pkgs.unzip
    pkgs.wget
    pkgs.curl
  ];

  env = {
    DJANGO_DEBUG = "1";
    CHIPOLLINO_BINARY = "${chipollino}/build/apps/InterpreterApp/InterpreterApp";
    CHIPOLLINO_GENERATOR_BINARY = "${chipollino}/build/apps/InputGeneratorApp/InputGeneratorApp";
  } // lib.optionalAttrs config.container.isBuilding {
    # Marker used by enterShell to skip dev-only setup inside containers.
    DEVENV_CONTAINER_MODE = "1";
  };

  enterShell = ''
    # Skip dev-environment setup when running inside a production container.
    if [ "$DEVENV_CONTAINER_MODE" = "1" ]; then
      return 0
    fi

    export PATH="${refal5}/bin:$PATH"

    if [ ! -f config/config.yaml ]; then
      mkdir -p config
      cp --no-preserve=mode ${inputs.chipollino-config}/config.yaml config/config.yaml
      echo "Copied config.yaml from Automatic-Chipollino-Update to config/config.yaml"
    fi

    if [ ! -d Chipollino ]; then
      cp -r ${chipollino} Chipollino
      chmod -R u+w Chipollino
      echo "Copied Chipollino to ./Chipollino"
    fi
  '';

  tasks = {
    "app:migrate".exec = "python manage.py migrate";
  };

  processes = {
    runserver = {
      exec = "python manage.py runserver";
      after = [ "app:migrate" ];
    };
  };

  containers = {
    app = {
      name = "chipollino-web-app";
      version = "latest";
      workingDir = "/app";
      startupCommand = appEntrypoint;
      copyToRoot = [ ];
      layers = [
        {
          copyToRoot = [
            (pkgs.buildEnv {
              name = "chipollino-web-runtime";
              paths = [
                pythonEnv
                pkgs.graphviz
                tex
                refal5
                chipollino
                pkgs.bash
                pkgs.coreutils
              ];
              ignoreCollisions = true;
            })
          ];
        }
        {
          copyToRoot = [ appSource ];
          perms = [
            {
              path = appSource;
              regex = ".*";
              mode = "0755";
              uid = 1000;
              gid = 1000;
              uname = "user";
              gname = "user";
            }
          ];
        }
      ];
    };

    caddy = {
      name = "chipollino-web-caddy";
      version = "latest";
      startupCommand = "HOME=/tmp ${pkgs.caddy}/bin/caddy run --config /etc/caddy/Caddyfile --adapter caddyfile";
      copyToRoot = [ ];
      layers = [
        {
          copyToRoot = [ caddyRoot ];
        }
      ];
    };
  };
}
